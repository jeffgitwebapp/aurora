"""Busca reformulada pelo LLM (F4): laço limitado, só leitura, sem rede."""

import asyncio
from typing import Any

import pytest

from aurora_backend.contexts.conversation.services.knowledge.models import KnowledgeStatus
from aurora_backend.contexts.conversation.services.knowledge.port import (
    KnowledgeUnavailableError,
)
from aurora_backend.contexts.conversation.services.knowledge_base.agentic_selector import (
    AGENTIC_SELECTION_SCHEMA,
    AGENTIC_SELECTOR_SYSTEM_PROMPT,
    MAX_QUERY_CHARS,
    LanguageModelAgenticChunkSelector,
    SelectionDecision,
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
    ChunkSelectionUnavailableError,
)
from aurora_backend.contexts.conversation.services.knowledge_base.service import (
    EXTRA_SEARCH_CANDIDATES,
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
# Nenhuma palavra em comum com a base: o BM25 não traz candidatos.
COLLOQUIAL = "ele fica atrás de mim o tempo todo"


class FakeAgent:
    """Devolve as decisões na ordem; registra o que recebeu em cada passo."""

    def __init__(self, *decisions: SelectionDecision | Exception):
        self.decisions = list(decisions)
        self.calls: list[dict[str, Any]] = []

    async def decide(
        self,
        message: str,
        candidates: tuple[KnowledgeChunk, ...],
        *,
        can_search: bool,
        previous_queries: tuple[str, ...] = (),
    ) -> SelectionDecision:
        self.calls.append(
            {
                "candidates": tuple(c.id for c in candidates),
                "can_search": can_search,
                "previous_queries": previous_queries,
            }
        )
        decision = self.decisions.pop(0) if len(self.decisions) > 1 else self.decisions[0]
        if isinstance(decision, Exception):
            raise decision
        return decision


def service(agent: FakeAgent, chunks=CHUNKS, **options: Any) -> KnowledgeBaseService:
    snapshot = KnowledgeBaseSnapshot(kb_version="v0.01", source_hash="x", chunks=chunks)
    return KnowledgeBaseService(KnowledgeBaseRepository(snapshot), selector=agent, **options)


def search(query: str) -> SelectionDecision:
    return SelectionDecision(search_query=query)


def pick(*ids: str) -> SelectionDecision:
    return SelectionDecision(relevant_ids=ids)


def test_colloquial_message_without_candidates_is_found_after_reformulated_search() -> None:
    agent = FakeAgent(search("perseguição"), pick("perseguicao#1"))

    result = asyncio.run(service(agent).retrieve(COLLOQUIAL))

    assert result.status is KnowledgeStatus.FOUND
    assert [p.source.id for p in result.passages] == ["perseguicao#1"]
    assert agent.calls[0] == {"candidates": (), "can_search": True, "previous_queries": ()}
    assert agent.calls[1]["candidates"] == ("perseguicao#1",)
    assert agent.calls[1]["previous_queries"] == ("perseguição",)


def test_direct_selection_costs_a_single_call() -> None:
    agent = FakeAgent(pick("intimidade#1"))

    result = asyncio.run(service(agent).retrieve("registro da intimidade"))

    assert [p.source.id for p in result.passages] == ["intimidade#1"]
    assert len(agent.calls) == 1


def test_searches_are_limited_and_last_step_cannot_search() -> None:
    agent = FakeAgent(search("perseguição"), search("medida protetiva"), search("intimidade"))

    result = asyncio.run(service(agent).retrieve(COLLOQUIAL))

    assert len(agent.calls) == 3
    assert [call["can_search"] for call in agent.calls] == [True, True, False]
    assert result.status is KnowledgeStatus.NO_SOURCE


def test_extra_search_limit_is_configurable() -> None:
    agent = FakeAgent(search("perseguição"))

    result = asyncio.run(service(agent, max_extra_searches=0).retrieve(COLLOQUIAL))

    assert agent.calls == []
    assert result.status is KnowledgeStatus.NO_SOURCE


def test_repeated_query_stops_the_loop_without_source() -> None:
    agent = FakeAgent(search("perseguição"), search("perseguição"))

    result = asyncio.run(service(agent).retrieve(COLLOQUIAL))

    assert len(agent.calls) == 2
    assert result.status is KnowledgeStatus.NO_SOURCE


def test_extra_search_adds_only_new_candidates_up_to_the_cap() -> None:
    many = tuple(chunk(f"lei{i}#1", f"perseguição artigo {i}") for i in range(30))
    agent = FakeAgent(search("perseguição"), pick())

    asyncio.run(service(agent, chunks=many).retrieve(COLLOQUIAL))

    assert len(agent.calls[1]["candidates"]) == EXTRA_SEARCH_CANDIDATES


def test_ids_outside_candidates_are_ignored() -> None:
    agent = FakeAgent(pick("inventado#9", "intimidade#1"))

    result = asyncio.run(service(agent).retrieve("registro da intimidade"))

    assert [p.source.id for p in result.passages] == ["intimidade#1"]


def test_agent_failure_is_fail_closed() -> None:
    agent = FakeAgent(search("perseguição"), ChunkSelectionUnavailableError("timeout"))

    with pytest.raises(KnowledgeUnavailableError):
        asyncio.run(service(agent).retrieve(COLLOQUIAL))


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


def decide(
    model: FakeLanguageModel,
    message: str = COLLOQUIAL,
    *,
    can_search: bool = True,
    previous_queries: tuple[str, ...] = (),
) -> SelectionDecision:
    selector = LanguageModelAgenticChunkSelector(model)
    return asyncio.run(
        selector.decide(message, CHUNKS, can_search=can_search, previous_queries=previous_queries)
    )


def test_selector_sends_schema_prompt_and_search_state_through_the_port() -> None:
    model = FakeLanguageModel(
        {"action": "select", "relevant_ids": ["intimidade#1"], "search_query": ""}
    )

    assert decide(model, previous_queries=("perseguição",)) == pick("intimidade#1")
    call = model.calls[0]
    assert call["system"] == AGENTIC_SELECTOR_SYSTEM_PROMPT
    assert call["schema"] == AGENTIC_SELECTION_SCHEMA
    assert "<busca_disponivel>sim</busca_disponivel>" in call["prompt"]
    assert "<busca_feita>perseguição</busca_feita>" in call["prompt"]
    assert COLLOQUIAL in call["prompt"]


def test_search_action_returns_normalized_query() -> None:
    model = FakeLanguageModel(
        {"action": "search", "relevant_ids": [], "search_query": "  perseguição \n reiterada "}
    )

    assert decide(model) == search("perseguição reiterada")


def test_long_query_is_truncated() -> None:
    model = FakeLanguageModel({"action": "search", "relevant_ids": [], "search_query": "x" * 999})

    assert decide(model).search_query == "x" * MAX_QUERY_CHARS


def test_search_when_not_available_becomes_selection() -> None:
    model = FakeLanguageModel(
        {"action": "search", "relevant_ids": ["protetiva#1"], "search_query": "medida"}
    )

    decision = decide(model, can_search=False)

    assert decision == pick("protetiva#1")
    assert "<busca_disponivel>nao</busca_disponivel>" in model.calls[0]["prompt"]


def test_empty_search_query_becomes_selection() -> None:
    model = FakeLanguageModel({"action": "search", "relevant_ids": [], "search_query": "  "})

    assert decide(model) == pick()


@pytest.mark.parametrize(
    "model",
    [
        FakeLanguageModel(error=LanguageModelUnavailableError("timeout")),
        FakeLanguageModel({"action": "outra", "relevant_ids": [], "search_query": ""}),
        FakeLanguageModel({"action": "select", "relevant_ids": "x", "search_query": ""}),
        FakeLanguageModel({"action": "select", "relevant_ids": [1], "search_query": ""}),
        FakeLanguageModel({"action": "search", "relevant_ids": []}),
        FakeLanguageModel(["não é objeto"]),
    ],
)
def test_selector_failures_raise_unavailable(model: FakeLanguageModel) -> None:
    with pytest.raises(ChunkSelectionUnavailableError):
        decide(model)


def test_logs_have_no_message_nor_reformulated_query(caplog: pytest.LogCaptureFixture) -> None:
    secret = "MARCADOR-PRIVADO-123"
    model = FakeLanguageModel(
        {"action": "search", "relevant_ids": [], "search_query": f"{secret} termos"}
    )
    agent = LanguageModelAgenticChunkSelector(model)
    snapshot = KnowledgeBaseSnapshot(kb_version="v0.01", source_hash="x", chunks=CHUNKS)

    with caplog.at_level("INFO"):
        asyncio.run(
            KnowledgeBaseService(KnowledgeBaseRepository(snapshot), selector=agent).retrieve(
                f"{secret} {COLLOQUIAL}"
            )
        )

    logged = " ".join(f"{record.getMessage()} {record.__dict__}" for record in caplog.records)
    assert secret not in logged
    assert "extra_searches" in logged
