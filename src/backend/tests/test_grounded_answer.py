"""Redação pelo LLM ancorada nos trechos (F2): marcadores [n], guardrail e falha fechada."""

import asyncio
import json
from typing import Any

import pytest
from fastapi.testclient import TestClient

from aurora_backend.contexts.conversation.services.answer_guardrail.service import (
    AnswerGuardrailService,
)
from aurora_backend.contexts.conversation.services.chat_response.port import (
    ChatResponseUnavailableError,
)
from aurora_backend.contexts.conversation.services.grounded_answer.service import (
    ANSWER_SCHEMA,
    GroundedAnswerService,
    load_system_prompt,
)
from aurora_backend.contexts.conversation.services.knowledge.models import (
    KnowledgePassage,
    KnowledgeResult,
    KnowledgeStatus,
    SourceReference,
)
from aurora_backend.contexts.conversation.services.knowledge_base.repository import (
    KnowledgeBaseRepository,
)
from aurora_backend.contexts.conversation.services.language_model.port import (
    LanguageModelResult,
    LanguageModelUnavailableError,
)
from aurora_backend.main import create_app

REPOSITORY = KnowledgeBaseRepository.from_file()


def passage(chunk_id: str) -> KnowledgePassage:
    chunk = REPOSITORY.get(chunk_id)
    assert chunk is not None
    return KnowledgePassage(
        text=chunk.citable_text,
        source=SourceReference(
            id=chunk.id,
            title=chunk.title,
            locator=chunk.locator,
            publisher=chunk.publisher,
            url=chunk.url,
            version=chunk.version,
        ),
    )


PASSAGES = (passage("cp-art147b#caput"), passage("lei-11340-2006#art7-II"))


class FakeLanguageModel:
    provider = "fake"
    model = "fake-model"

    def __init__(self, data: Any = None, error: Exception | None = None):
        self.data = data
        self.error = error
        self.calls: list[dict[str, Any]] = []

    async def generate_json(self, **kwargs: Any) -> LanguageModelResult:
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return LanguageModelResult(data=self.data, provider=self.provider, model=self.model)


def service(model: FakeLanguageModel) -> GroundedAnswerService:
    return GroundedAnswerService(model, REPOSITORY, AnswerGuardrailService())


def generate(model: FakeLanguageModel, message: str = "Violência psicológica é crime?") -> str:
    return asyncio.run(service(model).generate_reply(message, PASSAGES))


def segments(*items: tuple[str, list[str]]) -> dict[str, Any]:
    return {"segments": [{"text": text, "source_ids": ids} for text, ids in items]}


def test_reply_renders_markers_in_source_order() -> None:
    model = FakeLanguageModel(
        segments(
            (
                "Pela Lei Maria da Penha, a violência psicológica é uma forma de violência.",
                ["lei-11340-2006#art7-II"],
            ),
            ("Desde 2021 ela também é crime.", ["cp-art147b#caput", "lei-11340-2006#art7-II"]),
            ("Eu não avalio a sua situação; a Defensoria pode fazer essa análise.", []),
        )
    )

    reply = generate(model)

    assert reply.split("\n\n") == [
        "Pela Lei Maria da Penha, a violência psicológica é uma forma de violência. [2]",
        "Desde 2021 ela também é crime. [1][2]",
        "Eu não avalio a sua situação; a Defensoria pode fazer essa análise.",
    ]


def test_prompt_contains_passages_scope_notes_and_message_but_schema_is_fixed() -> None:
    model = FakeLanguageModel(segments(("Texto com fonte.", ["cp-art147b#caput"])))

    generate(model, "ele me humilha todo dia")

    call = model.calls[0]
    assert call["schema"] == ANSWER_SCHEMA
    assert call["system"] == load_system_prompt()[0]
    assert '<trecho id="cp-art147b#caput">' in call["prompt"]
    assert "Atenção: o Aurora não avalia" in call["prompt"]
    assert "ele me humilha todo dia" in call["prompt"]


def test_prompt_version_is_stable_hash() -> None:
    text, version = load_system_prompt()

    assert version.startswith("system_v1_2@")
    assert len(version.split("@")[1]) == 12
    assert "Você não é uma pessoa" in text


@pytest.mark.parametrize(
    "model",
    [
        FakeLanguageModel(error=LanguageModelUnavailableError("gemini: 503")),
        FakeLanguageModel({"outra": []}),
        FakeLanguageModel({"segments": [{"text": 1, "source_ids": []}]}),
        FakeLanguageModel(segments(("Você deve denunciar hoje.", ["cp-art147b#caput"]))),
        FakeLanguageModel(segments(("A pena é de 10 anos.", []))),
        FakeLanguageModel(segments(("Isso é crime.", ["inventado#1"]))),
        FakeLanguageModel(segments(("Ligue (81) 3333-4444.", ["cp-art147b#caput"]))),
    ],
)
def test_failures_and_guardrail_violations_are_fail_closed(model: FakeLanguageModel) -> None:
    with pytest.raises(ChatResponseUnavailableError):
        generate(model)


def test_trace_logs_only_metadata(caplog: pytest.LogCaptureFixture) -> None:
    secret = "MARCADOR-PRIVADO-456"
    model = FakeLanguageModel(segments(("Resposta com fonte.", ["cp-art147b#caput"])))

    with caplog.at_level("INFO"):
        generate(model, f"{secret} ele me xinga")

    records = [r.getMessage() for r in caplog.records if "grounded_answer" in r.getMessage()]
    assert len(records) == 1
    event = json.loads(records[0])
    assert event["outcome"] == "informational"
    assert event["cited_source_ids"] == ["cp-art147b#caput"]
    assert event["prompt_version"].startswith("system_v1_2@")
    assert secret not in records[0]
    assert "Resposta com fonte" not in records[0]
    assert "Causar dano emocional" not in records[0]


class FoundKnowledge:
    async def retrieve(self, message: str) -> KnowledgeResult:
        del message
        return KnowledgeResult(status=KnowledgeStatus.FOUND, passages=PASSAGES)


def test_guardrail_rejection_returns_503_through_http_contract() -> None:
    blocked = service(FakeLanguageModel(segments(("Saia de casa agora.", ["cp-art147b#caput"]))))
    client = TestClient(
        create_app(knowledge_service=FoundKnowledge(), chat_response_service=blocked)
    )

    response = client.post("/api/chat/messages", json={"message": "o que fazer?"})

    assert response.status_code == 503
    assert response.json() == {"detail": "O serviço de informações está indisponível no momento."}


def test_grounded_reply_goes_through_http_contract_with_sources() -> None:
    grounded = service(FakeLanguageModel(segments(("Desde 2021 é crime.", ["cp-art147b#caput"]))))
    client = TestClient(
        create_app(knowledge_service=FoundKnowledge(), chat_response_service=grounded)
    )

    payload = client.post("/api/chat/messages", json={"message": "é crime?"}).json()

    assert payload["knowledge_status"] == "found"
    assert payload["reply"] == "Desde 2021 é crime. [1]"
    assert [s["id"] for s in payload["sources"]] == ["cp-art147b#caput", "lei-11340-2006#art7-II"]
