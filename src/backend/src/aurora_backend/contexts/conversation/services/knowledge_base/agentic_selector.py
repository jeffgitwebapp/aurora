"""Seleção com busca reformulada (F4): o LLM escolhe trechos ou pede uma nova busca.

A "ferramenta" de busca é uma ação no JSON da porta LanguageModel, não o tool calling
nativo de um provedor, para que Gemini e Claude continuem trocáveis pelo ambiente.
Quem executa a busca é o KnowledgeBaseService (BM25 na base vigente, só leitura); o
LLM só propõe os termos. O número de buscas extras é limitado pelo serviço.
"""

import logging
import time
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from aurora_backend.contexts.conversation.services.knowledge_base.models import KnowledgeChunk
from aurora_backend.contexts.conversation.services.knowledge_base.selector import (
    MAX_OUTPUT_TOKENS,
    MAX_SELECTED,
    SELECTOR_SYSTEM_PROMPT,
    ChunkSelectionUnavailableError,
    candidate_block,
)
from aurora_backend.contexts.conversation.services.language_model.port import (
    LanguageModel,
    LanguageModelUnavailableError,
)

logger = logging.getLogger(__name__)

MAX_QUERY_CHARS = 200

AGENTIC_SELECTOR_SYSTEM_PROMPT = (
    SELECTOR_SYSTEM_PROMPT
    + """
Busca reformulada:
- Se os candidatos não bastam porque a usuária usou palavras do dia a dia, você pode pedir \
uma nova busca na base com action "search" e, em search_query, poucos termos técnicos \
equivalentes (por exemplo: "ele controla tudo" → "controle coercitivo isolamento \
vigilância"). Os resultados serão somados aos candidatos.
- Só peça busca se ela puder trazer trechos melhores; com candidatos suficientes, use \
action "select". Quando <busca_disponivel> for "nao", use sempre action "select".
- Com action "select", search_query fica vazio; com action "search", relevant_ids fica vazio.
- A busca é só na base do Aurora; nunca use search_query para outra finalidade.
"""
)

AGENTIC_SELECTION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": ["select", "search"]},
        "relevant_ids": {"type": "array", "items": {"type": "string"}},
        "search_query": {"type": "string"},
    },
    "required": ["action", "relevant_ids", "search_query"],
    "additionalProperties": False,
}


@dataclass(frozen=True)
class SelectionDecision:
    """Ids escolhidos ou, se search_query não for None, pedido de nova busca."""

    relevant_ids: tuple[str, ...] = ()
    search_query: str | None = None


@runtime_checkable
class AgenticChunkSelector(Protocol):
    async def decide(
        self,
        message: str,
        candidates: tuple[KnowledgeChunk, ...],
        *,
        can_search: bool,
        previous_queries: tuple[str, ...] = (),
    ) -> SelectionDecision: ...


class LanguageModelAgenticChunkSelector:
    """Seletor da F4 sobre a porta LanguageModel; ids estranhos são descartados."""

    def __init__(
        self, language_model: LanguageModel, *, max_output_tokens: int = MAX_OUTPUT_TOKENS
    ):
        self._language_model = language_model
        self._max_output_tokens = max_output_tokens

    async def decide(
        self,
        message: str,
        candidates: tuple[KnowledgeChunk, ...],
        *,
        can_search: bool,
        previous_queries: tuple[str, ...] = (),
    ) -> SelectionDecision:
        candidate_ids = {chunk.id for chunk in candidates}
        searches = "".join(f"<busca_feita>{query}</busca_feita>\n" for query in previous_queries)
        prompt = (
            "<trechos_candidatos>\n"
            + "\n".join(candidate_block(chunk) for chunk in candidates)
            + "\n</trechos_candidatos>\n\n"
            + searches
            + f"<busca_disponivel>{'sim' if can_search else 'nao'}</busca_disponivel>\n\n"
            + "<mensagem_da_usuaria>\n"
            + message
            + "\n</mensagem_da_usuaria>"
        )
        started = time.perf_counter()
        try:
            result = await self._language_model.generate_json(
                system=AGENTIC_SELECTOR_SYSTEM_PROMPT,
                prompt=prompt,
                schema=AGENTIC_SELECTION_SCHEMA,
                max_output_tokens=self._max_output_tokens,
            )
        except LanguageModelUnavailableError as exc:
            raise ChunkSelectionUnavailableError(str(exc)) from exc

        data = result.data if isinstance(result.data, dict) else {}
        action = data.get("action")
        raw_ids = data.get("relevant_ids")
        query = data.get("search_query")
        if (
            action not in ("select", "search")
            or not isinstance(raw_ids, list)
            or not all(isinstance(i, str) for i in raw_ids)
            or not isinstance(query, str)
        ):
            raise ChunkSelectionUnavailableError("resposta fora do schema")

        query = " ".join(query.split())[:MAX_QUERY_CHARS]
        selected = tuple(dict.fromkeys(i for i in raw_ids if i in candidate_ids))[:MAX_SELECTED]
        wants_search = action == "search" and can_search and query != ""
        logger.info(
            "knowledge_base.agentic_selection",
            extra={
                "provider": result.provider,
                "model": result.model,
                "candidates": len(candidates),
                "action": "search" if wants_search else "select",
                "selected": 0 if wants_search else len(selected),
                "discarded_ids": len(raw_ids) - len(selected),
                "input_tokens": result.usage.input_tokens,
                "output_tokens": result.usage.output_tokens,
                "duration_ms": round((time.perf_counter() - started) * 1000),
            },
        )
        if wants_search:
            return SelectionDecision(search_query=query)
        return SelectionDecision(relevant_ids=selected)
