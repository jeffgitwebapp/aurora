"""Seleção de trechos pelo Claude entre os candidatos do BM25 (D-12), sem rede."""

import asyncio
import json
from types import SimpleNamespace
from typing import Any

import anthropic
import httpx2
import pytest

from aurora_backend.contexts.conversation.services.knowledge.models import KnowledgeStatus
from aurora_backend.contexts.conversation.services.knowledge.port import (
    KnowledgeUnavailableError,
)
from aurora_backend.contexts.conversation.services.knowledge_base.models import (
    CitableKind,
    KnowledgeBaseSnapshot,
    KnowledgeChunk,
    ReviewStatus,
)
from aurora_backend.contexts.conversation.services.knowledge_base.repository import (
    KnowledgeBaseRepository,
)
from aurora_backend.contexts.conversation.services.knowledge_base.selector import (
    FALLBACK_BETA,
    ChunkSelectionUnavailableError,
    ClaudeChunkSelector,
)
from aurora_backend.contexts.conversation.services.knowledge_base.service import (
    KnowledgeBaseService,
)


def chunk(chunk_id: str, text: str) -> KnowledgeChunk:
    return KnowledgeChunk(
        id=chunk_id,
        doc_id=chunk_id.split("#")[0],
        kind="legislacao",
        title=f"Título {chunk_id}",
        section="seção",
        locator=f"localizador {chunk_id}",
        citable_text=text,
        citable_kind=CitableKind.OFFICIAL_TEXT,
        plain_summary=None,
        scope_notes=(),
        topics=("tema",),
        test_questions=(),
        url="https://exemplo.gov.br",
        version=None,
        publisher="Órgão",
        status=ReviewStatus.PENDING,
        internal=False,
    )


CHUNKS = (
    chunk("perseguicao#1", "perseguição reiterada por qualquer meio"),
    chunk("intimidade#1", "registro não autorizado da intimidade sexual"),
    chunk("protetiva#1", "medida protetiva de urgência"),
)


class FakeSelector:
    def __init__(self, result: tuple[str, ...] | Exception):
        self.result = result
        self.calls: list[tuple[str, tuple[str, ...]]] = []

    async def select(self, message: str, candidates: tuple[KnowledgeChunk, ...]) -> tuple[str, ...]:
        self.calls.append((message, tuple(c.id for c in candidates)))
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


def service(selector: FakeSelector, **options: Any) -> KnowledgeBaseService:
    snapshot = KnowledgeBaseSnapshot(kb_version="v0.01", source_hash="x", chunks=CHUNKS)
    return KnowledgeBaseService(KnowledgeBaseRepository(snapshot), selector=selector, **options)


def test_selector_receives_bm25_candidates_and_its_choice_defines_the_passages() -> None:
    selector = FakeSelector(("intimidade#1",))

    result = asyncio.run(service(selector).retrieve("registro da perseguição"))

    assert selector.calls[0][1][0] in {"perseguicao#1", "intimidade#1"}
    assert set(selector.calls[0][1]) == {"perseguicao#1", "intimidade#1"}
    assert result.status is KnowledgeStatus.FOUND
    assert [p.source.id for p in result.passages] == ["intimidade#1"]


def test_no_bm25_candidate_returns_no_source_without_calling_selector() -> None:
    selector = FakeSelector(("perseguicao#1",))

    result = asyncio.run(service(selector).retrieve("receita de bolo"))

    assert result.status is KnowledgeStatus.NO_SOURCE
    assert selector.calls == []


def test_empty_selection_returns_no_source() -> None:
    result = asyncio.run(service(FakeSelector(())).retrieve("perseguição"))

    assert result.status is KnowledgeStatus.NO_SOURCE


def test_ids_outside_candidates_are_ignored() -> None:
    result = asyncio.run(
        service(FakeSelector(("inventado#9", "perseguicao#1"))).retrieve("perseguição")
    )

    assert [p.source.id for p in result.passages] == ["perseguicao#1"]


def test_candidate_limit_is_respected() -> None:
    selector = FakeSelector(())

    asyncio.run(service(selector, candidates=1).retrieve("registro da perseguição"))

    assert len(selector.calls[0][1]) == 1


