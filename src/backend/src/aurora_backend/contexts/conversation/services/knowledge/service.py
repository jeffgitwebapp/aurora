"""Serviço de conhecimento com trechos estáticos de fontes oficiais no protótipo."""

from aurora_backend.contexts.conversation.services.knowledge.models import (
    KnowledgePassage,
    KnowledgeResult,
    KnowledgeStatus,
    SourceReference,
)
from aurora_backend.shared.fixture_text import (
    normalize_fixture_sentence,
)
from aurora_backend.shared.legal_sources import (
    CODIGO_PENAL_ART_147_B,
    MARIA_DA_PENHA_ART_7_II,
    LegalExcerpt,
)


def _passage(excerpt: LegalExcerpt) -> KnowledgePassage:
    return KnowledgePassage(
        text=excerpt.text,
        source=SourceReference(
            id=excerpt.id,
            title=excerpt.title,
            locator=excerpt.locator,
            publisher=excerpt.publisher,
            url=excerpt.url,
            version=excerpt.version,
        ),
    )


_KNOWLEDGE_FIXTURES: dict[str, tuple[KnowledgePassage, ...]] = {
    "O que é violência psicológica?": (_passage(MARIA_DA_PENHA_ART_7_II),),
    "Violência psicológica é crime?": (_passage(CODIGO_PENAL_ART_147_B),),
}

_NORMALIZED_KNOWLEDGE_FIXTURES = {
    normalize_fixture_sentence(question): passages
    for question, passages in _KNOWLEDGE_FIXTURES.items()
}


class KnowledgeService:
    """Recupera trechos das fixtures estáticas atuais; não é busca RAG real."""

    async def retrieve(self, message: str) -> KnowledgeResult:
        passages = _NORMALIZED_KNOWLEDGE_FIXTURES.get(normalize_fixture_sentence(message))
        if passages is None:
            return KnowledgeResult(status=KnowledgeStatus.NO_SOURCE)
        return KnowledgeResult(status=KnowledgeStatus.FOUND, passages=passages)
