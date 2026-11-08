"""Relato pessoal sem fonte recebe acolhimento em vez do "não sei" (U-14)."""

import asyncio

import pytest
from fastapi.testclient import TestClient

from aurora_backend.contexts.conversation.features.send_message.replies import (
    DISCLOSURE_NO_SOURCE_REPLY,
    NO_SOURCE_REPLY,
)
from aurora_backend.contexts.conversation.services.disclosure.service import DisclosureService
from aurora_backend.contexts.conversation.services.knowledge.models import (
    KnowledgeResult,
    KnowledgeStatus,
)
from aurora_backend.main import create_app

ENDPOINT = "/api/chat/messages"


def is_disclosure(message: str) -> bool:
    return asyncio.run(DisclosureService().is_disclosure(message))


@pytest.mark.parametrize(
    "message",
    [
        "meu marido está me gritando",
        "Meu namorado me xinga na frente dos outros",
        "ELE ME HUMILHA TODO DIA",
        "meu ex fica me ameacando",
        "ele controla meu celular",
        "meu companheiro não me deixa sair com as amigas",
        "ele me chama de burra",
        "estou com medo, meu marido está me gritando",
        "tenho muito medo dele",
        "não aguento mais essa situação",
        "me sinto humilhada",
        "sofro violência em casa",
    ],
)
def test_recognizes_personal_disclosure(message: str) -> None:
    assert is_disclosure(message) is True


@pytest.mark.parametrize(
    "message",
    [
        "O que é violência psicológica?",
        "ameaça é crime?",
        "previsão do tempo amanhã",
        "Quero informações sobre serviços de apoio na minha cidade",
        "meu marido viajou",
        "bateria do celular acabou",
        "",
        "   ",
    ],
)
def test_ignores_questions_and_unrelated_messages(message: str) -> None:
    assert is_disclosure(message) is False


class NoSourceKnowledge:
    async def retrieve(self, _message: str) -> KnowledgeResult:
        return KnowledgeResult(status=KnowledgeStatus.NO_SOURCE)


class ExplodingReply:
    async def generate_reply(self, _message: str, _passages: tuple) -> str:
        raise AssertionError("sem fonte não pode chamar a redação")


def client() -> TestClient:
    app = create_app(knowledge_service=NoSourceKnowledge(), chat_response_service=ExplodingReply())
    return TestClient(app)


def test_disclosure_without_source_returns_welcoming_reply() -> None:
    response = client().post(ENDPOINT, json={"message": "meu marido está me gritando"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["triage_status"] == "no_acute_signal"
    assert payload["knowledge_status"] == "no_source"
    assert payload["reply"] == DISCLOSURE_NO_SOURCE_REPLY
    assert payload["sources"] == []
    assert payload["conversation"] is None


def test_question_without_source_keeps_generic_reply() -> None:
    response = client().post(ENDPOINT, json={"message": "previsão do tempo amanhã"})

    assert response.json()["reply"] == NO_SOURCE_REPLY


def test_acute_risk_in_disclosure_still_opens_emergency() -> None:
    response = client().post(ENDPOINT, json={"message": "meu marido está me batendo agora"})

    payload = response.json()
    assert payload["triage_status"] == "acute"
    assert payload["reply"] is None
