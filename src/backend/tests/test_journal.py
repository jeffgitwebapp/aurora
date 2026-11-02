import asyncio
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from aurora_backend.contexts.accounts.services.accounts.models import (
    InvalidJournalEntryError,
    JournalEntryNotFoundError,
)
from aurora_backend.contexts.accounts.services.accounts.service import AccountService
from aurora_backend.main import create_app

PASSWORD = "senhaforte1"
# 2026-11-02 12:00 no horário local do processo.
NOW = datetime(2026, 11, 2, 12, 0).timestamp()


def run(coroutine):
    return asyncio.run(coroutine)


@pytest.fixture
def service() -> AccountService:
    return AccountService(wall_clock=lambda: NOW)


@pytest.fixture
def token(service: AccountService) -> str:
    return run(service.register("lua_azul", PASSWORD)).token


def test_create_edit_list_and_delete_entries(service: AccountService, token: str) -> None:
    first = run(
        service.save_journal_entry(token, None, "2026-10-30", "21:15", "Registro sintético 1")
    )
    second = run(
        service.save_journal_entry(token, None, "2026-11-01", None, "Registro sintético 2")
    )

    assert [entry.id for entry in run(service.list_journal(token))] == [second.id, first.id]

    edited = run(service.save_journal_entry(token, first.id, "2026-10-30", "21:30", "Editado"))
    assert edited.id == first.id
    assert edited.description == "Editado"
    assert len(run(service.list_journal(token))) == 2

    run(service.delete_journal_entry(token, first.id))
    assert [entry.id for entry in run(service.list_journal(token))] == [second.id]
    with pytest.raises(JournalEntryNotFoundError):
        run(service.delete_journal_entry(token, first.id))


def test_journal_is_encrypted_at_rest(service: AccountService, token: str) -> None:
    entry = run(service.save_journal_entry(token, None, "2026-11-01", None, "Texto secreto"))

    stored = service._accounts["lua_azul"].journal[entry.id]
    assert b"secreto" not in stored.ciphertext
    assert b"2026-11-01" not in stored.ciphertext
    assert "secreto" not in repr(service._accounts)


@pytest.mark.parametrize(
    ("entry_date", "entry_time", "description"),
    [
        ("2026-11-03", None, "Futuro"),
        ("02/11/2026", None, "Formato"),
        ("2026-02-30", None, "Inexistente"),
        ("2026-11-01", "25:00", "Hora"),
        ("2026-11-01", "9:00", "Hora curta"),
        ("2026-11-01", None, "   "),
        ("2026-11-01", None, "x" * 4001),
    ],
)
def test_invalid_entries_are_rejected(
    service: AccountService,
    token: str,
    entry_date: str,
    entry_time: str | None,
    description: str,
) -> None:
    with pytest.raises(InvalidJournalEntryError):
        run(service.save_journal_entry(token, None, entry_date, entry_time, description))


def test_editing_unknown_entry_fails(service: AccountService, token: str) -> None:
    with pytest.raises(JournalEntryNotFoundError):
        run(service.save_journal_entry(token, "inexistente", "2026-11-01", None, "x"))


def test_journal_is_deleted_with_account(service: AccountService, token: str) -> None:
    run(service.save_journal_entry(token, None, "2026-11-01", None, "Registro"))
    run(service.delete_account(token))

    new_token = run(service.register("lua_azul", PASSWORD)).token
    assert run(service.list_journal(new_token)) == ()


def test_http_journal_flow() -> None:
    client = TestClient(create_app(account_service=AccountService()))
    token = client.post(
        "/api/accounts", json={"nickname": "lua_azul", "password": PASSWORD}
    ).json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post(
        "/api/account/journal",
        json={"date": "2026-01-10", "time": "", "description": "Registro sintético"},
        headers=headers,
    )
    assert created.status_code == 201
    entry = created.json()
    assert entry["time"] is None

    updated = client.put(
        f"/api/account/journal/{entry['id']}",
        json={"date": "2026-01-10", "time": "08:05", "description": "Editado"},
        headers=headers,
    )
    assert updated.json()["time"] == "08:05"
    listing = client.get("/api/account/journal", headers=headers).json()
    assert listing["demo"] is True
    assert [item["description"] for item in listing["entries"]] == ["Editado"]

    bad = client.post(
        "/api/account/journal",
        json={"date": "2999-01-01", "description": "x"},
        headers=headers,
    )
    assert bad.status_code == 422
    assert client.get("/api/account/journal").status_code == 401
    assert client.delete("/api/account/journal/inexistente", headers=headers).status_code == 404
    assert client.delete(f"/api/account/journal/{entry['id']}", headers=headers).status_code == 204
