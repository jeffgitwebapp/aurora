"""Saudação, agradecimento e despedida sem LLM (U-11)."""

import asyncio

import pytest
from fastapi.testclient import TestClient

from aurora_backend.contexts.conversation.services.knowledge.models import KnowledgeResult
from aurora_backend.contexts.conversation.services.small_talk.service import (
    REPLIES,
    ConversationKind,
    SmallTalkService,
)
from aurora_backend.main import create_app

ENDPOINT = "/api/chat/messages"


def classify(message: str) -> ConversationKind | None:
    reply = asyncio.run(SmallTalkService().respond(message))
    return reply.kind if reply is not None else None


@pytest.mark.parametrize(
    ("message", "kind"),
    [
        ("oi", ConversationKind.GREETING),
        ("Oi!", ConversationKind.GREETING),
        ("oii", ConversationKind.GREETING),
        ("OLÁ", ConversationKind.GREETING),
        ("olá, tudo bem?", ConversationKind.GREETING),
        ("bom dia", ConversationKind.GREETING),
        ("Boa noite, Aurora", ConversationKind.GREETING),
        ("tem alguém aí?", ConversationKind.GREETING),
        ("obrigada", ConversationKind.THANKS),
        ("muito obrigado pela ajuda", ConversationKind.THANKS),
        ("valeu!", ConversationKind.THANKS),
        ("tchau", ConversationKind.FAREWELL),
        ("até mais, obrigada", ConversationKind.FAREWELL),
    ],
)
def test_recognizes_whole_message_small_talk(message: str, kind: ConversationKind) -> None:
    assert classify(message) is kind


@pytest.mark.parametrize(
    "message",
    [
        "oi, meu marido me ameaça",
        "olá, o que é violência psicológica?",
        "obrigada, mas ele continua me humilhando",
        "O que é violência psicológica?",
        "boa",
        "",
        "   ",
    ],
)
def test_messages_with_content_follow_normal_flow(message: str) -> None:
    assert classify(message) is None


class ExplodingKnowledge:
    async def retrieve(self, _message: str) -> KnowledgeResult:
        raise AssertionError("saudação não pode chegar à busca nem ao LLM")


class ExplodingReply:
    async def generate_reply(self, _message: str, _passages: tuple) -> str:
        raise AssertionError("saudação não pode chamar a redação")


def client() -> TestClient:
    app = create_app(knowledge_service=ExplodingKnowledge(), chat_response_service=ExplodingReply())
    return TestClient(app)


@pytest.mark.parametrize(
    ("message", "conversation"),
    [("oi", "greeting"), ("obrigada", "thanks"), ("tchau", "farewell")],
)
def test_api_returns_conversation_kind_without_search_or_llm(
    message: str, conversation: str
) -> None:
    response = client().post(ENDPOINT, json={"message": message})

    assert response.status_code == 200
    payload = response.json()
    assert payload["conversation"] == conversation
    assert payload["triage_status"] == "no_acute_signal"
    assert payload["scope_status"] == "allowed"
    assert payload["knowledge_status"] is None
    assert payload["reply"] == REPLIES[ConversationKind(conversation)]
    assert payload["sources"] == []
    assert payload["offer"] is None


def test_risk_in_greeting_still_triggers_emergency() -> None:
    response = client().post(ENDPOINT, json={"message": "oi, quero me matar"})

    payload = response.json()
    assert payload["triage_status"] == "acute"
    assert payload["conversation"] is None


def test_other_responses_report_conversation_null() -> None:
    response = client().post(ENDPOINT, json={"message": "Eu tenho depressão?"})

    assert response.json()["conversation"] is None


def test_every_kind_has_a_backend_reply_text() -> None:
    assert set(REPLIES) == set(ConversationKind)
    assert all(text.strip() for text in REPLIES.values())
