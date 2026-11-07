"""Escolhe o provedor de LLM pelo ambiente; trocar Gemini ↔ Claude não exige mudar código.

AURORA_LLM_PROVIDER = gemini (padrão na demonstração) | claude
AURORA_LLM_MODEL    = gemini-3.5-flash-lite (padrão do Gemini) | claude-opus-5-5 (padrão do Claude)
Credencial: GEMINI_API_KEY (Gemini) ou ANTHROPIC_API_KEY / perfil `ant auth login` (Claude).
"""

import os
from collections.abc import Mapping
from dataclasses import dataclass

from aurora_backend.contexts.conversation.services.language_model.port import LanguageModel

DEFAULT_MODELS = {"gemini": "gemini-3.5-flash-lite", "claude": "claude-opus-5-5"}


class LanguageModelConfigurationError(ValueError):
    """Provedor desconhecido ou credencial ausente; o app não deve subir assim."""


@dataclass(frozen=True)
class LanguageModelSettings:
    provider: str
    model: str
    timeout_seconds: float = 8.0

    @classmethod
    def from_env(cls, env: Mapping[str, str] = os.environ) -> "LanguageModelSettings":
        provider = env.get("AURORA_LLM_PROVIDER", "gemini").strip().lower()
        if provider not in DEFAULT_MODELS:
            raise LanguageModelConfigurationError(
                f"AURORA_LLM_PROVIDER inválido: {provider!r} (use gemini ou claude)"
            )
        model = env.get("AURORA_LLM_MODEL", "").strip() or DEFAULT_MODELS[provider]
        timeout = float(env.get("AURORA_LLM_TIMEOUT_SECONDS", "8"))
        return cls(provider=provider, model=model, timeout_seconds=timeout)


def create_language_model(
    settings: LanguageModelSettings, env: Mapping[str, str] = os.environ
) -> LanguageModel:
    if settings.provider == "gemini":
        api_key = env.get("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise LanguageModelConfigurationError("GEMINI_API_KEY não definida")
        from google import genai

        from aurora_backend.contexts.conversation.services.language_model.gemini import (
            GeminiLanguageModel,
        )

        return GeminiLanguageModel(
            genai.Client(api_key=api_key),
            model=settings.model,
            timeout_seconds=settings.timeout_seconds,
        )

    import anthropic

    from aurora_backend.contexts.conversation.services.language_model.claude import (
        ClaudeLanguageModel,
    )

    try:
        client = anthropic.AsyncAnthropic()
    except anthropic.AnthropicError as exc:
        raise LanguageModelConfigurationError("credencial do Claude ausente") from exc
    return ClaudeLanguageModel(
        client, model=settings.model, timeout_seconds=settings.timeout_seconds
    )
