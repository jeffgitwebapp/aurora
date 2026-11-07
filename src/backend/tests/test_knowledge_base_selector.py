"""Seleção de trechos pelo LLM entre os candidatos do BM25 (D-12/D-13), sem rede."""

import asyncio
from typing import Any

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
    SELECTION_SCHEMA,
    SELECTOR_SYSTEM_PROMPT,
    ChunkSelectionUnavailableError,
    LanguageModelChunkSelector,
)
from aurora_backend.contexts.conversation.services.knowledge_base.service import (
    KnowledgeBaseService,
)
from aurora_backend.contexts.conversation.services.language_model.port import (
    LanguageModelResult,
    LanguageModelUnavailableError,
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


class FakeLanguageModel:
    provider = "fake"
    model = "fake-model"

    def __init__(self, data: Any = None, error: Exception | None = None):
        self.data = data
        self.error = error
        self.calls: list[dict[str, Any]] = []

    async def generate_json(self, **kwargs: Any) -> LanguageModelResult:
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return LanguageModelResult(data=self.data, provider=self.provider, model=self.model)


def select(
    language_model: FakeLanguageModel,
    message: str = "ele me filmou",
    candidates: tuple[KnowledgeChunk, ...] = CHUNKS,
) -> tuple[str, ...]:
    return asyncio.run(LanguageModelChunkSelector(language_model).select(message, candidates))


def test_selector_sends_candidates_and_message_through_the_port() -> None:
    model = FakeLanguageModel({"relevant_ids": ["intimidade#1", "x#1", "intimidade#1"]})

    assert select(model) == ("intimidade#1",)
    call = model.calls[0]
    assert call["system"] == SELECTOR_SYSTEM_PROMPT
    assert call["schema"] == SELECTION_SCHEMA
    assert '<trecho id="intimidade#1">' in call["prompt"]
    assert "ele me filmou" in call["prompt"]


def test_selector_limits_to_five_ids() -> None:
    many = tuple(chunk(f"c{i}#1", f"texto {i}") for i in range(8))

    assert len(select(FakeLanguageModel({"relevant_ids": [c.id for c in many]}), "t", many)) == 5


@pytest.mark.parametrize(
    "model",
    [
        FakeLanguageModel(error=LanguageModelUnavailableError("timeout")),
        FakeLanguageModel({"outra_chave": []}),
        FakeLanguageModel({"relevant_ids": "intimidade#1"}),
        FakeLanguageModel({"relevant_ids": [1, 2]}),
    ],
)
def test_selector_failures_raise_unavailable(model: FakeLanguageModel) -> None:
    with pytest.raises(ChunkSelectionUnavailableError):
        select(model)


def test_selector_logs_only_metadata(caplog: pytest.LogCaptureFixture) -> None:
    secret = "MARCADOR-PRIVADO-123"

    with caplog.at_level("INFO"):
        select(FakeLanguageModel({"relevant_ids": ["intimidade#1"]}), f"{secret} ele me filmou")

    logged = " ".join(f"{record.getMessage()} {record.__dict__}" for record in caplog.records)
    assert secret not in logged
    assert "registro não autorizado" not in logged
