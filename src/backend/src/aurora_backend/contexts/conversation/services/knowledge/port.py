"""Porta para um serviço substituível de recuperação de conhecimento."""

from typing import Protocol

from aurora_backend.contexts.conversation.services.knowledge.models import KnowledgeResult


class KnowledgeUnavailableError(RuntimeError):
    """Falha técnica da recuperação; distinta de ausência de fonte."""


class KnowledgeRetriever(Protocol):
    async def retrieve(self, message: str) -> KnowledgeResult: ...
