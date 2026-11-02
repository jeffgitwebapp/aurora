import asyncio

import pytest
from fastapi.testclient import TestClient

from aurora_backend.contexts.accounts.services.accounts.models import (
    AccountLockedError,
    InvalidCredentialsError,
    InvalidRegistrationError,
    InvalidSessionError,
    NicknameTakenError,
)
from aurora_backend.contexts.accounts.services.accounts.service import (
    LOCK_SECONDS,
    SESSION_TTL_SECONDS,
    AccountService,
)
from aurora_backend.main import create_app

PASSWORD = "senhaforte1"


class FakeClock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def service(clock: FakeClock) -> AccountService:
    return AccountService(clock=clock)


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app(account_service=AccountService()))


def run(coroutine):
    return asyncio.run(coroutine)


@pytest.mark.parametrize("nickname", ["ab", "a" * 31, "com espaço", "acentuação", ""])
def test_register_rejects_invalid_nickname(service: AccountService, nickname: str) -> None:
    with pytest.raises(InvalidRegistrationError):
        run(service.register(nickname, PASSWORD))


@pytest.mark.parametrize("password", ["curta1", "somenteletras", "1234567890", "a1" * 65])
def test_register_rejects_weak_password(service: AccountService, password: str) -> None:
    with pytest.raises(InvalidRegistrationError):
        run(service.register("lua.azul", password))


def test_register_and_login_return_session(service: AccountService) -> None:
    created = run(service.register("Lua.Azul", PASSWORD))
    logged = run(service.login("lua.azul", PASSWORD))

    assert created.nickname == logged.nickname == "Lua.Azul"
    assert created.token != logged.token
    assert run(service.current(logged.token)) == "Lua.Azul"


def test_nickname_is_unique_ignoring_case(service: AccountService) -> None:
    run(service.register("lua_azul", PASSWORD))
    with pytest.raises(NicknameTakenError):
        run(service.register("LUA_AZUL", PASSWORD))


def test_password_is_not_stored_in_plain_text(service: AccountService) -> None:
    run(service.register("lua_azul", PASSWORD))

    assert PASSWORD.encode() not in repr(service._accounts).encode()


def test_wrong_password_and_unknown_nickname_share_generic_error(
    service: AccountService,
) -> None:
    run(service.register("lua_azul", PASSWORD))

    with pytest.raises(InvalidCredentialsError) as wrong_password:
        run(service.login("lua_azul", "outrasenha1"))
    with pytest.raises(InvalidCredentialsError) as unknown:
        run(service.login("ninguem", PASSWORD))
    assert str(wrong_password.value) == str(unknown.value) == "Apelido ou senha incorretos."


@pytest.mark.parametrize("registered", [True, False])
def test_five_failures_lock_nickname_for_one_minute(
    service: AccountService,
    clock: FakeClock,
    registered: bool,
) -> None:
    if registered:
        run(service.register("lua_azul", PASSWORD))
    for _ in range(5):
        with pytest.raises(InvalidCredentialsError):
            run(service.login("lua_azul", "errada12345"))

    with pytest.raises(AccountLockedError):
        run(service.login("lua_azul", PASSWORD))

    clock.now += LOCK_SECONDS + 1
    if registered:
        assert run(service.login("lua_azul", PASSWORD)).nickname == "lua_azul"


def test_successful_login_resets_failures(service: AccountService) -> None:
    run(service.register("lua_azul", PASSWORD))
    for _ in range(4):
        with pytest.raises(InvalidCredentialsError):
            run(service.login("lua_azul", "errada12345"))
    run(service.login("lua_azul", PASSWORD))
    for _ in range(4):
        with pytest.raises(InvalidCredentialsError):
            run(service.login("lua_azul", "errada12345"))

    assert run(service.login("lua_azul", PASSWORD)).nickname == "lua_azul"


def test_logout_and_expiry_end_session(service: AccountService, clock: FakeClock) -> None:
    first = run(service.register("lua_azul", PASSWORD))
    run(service.logout(first.token))
    with pytest.raises(InvalidSessionError):
        run(service.current(first.token))

    second = run(service.login("lua_azul", PASSWORD))
    clock.now += SESSION_TTL_SECONDS
    with pytest.raises(InvalidSessionError):
        run(service.current(second.token))


def test_http_register_login_current_logout(client: TestClient) -> None:
    created = client.post("/api/accounts", json={"nickname": "lua_azul", "password": PASSWORD})
    assert created.status_code == 201
    assert created.json()["demo"] is True
    assert "password" not in created.text

    login = client.post("/api/sessions", json={"nickname": "lua_azul", "password": PASSWORD})
    token = login.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    assert client.get("/api/sessions/current", headers=headers).json() == {
        "nickname": "lua_azul",
        "demo": True,
    }
    assert client.delete("/api/sessions/current", headers=headers).status_code == 204
    assert client.get("/api/sessions/current", headers=headers).status_code == 401


def test_http_error_statuses(client: TestClient) -> None:
    body = {"nickname": "lua_azul", "password": PASSWORD}
    assert client.post("/api/accounts", json={**body, "password": "fraca"}).status_code == 422
    client.post("/api/accounts", json=body)
    assert client.post("/api/accounts", json=body).status_code == 409

    wrong = client.post("/api/sessions", json={**body, "password": "errada12345"})
    assert wrong.status_code == 401
    assert wrong.json()["detail"] == "Apelido ou senha incorretos."
    for _ in range(4):
        client.post("/api/sessions", json={**body, "password": "errada12345"})
    assert client.post("/api/sessions", json=body).status_code == 429
    assert client.get("/api/sessions/current").status_code == 401
