"""Porta, resultados e serviço de recuperação de conhecimento com fontes."""

from aurora_backend.contexts.conversation.services.knowledge.models import (
    KnowledgePassage,
    KnowledgeResult,
    KnowledgeStatus,
    SourceReference,
)
from aurora_backend.contexts.conversation.services.knowledge.port import (
    KnowledgeRetriever,
    KnowledgeUnavailableError,
)
from aurora_backend.contexts.conversation.services.knowledge.service import KnowledgeService

__all__ = [
    "KnowledgePassage",
    "KnowledgeResult",
    "KnowledgeRetriever",
    "KnowledgeService",
    "KnowledgeStatus",
    "KnowledgeUnavailableError",
    "SourceReference",
]
