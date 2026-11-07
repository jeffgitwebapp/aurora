"""Porta de LLM independente de provedor (D-13) e fábrica por ambiente."""

from aurora_backend.contexts.conversation.services.language_model.factory import (
    LanguageModelConfigurationError,
    LanguageModelSettings,
    create_language_model,
)
from aurora_backend.contexts.conversation.services.language_model.port import (
    LanguageModel,
    LanguageModelResult,
    LanguageModelUnavailableError,
    LanguageModelUsage,
)

__all__ = [
    "LanguageModel",
    "LanguageModelConfigurationError",
    "LanguageModelResult",
    "LanguageModelSettings",
    "LanguageModelUnavailableError",
    "LanguageModelUsage",
    "create_language_model",
]
