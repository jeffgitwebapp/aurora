"""Base de conhecimento curada (v1.2): versão vigente, snapshot e busca BM25."""

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
    ChunkSelector,
    LanguageModelChunkSelector,
)
from aurora_backend.contexts.conversation.services.knowledge_base.service import (
    KnowledgeBaseService,
)

__all__ = [
    "ChunkSelectionUnavailableError",
    "ChunkSelector",
    "CitableKind",
    "LanguageModelChunkSelector",
    "KnowledgeBaseRepository",
    "KnowledgeBaseService",
    "KnowledgeBaseSnapshot",
    "KnowledgeChunk",
    "ReviewStatus",
]
