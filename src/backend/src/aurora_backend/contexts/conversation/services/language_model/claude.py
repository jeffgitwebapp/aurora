"""Adaptador Claude (SDK anthropic) da porta LanguageModel."""

import json
from typing import Any

import anthropic

from aurora_backend.contexts.conversation.services.language_model.port import (
    LanguageModelResult,
    LanguageModelUnavailableError,
    LanguageModelUsage,
)

FALLBACK_BETA = "server-side-fallback-2026-07-01"


class ClaudeLanguageModel:
    provider = "claude"

    def __init__(
        self,
        client: anthropic.AsyncAnthropic,
        *,
        model: str,
        effort: str = "low",
        timeout_seconds: float = 8.0,
    ):
        self._client = client.with_options(timeout=timeout_seconds, max_retries=1)
        self.model = model
        self._effort = effort

    async def generate_json(
        self,
        *,
        system: str,
        prompt: str,
        schema: dict[str, Any],
        max_output_tokens: int,
    ) -> LanguageModelResult:
        try:
            response = await self._client.beta.messages.create(
                model=self.model,
                max_tokens=max_output_tokens,
                system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
                messages=[{"role": "user", "content": prompt}],
                output_config={
                    "effort": self._effort,
                    "format": {"type": "json_schema", "schema": schema},
                },
                betas=[FALLBACK_BETA],
                fallbacks="default",
            )
        except (anthropic.APIStatusError, anthropic.APIConnectionError) as exc:
            raise LanguageModelUnavailableError(f"claude: {type(exc).__name__}") from exc

        if response.stop_reason != "end_turn":
            raise LanguageModelUnavailableError(f"claude: stop_reason={response.stop_reason}")
        text = next((block.text for block in response.content if block.type == "text"), None)
        try:
            data = json.loads(text or "")
        except json.JSONDecodeError as exc:
            raise LanguageModelUnavailableError("claude: resposta fora do schema") from exc
        if not isinstance(data, dict):
            raise LanguageModelUnavailableError("claude: resposta fora do schema")

        usage = response.usage
        return LanguageModelResult(
            data=data,
            provider=self.provider,
            model=response.model,
            usage=LanguageModelUsage(
                input_tokens=usage.input_tokens,
                output_tokens=usage.output_tokens,
                cached_input_tokens=getattr(usage, "cache_read_input_tokens", 0) or 0,
            ),
        )
