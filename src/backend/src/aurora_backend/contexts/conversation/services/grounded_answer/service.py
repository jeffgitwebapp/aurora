"""Redação da resposta pelo LLM, ancorada nos trechos recuperados (porta ChatResponseGenerator).

O LLM devolve segmentos com os ids das fontes; o serviço converte os ids em marcadores
[n] na ordem de `sources` (U-03), passa a resposta pelo guardrail de saída e registra
só metadados. Falha do LLM ou reprovação do guardrail → ChatResponseUnavailableError (503).
"""

import hashlib
import time
from pathlib import Path
from typing import Any

from aurora_backend.contexts.conversation.services.answer_guardrail.service import (
    AnswerGuardrailService,
    AnswerSegment,
)
from aurora_backend.contexts.conversation.services.chat_response.port import (
    ChatResponseUnavailableError,
)
from aurora_backend.contexts.conversation.services.decision_trace.service import (
    DecisionTraceService,
)
from aurora_backend.contexts.conversation.services.knowledge.models import KnowledgePassage
from aurora_backend.contexts.conversation.services.knowledge_base.repository import (
    KnowledgeBaseRepository,
)
from aurora_backend.contexts.conversation.services.language_model.port import (
    LanguageModel,
    LanguageModelUnavailableError,
)

PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "system_v1_2.md"
MAX_OUTPUT_TOKENS = 4096
MAX_SEGMENTS = 6
SUMMARY_LABEL = "Resumo em linguagem simples (apoio, não citar como lei)"

ANSWER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "segments": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "source_ids": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["text", "source_ids"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["segments"],
    "additionalProperties": False,
}


def load_system_prompt(path: Path = PROMPT_PATH) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").strip()
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    return text, f"{path.stem}@{digest}"


class GroundedAnswerService:
    def __init__(
        self,
        language_model: LanguageModel,
        repository: KnowledgeBaseRepository,
        guardrail: AnswerGuardrailService,
        *,
        trace: DecisionTraceService | None = None,
        max_output_tokens: int = MAX_OUTPUT_TOKENS,
    ):
        self._language_model = language_model
        self._repository = repository
        self._guardrail = guardrail
        self._trace = trace or DecisionTraceService()
        self._max_output_tokens = max_output_tokens
        self._system_prompt, self.prompt_version = load_system_prompt()

    async def generate_reply(
        self,
        message: str,
        passages: tuple[KnowledgePassage, ...],
    ) -> str:
        if not passages:
            raise ValueError("A resposta exige ao menos um trecho de fonte.")
        numbers: dict[str, int] = {}
        for passage in passages:
            numbers.setdefault(passage.source.id, len(numbers) + 1)
        metadata: dict[str, Any] = {
            "kb_version": self._repository.kb_version,
            "prompt_version": self.prompt_version,
            "source_ids": list(numbers),
        }
        started = time.perf_counter()
        try:
            result = await self._language_model.generate_json(
                system=self._system_prompt,
                prompt=self._prompt(message, passages),
                schema=ANSWER_SCHEMA,
                max_output_tokens=self._max_output_tokens,
            )
        except LanguageModelUnavailableError as exc:
            self._trace.record(
                "grounded_answer", outcome="llm_unavailable", error=str(exc), **metadata
            )
            raise ChatResponseUnavailableError("Geração indisponível.") from exc

        metadata.update(
            provider=result.provider,
            model=result.model,
            input_tokens=result.usage.input_tokens,
            output_tokens=result.usage.output_tokens,
            cached_input_tokens=result.usage.cached_input_tokens,
            duration_ms=round((time.perf_counter() - started) * 1000),
        )
        segments = self._segments(result.data)
        check = self._guardrail.check(
            segments,
            allowed_source_ids=frozenset(numbers),
            allowed_urls=frozenset(passage.source.url for passage in passages),
        )
        metadata.update(
            guardrail_version=check.version,
            segments=len(segments),
            cited_source_ids=sorted({i for s in segments for i in s.source_ids}),
        )
        if not check.passed:
            self._trace.record(
                "grounded_answer",
                outcome="blocked",
                guardrail_violations=list(check.violations),
                **metadata,
            )
            raise ChatResponseUnavailableError("Resposta reprovada pelo guardrail de saída.")

        self._trace.record("grounded_answer", outcome="informational", **metadata)
        return "\n\n".join(self._render(segment, numbers) for segment in segments)

    def _prompt(self, message: str, passages: tuple[KnowledgePassage, ...]) -> str:
        blocks = []
        for passage in passages:
            chunk = self._repository.get(passage.source.id)
            lines = [
                f'<trecho id="{passage.source.id}">',
                f"Fonte: {passage.source.title} — {passage.source.locator}",
                f"Texto: {passage.text}",
            ]
            if chunk is not None and chunk.plain_summary and chunk.plain_summary != passage.text:
                lines.append(f"{SUMMARY_LABEL}: {chunk.plain_summary}")
            if chunk is not None:
                lines.extend(f"Atenção: {note}" for note in chunk.scope_notes)
            lines.append("</trecho>")
            blocks.append("\n".join(lines))
        return (
            "<trechos>\n"
            + "\n".join(blocks)
            + "\n</trechos>\n\n<mensagem_da_usuaria>\n"
            + message
            + "\n</mensagem_da_usuaria>"
        )

    @staticmethod
    def _segments(data: dict[str, Any]) -> tuple[AnswerSegment, ...]:
        raw = data.get("segments")
        if not isinstance(raw, list):
            raise ChatResponseUnavailableError("Resposta fora do schema.")
        segments = []
        for item in raw[:MAX_SEGMENTS]:
            if (
                not isinstance(item, dict)
                or not isinstance(item.get("text"), str)
                or not isinstance(item.get("source_ids"), list)
                or not all(isinstance(i, str) for i in item["source_ids"])
            ):
                raise ChatResponseUnavailableError("Resposta fora do schema.")
            text = item["text"].strip()
            if text:
                segments.append(
                    AnswerSegment(text=text, source_ids=tuple(dict.fromkeys(item["source_ids"])))
                )
        return tuple(segments)

    @staticmethod
    def _render(segment: AnswerSegment, numbers: dict[str, int]) -> str:
        markers = "".join(f"[{numbers[i]}]" for i in segment.source_ids if i in numbers)
        return f"{segment.text} {markers}".rstrip()
