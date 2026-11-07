"""Normalização pt-BR (D-03) e recuperação BM25 da base curada."""

import asyncio

import pytest

from aurora_backend.contexts.conversation.services.knowledge.models import KnowledgeStatus
from aurora_backend.contexts.conversation.services.knowledge_base.models import (
    CitableKind,
    KnowledgeBaseSnapshot,
    KnowledgeChunk,
    ReviewStatus,
)
from aurora_backend.contexts.conversation.services.knowledge_base.repository import (
    KnowledgeBaseRepository,
)
from aurora_backend.contexts.conversation.services.knowledge_base.search import tokenize
from aurora_backend.contexts.conversation.services.knowledge_base.service import (
    CURATED_SUMMARY_LABEL,
    KnowledgeBaseService,
)


def chunk(chunk_id: str, text: str, **overrides: object) -> KnowledgeChunk:
    values: dict[str, object] = {
        "id": chunk_id,
        "doc_id": chunk_id.split("#")[0],
        "kind": "legislacao",
        "title": f"Título {chunk_id}",
        "section": "",
        "locator": f"localizador {chunk_id}",
        "citable_text": text,
        "citable_kind": CitableKind.OFFICIAL_TEXT,
        "plain_summary": None,
        "scope_notes": (),
        "topics": (),
        "test_questions": ("pergunta que não deve ser indexada zebra",),
        "url": "https://exemplo.gov.br",
        "version": None,
        "publisher": "Órgão",
        "status": ReviewStatus.PENDING,
        "internal": False,
    }
    values.update(overrides)
    return KnowledgeChunk(**values)  # type: ignore[arg-type]


def service_for(*chunks: KnowledgeChunk, **options: object) -> KnowledgeBaseService:
    snapshot = KnowledgeBaseSnapshot(kb_version="v0.01", source_hash="x", chunks=chunks)
    return KnowledgeBaseService(KnowledgeBaseRepository(snapshot), **options)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "variant",
    [
        "Violência psicológica é crime?",
        "violencia psicologica e crime",
        "VIOLÊNCIA PSICOLÓGICA É CRIME?",
        "VIOLENCIA PSICOLOGICA E CRIME",
        "ViOlÊnCiA   psicológica,é crime!!",
    ],
)
def test_tokenize_ignores_accents_case_and_punctuation(variant: str) -> None:
    assert tokenize(variant) == ["violencia", "psicologica", "crime"]


def test_tokenize_splits_legal_references_and_reduces_plurals() -> None:
    assert tokenize("art. 147-B das Leis") == ["art", "147", "b", "lei"]
    assert tokenize("ameaças e humilhações") == ["ameaca", "humilhacao"]


def test_real_base_returns_same_chunks_for_accent_and_case_variants() -> None:
    service = KnowledgeBaseService(KnowledgeBaseRepository.from_file(), score_threshold=0)
    variants = (
        "Violência psicológica é crime?",
        "violencia psicologica e crime",
        "VIOLENCIA PSICOLOGICA É CRIME",
    )

    rankings = [[(c.id, round(s, 9)) for c, s in service.rank(v)[:5]] for v in variants]

    assert rankings[0] == rankings[1] == rankings[2]
    assert "cp-art147b#caput" in [chunk_id for chunk_id, _ in rankings[0]]


def test_retrieve_returns_ranked_passages_with_source_metadata() -> None:
    service = service_for(
        chunk("a#1", "perseguição reiterada da vítima"),
        chunk("b#1", "medida protetiva de urgência"),
        score_threshold=0.1,
    )

    result = asyncio.run(service.retrieve("O que é perseguição?"))

    assert result.status is KnowledgeStatus.FOUND
    assert [passage.source.id for passage in result.passages] == ["a#1"]
    assert result.passages[0].text == "perseguição reiterada da vítima"
    assert result.passages[0].source.url == "https://exemplo.gov.br"
    assert result.demo is True


def test_retrieve_below_threshold_returns_no_source() -> None:
    service = service_for(chunk("a#1", "perseguição reiterada"), score_threshold=0.1)

    result = asyncio.run(service.retrieve("receita de bolo de cenoura"))

    assert result.status is KnowledgeStatus.NO_SOURCE
    assert result.passages == ()


def test_test_questions_are_not_indexed() -> None:
    service = service_for(chunk("a#1", "perseguição reiterada"), score_threshold=0.0001)

    assert asyncio.run(service.retrieve("zebra")).status is KnowledgeStatus.NO_SOURCE


def test_curated_summary_is_labeled_in_locator() -> None:
    service = service_for(
        chunk("g#1", "resumo sobre o ciclo", citable_kind=CitableKind.CURATED_SUMMARY),
        score_threshold=0.1,
    )

    passage = asyncio.run(service.retrieve("ciclo")).passages[0]

    assert passage.source.locator.endswith(f"({CURATED_SUMMARY_LABEL})")


def test_internal_and_unapproved_chunks_respect_filters() -> None:
    internal = chunk("i#1", "ciclo interno", internal=True)
    approved = chunk("p#1", "ciclo aprovado", status=ReviewStatus.APPROVED)
    pending = chunk("q#1", "ciclo pendente")

    ids = {
        passage.source.id
        for passage in asyncio.run(
            service_for(internal, approved, pending, score_threshold=0.01).retrieve("ciclo")
        ).passages
    }
    strict = asyncio.run(
        service_for(
            internal, approved, pending, score_threshold=0.01, allow_pending=False
        ).retrieve("ciclo")
    )

    assert ids == {"p#1", "q#1"}
    assert [passage.source.id for passage in strict.passages] == ["p#1"]
    assert strict.demo is False


def test_top_k_limits_passages() -> None:
    chunks = [chunk(f"c{i}#1", f"ciclo da violência variação {i}") for i in range(8)]

    result = asyncio.run(service_for(*chunks, top_k=3, score_threshold=0.01).retrieve("ciclo"))

    assert len(result.passages) == 3
