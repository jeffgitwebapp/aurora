"""Porta para um serviço de geração de resposta ancorada em trechos recuperados."""

from typing import Protocol

from aurora_backend.contexts.conversation.services.knowledge.models import KnowledgePassage


class ChatResponseUnavailableError(RuntimeError):
    """Falha técnica, recusa ou resposta reprovada pelo guardrail de saída (falha fechada)."""


class ChatResponseGenerator(Protocol):
    async def generate_reply(
        self,
        message: str,
        passages: tuple[KnowledgePassage, ...],
    ) -> str: ...
