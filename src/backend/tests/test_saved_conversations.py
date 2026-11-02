import asyncio

import pytest
from fastapi.testclient import TestClient

from aurora_backend.contexts.accounts.services.accounts.models import (
    ConversationNotFoundError,
    InvalidConversationError,
    InvalidSessionError,
    SavedMessage,
)
from aurora_backend.contexts.accounts.services.accounts.service import AccountService
from aurora_backend.main import create_app

PASSWORD = "senhaforte1"
MESSAGES = (
    SavedMessage(role="user", text="Relato sintético de teste para salvar"),
    SavedMessage(role="assistant", text="Resposta de demonstração."),
)


def run(coroutine):
    return asyncio.run(coroutine)


@pytest.fixture
def service() -> AccountService:
    return AccountService()


def test_save_list_and_read_conversation(service: AccountService) -> None:
    session = run(service.register("lua_azul", PASSWORD))
    summary = run(service.save_conversation(session.token, MESSAGES))

    assert summary.message_count == 2
    assert summary.excerpt == "Relato sintético de teste para salvar"
    assert run(service.list_conversations(session.token)) == (summary,)
    saved = run(service.get_conversation(session.token, summary.id))
    assert saved.messages == MESSAGES


def test_conversations_are_encrypted_at_rest(service: AccountService) -> None:
    session = run(service.register("lua_azul", PASSWORD))
    summary = run(service.save_conversation(session.token, MESSAGES))

    stored = service._accounts["lua_azul"].conversations[summary.id]
    assert b"Relato" not in stored.ciphertext
    assert "Relato" not in repr(service._accounts)


def test_new_login_with_password_reads_previous_conversations(service: AccountService) -> None:
    first = run(service.register("lua_azul", PASSWORD))
    summary = run(service.save_conversation(first.token, MESSAGES))
    run(service.logout(first.token))

    second = run(service.login("lua_azul", PASSWORD))
    assert run(service.get_conversation(second.token, summary.id)).messages == MESSAGES


def test_accounts_cannot_read_each_other(service: AccountService) -> None:
    owner = run(service.register("lua_azul", PASSWORD))
    other = run(service.register("sol_verde", PASSWORD))
    summary = run(service.save_conversation(owner.token, MESSAGES))

    assert run(service.list_conversations(other.token)) == ()
    with pytest.raises(ConversationNotFoundError):
        run(service.get_conversation(other.token, summary.id))


@pytest.mark.parametrize(
    "messages",
    [
        (),
        (SavedMessage(role="system", text="x"),),
        (SavedMessage(role="user", text="   "),),
        (SavedMessage(role="user", text="x" * 4001),),
        tuple(SavedMessage(role="user", text="x") for _ in range(201)),
    ],
)
def test_invalid_conversations_are_rejected(
    service: AccountService,
    messages: tuple[SavedMessage, ...],
) -> None:
    session = run(service.register("lua_azul", PASSWORD))
    with pytest.raises(InvalidConversationError):
        run(service.save_conversation(session.token, messages))


def test_delete_conversation(service: AccountService) -> None:
    session = run(service.register("lua_azul", PASSWORD))
    summary = run(service.save_conversation(session.token, MESSAGES))
    run(service.delete_conversation(session.token, summary.id))

    assert run(service.list_conversations(session.token)) == ()
    with pytest.raises(ConversationNotFoundError):
        run(service.delete_conversation(session.token, summary.id))


def test_delete_account_removes_account_data_and_all_sessions(service: AccountService) -> None:
    first = run(service.register("lua_azul", PASSWORD))
    second = run(service.login("lua_azul", PASSWORD))
    run(service.save_conversation(first.token, MESSAGES))

    run(service.delete_account(first.token))

    assert "lua_azul" not in service._accounts
    for token in (first.token, second.token):
        with pytest.raises(InvalidSessionError):
            run(service.current(token))
    assert run(service.register("lua_azul", PASSWORD)).nickname == "lua_azul"


def test_http_save_list_read_delete_flow() -> None:
    client = TestClient(create_app(account_service=AccountService()))
    token = client.post(
        "/api/accounts", json={"nickname": "lua_azul", "password": PASSWORD}
    ).json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    body = {"messages": [{"role": m.role, "text": m.text} for m in MESSAGES]}

    created = client.post("/api/account/conversations", json=body, headers=headers)
    assert created.status_code == 201
    conversation_id = created.json()["id"]
    listing = client.get("/api/account/conversations", headers=headers).json()
    assert listing["demo"] is True
    assert listing["conversations"][0]["message_count"] == 2
    read = client.get(f"/api/account/conversations/{conversation_id}", headers=headers)
    assert read.json()["messages"] == body["messages"]

    assert (
        client.post(
            "/api/account/conversations", json={"messages": []}, headers=headers
        ).status_code
        == 422
    )
    assert client.get("/api/account/conversations").status_code == 401
    assert client.get("/api/account/conversations/inexistente", headers=headers).status_code == 404
    assert (
        client.delete(f"/api/account/conversations/{conversation_id}", headers=headers).status_code
        == 204
    )

    assert client.delete("/api/accounts/current", headers=headers).status_code == 204
    assert client.get("/api/sessions/current", headers=headers).status_code == 401
    assert client.delete("/api/accounts/current", headers=headers).status_code == 401
