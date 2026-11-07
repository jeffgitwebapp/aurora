"""Porta LanguageModel: adaptadores Gemini e Claude intercambiáveis (D-13), sem rede."""

import asyncio
import json
from types import SimpleNamespace
from typing import Any

import anthropic
import httpx2
import pytest
from google.genai import errors, types

from aurora_backend.contexts.conversation.services.language_model.claude import (
    FALLBACK_BETA,
    ClaudeLanguageModel,
)
from aurora_backend.contexts.conversation.services.language_model.factory import (
    DEFAULT_MODELS,
    LanguageModelConfigurationError,
    LanguageModelSettings,
    create_language_model,
)
from aurora_backend.contexts.conversation.services.language_model.gemini import (
    GeminiLanguageModel,
)
from aurora_backend.contexts.conversation.services.language_model.port import (
    LanguageModelUnavailableError,
)

SCHEMA = {
    "type": "object",
    "properties": {"relevant_ids": {"type": "array", "items": {"type": "string"}}},
    "required": ["relevant_ids"],
    "additionalProperties": False,
}


def call(model: Any) -> Any:
    return asyncio.run(
        model.generate_json(
            system="sistema", prompt="pergunta", schema=SCHEMA, max_output_tokens=64
        )
    )


# --- Gemini -------------------------------------------------------------------------


class FakeGeminiModels:
    def __init__(self, response: Any = None, error: Exception | None = None):
        self.response = response
        self.error = error
        self.kwargs: dict[str, Any] = {}

    async def generate_content(self, **kwargs: Any) -> Any:
        self.kwargs = kwargs
        if self.error is not None:
            raise self.error
        return self.response


def gemini(models: FakeGeminiModels) -> GeminiLanguageModel:
    client = SimpleNamespace(aio=SimpleNamespace(models=models))
    return GeminiLanguageModel(client, model="gemini-3.6-flash")  # type: ignore[arg-type]


def gemini_response(
    text: str, finish: types.FinishReason = types.FinishReason.STOP
) -> types.GenerateContentResponse:
    return types.GenerateContentResponse(
        candidates=[
            types.Candidate(
                content=types.Content(role="model", parts=[types.Part(text=text)]),
                finish_reason=finish,
            )
        ],
        usage_metadata=types.GenerateContentResponseUsageMetadata(
            prompt_token_count=120, candidates_token_count=8
        ),
        model_version="gemini-3.6-flash",
    )


def test_gemini_returns_parsed_json_and_sends_schema() -> None:
    models = FakeGeminiModels(gemini_response(json.dumps({"relevant_ids": ["a#1"]})))

    result = call(gemini(models))

    assert result.data == {"relevant_ids": ["a#1"]}
    assert result.provider == "gemini"
    assert result.usage.input_tokens == 120
    config: types.GenerateContentConfig = models.kwargs["config"]
    assert models.kwargs["model"] == "gemini-3.6-flash"
    assert models.kwargs["contents"] == "pergunta"
    assert config.system_instruction == "sistema"
    assert config.response_mime_type == "application/json"
    assert config.response_json_schema == SCHEMA
    assert config.max_output_tokens == 64


def test_gemini_deadline_minimum_and_retries_for_temporary_errors() -> None:
    models = FakeGeminiModels(gemini_response(json.dumps({"relevant_ids": []})))

    call(gemini(models))

    http_options = models.kwargs["config"].http_options
    assert http_options.timeout == 10_000
    assert http_options.retry_options.attempts == 3
    assert http_options.retry_options.http_status_codes == [500, 503, 504]


@pytest.mark.parametrize(
    "models",
    [
        FakeGeminiModels(gemini_response("{}", types.FinishReason.SAFETY)),
        FakeGeminiModels(gemini_response("{}", types.FinishReason.MAX_TOKENS)),
        FakeGeminiModels(gemini_response("não é json")),
        FakeGeminiModels(gemini_response("[1, 2]")),
        FakeGeminiModels(
            types.GenerateContentResponse(
                prompt_feedback=types.GenerateContentResponsePromptFeedback(
                    block_reason=types.BlockedReason.SAFETY
                )
            )
        ),
        FakeGeminiModels(error=errors.APIError(429, {"error": {"message": "quota"}})),
        FakeGeminiModels(error=httpx2.ConnectTimeout("timeout")),
        FakeGeminiModels(error=TimeoutError()),
    ],
)
def test_gemini_failures_become_unavailable(models: FakeGeminiModels) -> None:
    with pytest.raises(LanguageModelUnavailableError):
        call(gemini(models))


