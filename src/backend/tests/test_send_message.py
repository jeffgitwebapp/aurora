import pytest
from fastapi.testclient import TestClient

from aurora_backend.contexts.conversation.features.send_message import handler
from aurora_backend.contexts.conversation.features.send_message.handler import (
    SIMULATED_REPLY_PREFIX,
)
from aurora_backend.main import app

client = TestClient(app)
ENDPOINT = "/api/chat/messages"


@pytest.mark.parametrize("message", ["Olá", "Preciso de ajuda", "  texto com espaços  "])
def test_non_empty_message_returns_disclaimed_simulated_text(message: str) -> None:
    response = client.post(ENDPOINT, json={"message": message})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    reply = response.json()["reply"]
    assert reply.startswith(f"{SIMULATED_REPLY_PREFIX}: ")
    assert len(reply) > len(SIMULATED_REPLY_PREFIX)


def test_simulated_paragraph_changes_with_generator(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(handler.random, "choice", lambda options: options[0])
    first_reply = handler.handle_send_message("Primeira mensagem")

    monkeypatch.setattr(handler.random, "choice", lambda options: options[-1])
    second_reply = handler.handle_send_message("Segunda mensagem")

    assert first_reply != second_reply
    assert first_reply.startswith(SIMULATED_REPLY_PREFIX)
    assert second_reply.startswith(SIMULATED_REPLY_PREFIX)


@pytest.mark.parametrize("message", ["", " ", "   \t\n "])
def test_empty_or_blank_message_is_rejected(message: str) -> None:
    response = client.post(ENDPOINT, json={"message": message})

    assert response.status_code == 422


def test_missing_message_field_is_rejected() -> None:
    response = client.post(ENDPOINT, json={})

    assert response.status_code == 422


def test_valid_message_returns_without_artificial_delay() -> None:
    response = client.post(ENDPOINT, json={"message": "Olá"})

    assert response.status_code == 200
    assert response.json()["reply"].startswith(SIMULATED_REPLY_PREFIX)


def test_get_is_not_allowed() -> None:
    response = client.get(ENDPOINT)

    assert response.status_code == 405
