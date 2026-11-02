"""Porta, resultados e serviço de limite de escopo da conversa."""

from aurora_backend.contexts.conversation.services.guardrail.models import (
    GuardrailResult,
    OutOfScopeCategory,
    ScopeDecision,
)
from aurora_backend.contexts.conversation.services.guardrail.port import (
    GuardrailUnavailableError,
    ScopeGuardrail,
)
from aurora_backend.contexts.conversation.services.guardrail.service import GuardrailService

__all__ = [
    "GuardrailResult",
    "GuardrailService",
    "GuardrailUnavailableError",
    "OutOfScopeCategory",
    "ScopeDecision",
    "ScopeGuardrail",
]
