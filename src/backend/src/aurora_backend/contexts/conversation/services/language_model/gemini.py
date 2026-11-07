"""Adaptador Gemini (google-genai) da porta LanguageModel.

Plano gratuito: o Google pode usar os dados enviados para melhorar seus produtos.
Usar só com dados sintéticos até trocar para plano pago ou para o Claude (D-13).
"""

import asyncio
import json
from typing import Any

import httpx
import httpx2
from google import genai
from google.genai import errors, types

from aurora_backend.contexts.conversation.services.language_model.port import (
    LanguageModelResult,
    LanguageModelUnavailableError,
    LanguageModelUsage,
)

_TRANSPORT_ERRORS = (errors.APIError, httpx.HTTPError, httpx2.HTTPError, OSError, TimeoutError)
# A API do Gemini recusa prazos menores que 10 s ("Minimum allowed deadline is 10s").
MIN_API_DEADLINE_SECONDS = 10.0
# O plano gratuito devolve 503 ("high demand") com frequência: novas tentativas curtas
# só para erros temporários; o limite total protege a requisição da usuária.
RETRY_ATTEMPTS = 3
RETRY_STATUS_CODES = [500, 503, 504]
TOTAL_DEADLINE_SECONDS = 25.0


class GeminiLanguageModel:
    provider = "gemini"

    def __init__(
        self,
        client: genai.Client,
        *,
        model: str,
        timeout_seconds: float = 8.0,
        thinking_level: str = "LOW",
    ):
        self._client = client
        self.model = model
        self._api_deadline = max(timeout_seconds, MIN_API_DEADLINE_SECONDS)
        self._thinking_level = thinking_level

    async def generate_json(
        self,
        *,
        system: str,
        prompt: str,
        schema: dict[str, Any],
        max_output_tokens: int,
    ) -> LanguageModelResult:
        config = types.GenerateContentConfig(
            system_instruction=system,
            response_mime_type="application/json",
            response_json_schema=schema,
            max_output_tokens=max_output_tokens,
            thinking_config=types.ThinkingConfig(thinking_level=self._thinking_level),
            http_options=types.HttpOptions(
                timeout=int(self._api_deadline * 1000),
                retry_options=types.HttpRetryOptions(
                    attempts=RETRY_ATTEMPTS,
                    initial_delay=1.0,
                    max_delay=4.0,
                    http_status_codes=RETRY_STATUS_CODES,
                ),
            ),
        )
        try:
            response = await asyncio.wait_for(
                self._client.aio.models.generate_content(
                    model=self.model, contents=prompt, config=config
                ),
                timeout=max(TOTAL_DEADLINE_SECONDS, self._api_deadline),
            )
        except _TRANSPORT_ERRORS as exc:
            raise LanguageModelUnavailableError(f"gemini: {type(exc).__name__}") from exc

        feedback = response.prompt_feedback
        if feedback is not None and feedback.block_reason is not None:
            raise LanguageModelUnavailableError(f"gemini: bloqueado ({feedback.block_reason})")
        candidates = response.candidates or []
        if not candidates or candidates[0].finish_reason != types.FinishReason.STOP:
            reason = candidates[0].finish_reason if candidates else "sem candidato"
            raise LanguageModelUnavailableError(f"gemini: finish_reason={reason}")
        try:
            data = json.loads(response.text or "")
        except (json.JSONDecodeError, ValueError) as exc:
            raise LanguageModelUnavailableError("gemini: resposta fora do schema") from exc
        if not isinstance(data, dict):
            raise LanguageModelUnavailableError("gemini: resposta fora do schema")

        usage = response.usage_metadata
        return LanguageModelResult(
            data=data,
            provider=self.provider,
            model=response.model_version or self.model,
            usage=LanguageModelUsage(
                input_tokens=(usage.prompt_token_count or 0) if usage else 0,
                output_tokens=(usage.candidates_token_count or 0) if usage else 0,
                cached_input_tokens=(usage.cached_content_token_count or 0) if usage else 0,
            ),
        )
