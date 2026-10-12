import time

import pytest
from fastapi.testclient import TestClient

from aurora_backend.contexts.conversation.features.send_message.router import (
    RESPONSE_DELAY_SECONDS,
)
from aurora_backend.main import app

client = TestClient(app)
ENDPOINT = "/api/chat/messages"
FIXED_REPLY = "Este chatbot está em desenvolvimento."


@pytest.mark.parametrize("message", ["Olá", "Preciso de ajuda", "  texto com espaços  "])
def test_non_empty_message_returns_fixed_reply(message: str) -> None:
    response = client.post(ENDPOINT, json={"message": message})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"reply": FIXED_REPLY}


@pytest.mark.parametrize("message", ["", " ", "   \t\n "])
def test_empty_or_blank_message_is_rejected(message: str) -> None:
    response = client.post(ENDPOINT, json={"message": message})

    assert response.status_code == 422


def test_missing_message_field_is_rejected() -> None:
    response = client.post(ENDPOINT, json={})

    assert response.status_code == 422


def test_valid_message_response_is_delayed() -> None:
    started_at = time.monotonic()

    response = client.post(ENDPOINT, json={"message": "Olá"})

    elapsed = time.monotonic() - started_at
    assert response.status_code == 200
    assert elapsed >= RESPONSE_DELAY_SECONDS


def test_get_is_not_allowed() -> None:
    response = client.get(ENDPOINT)

    assert response.status_code == 405