# --- Claude -------------------------------------------------------------------------


class FakeClaudeMessages:
    def __init__(self, response: Any = None, error: Exception | None = None):
        self.response = response
        self.error = error
        self.kwargs: dict[str, Any] = {}

    async def create(self, **kwargs: Any) -> Any:
        self.kwargs = kwargs
        if self.error is not None:
            raise self.error
        return self.response


class FakeClaudeClient:
    def __init__(self, messages: FakeClaudeMessages):
        self.beta = SimpleNamespace(messages=messages)

    def with_options(self, **_: Any) -> "FakeClaudeClient":
        return self


def claude(messages: FakeClaudeMessages) -> ClaudeLanguageModel:
    return ClaudeLanguageModel(FakeClaudeClient(messages), model="claude-opus-5-5")  # type: ignore[arg-type]


def claude_response(text: str, stop_reason: str = "end_turn") -> SimpleNamespace:
    return SimpleNamespace(
        stop_reason=stop_reason,
        model="claude-opus-5-5",
        content=[SimpleNamespace(type="thinking"), SimpleNamespace(type="text", text=text)],
        usage=SimpleNamespace(input_tokens=100, output_tokens=10, cache_read_input_tokens=40),
    )


def test_claude_returns_parsed_json_and_sends_schema() -> None:
    messages = FakeClaudeMessages(claude_response(json.dumps({"relevant_ids": ["a#1"]})))

    result = call(claude(messages))

    assert result.data == {"relevant_ids": ["a#1"]}
    assert result.provider == "claude"
    assert result.usage.cached_input_tokens == 40
    kwargs = messages.kwargs
    assert kwargs["output_config"] == {
        "effort": "low",
        "format": {"type": "json_schema", "schema": SCHEMA},
    }
    assert kwargs["betas"] == [FALLBACK_BETA]
    assert kwargs["fallbacks"] == "default"
    assert kwargs["system"][0]["text"] == "sistema"
    assert kwargs["messages"] == [{"role": "user", "content": "pergunta"}]


@pytest.mark.parametrize(
    "messages",
    [
        FakeClaudeMessages(claude_response("{}", stop_reason="refusal")),
        FakeClaudeMessages(claude_response("{}", stop_reason="max_tokens")),
        FakeClaudeMessages(claude_response("não é json")),
        FakeClaudeMessages(
            error=anthropic.APIConnectionError(
                request=httpx2.Request("POST", "https://api.anthropic.com")
            )
        ),
        FakeClaudeMessages(
            error=anthropic.APITimeoutError(
                request=httpx2.Request("POST", "https://api.anthropic.com")
            )
        ),
    ],
)
def test_claude_failures_become_unavailable(messages: FakeClaudeMessages) -> None:
    with pytest.raises(LanguageModelUnavailableError):
        call(claude(messages))


# --- Fábrica ------------------------------------------------------------------------


def test_settings_default_to_gemini_free_model() -> None:
    settings = LanguageModelSettings.from_env({})

    assert settings.provider == "gemini"
    assert settings.model == DEFAULT_MODELS["gemini"] == "gemini-3.5-flash-lite"


def test_settings_switch_to_claude_only_by_environment() -> None:
    settings = LanguageModelSettings.from_env({"AURORA_LLM_PROVIDER": "Claude"})

    assert settings.provider == "claude"
    assert settings.model == "claude-opus-5-5"


def test_settings_accept_model_override() -> None:
    env = {"AURORA_LLM_PROVIDER": "gemini", "AURORA_LLM_MODEL": "gemini-3.5-flash-lite"}

    assert LanguageModelSettings.from_env(env).model == "gemini-3.5-flash-lite"


def test_settings_reject_unknown_provider() -> None:
    with pytest.raises(LanguageModelConfigurationError):
        LanguageModelSettings.from_env({"AURORA_LLM_PROVIDER": "outro"})


def test_gemini_requires_api_key() -> None:
    with pytest.raises(LanguageModelConfigurationError, match="GEMINI_API_KEY"):
        create_language_model(LanguageModelSettings("gemini", "gemini-3.6-flash"), env={})


def test_factory_builds_each_adapter() -> None:
    gemini_model = create_language_model(
        LanguageModelSettings("gemini", "gemini-3.6-flash"), env={"GEMINI_API_KEY": "teste"}
    )

    assert isinstance(gemini_model, GeminiLanguageModel)
    assert gemini_model.model == "gemini-3.6-flash"