def test_selector_failure_is_fail_closed_as_knowledge_unavailable() -> None:
    selector = FakeSelector(ChunkSelectionUnavailableError("timeout"))

    with pytest.raises(KnowledgeUnavailableError):
        asyncio.run(service(selector).retrieve("perseguição"))


class FakeMessages:
    def __init__(self, response: Any = None, error: Exception | None = None):
        self.response = response
        self.error = error
        self.kwargs: dict[str, Any] = {}

    async def create(self, **kwargs: Any) -> Any:
        self.kwargs = kwargs
        if self.error is not None:
            raise self.error
        return self.response


class FakeClient:
    def __init__(self, messages: FakeMessages):
        self.beta = SimpleNamespace(messages=messages)
        self.options: dict[str, Any] = {}

    def with_options(self, **options: Any) -> "FakeClient":
        self.options = options
        return self


def response(text: str, stop_reason: str = "end_turn") -> SimpleNamespace:
    return SimpleNamespace(
        stop_reason=stop_reason,
        model="claude-opus-5-5",
        content=[SimpleNamespace(type="thinking"), SimpleNamespace(type="text", text=text)],
        usage=SimpleNamespace(input_tokens=100, output_tokens=10),
    )


def select(messages: FakeMessages, message: str = "ele me filmou") -> tuple[str, ...]:
    client = FakeClient(messages)
    selector = ClaudeChunkSelector(client, model="claude-opus-5-5")  # type: ignore[arg-type]
    return asyncio.run(selector.select(message, CHUNKS))


def test_claude_selector_builds_request_and_filters_ids() -> None:
    messages = FakeMessages(
        response(json.dumps({"relevant_ids": ["intimidade#1", "x#1", "intimidade#1"]}))
    )

    selected = select(messages)

    assert selected == ("intimidade#1",)
    kwargs = messages.kwargs
    assert kwargs["model"] == "claude-opus-5-5"
    assert kwargs["output_config"]["effort"] == "low"
    assert kwargs["output_config"]["format"]["type"] == "json_schema"
    assert kwargs["betas"] == [FALLBACK_BETA]
    assert kwargs["fallbacks"] == "default"
    assert kwargs["system"][0]["cache_control"] == {"type": "ephemeral"}
    user_content = kwargs["messages"][0]["content"]
    assert '<trecho id="intimidade#1">' in user_content
    assert "ele me filmou" in user_content


def test_claude_selector_limits_to_five_ids() -> None:
    many = tuple(chunk(f"c{i}#1", f"texto {i}") for i in range(8))
    messages = FakeMessages(response(json.dumps({"relevant_ids": [c.id for c in many]})))
    client = FakeClient(messages)
    selector = ClaudeChunkSelector(client, model="m")  # type: ignore[arg-type]

    assert len(asyncio.run(selector.select("texto", many))) == 5


@pytest.mark.parametrize(
    "fake",
    [
        FakeMessages(response("{}", stop_reason="refusal")),
        FakeMessages(response("{}", stop_reason="max_tokens")),
        FakeMessages(response("não é json")),
        FakeMessages(response(json.dumps({"outra_chave": []}))),
        FakeMessages(
            error=anthropic.APIConnectionError(
                request=httpx2.Request("POST", "https://api.anthropic.com")
            )
        ),
        FakeMessages(
            error=anthropic.APITimeoutError(
                request=httpx2.Request("POST", "https://api.anthropic.com")
            )
        ),
    ],
)
def test_claude_selector_failures_raise_unavailable(fake: FakeMessages) -> None:
    with pytest.raises(ChunkSelectionUnavailableError):
        select(fake)


def test_claude_selector_logs_only_metadata(caplog: pytest.LogCaptureFixture) -> None:
    secret = "MARCADOR-PRIVADO-123"
    messages = FakeMessages(response(json.dumps({"relevant_ids": ["intimidade#1"]})))

    with caplog.at_level("INFO"):
        select(messages, message=f"{secret} ele me filmou")

    logged = " ".join(f"{record.getMessage()} {record.__dict__}" for record in caplog.records)
    assert secret not in logged
    assert "registro não autorizado" not in logged
