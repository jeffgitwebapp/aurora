"""Porta para um serviço substituível de limite de escopo."""

from typing import Protocol

from aurora_backend.contexts.conversation.services.guardrail.models import GuardrailResult


class GuardrailUnavailableError(RuntimeError):
    """Falha técnica do guardrail; a conversa falha fechada, sem gerar resposta."""


class ScopeGuardrail(Protocol):
    async def check_request(self, message: str) -> GuardrailResult: ...
