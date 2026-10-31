import asyncio
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from aurora_backend.contexts.conversation.features.send_message import router as send_message_router
from aurora_backend.contexts.conversation.features.send_message.handler import (
    handle_send_message,
)
from aurora_backend.contexts.conversation.services.chat_response import service as chat_service
from aurora_backend.contexts.conversation.services.chat_response.service import (
    SIMULATED_REPLY_PREFIX,
    ChatResponseService,
)
from aurora_backend.contexts.conversation.services.triage.models import (
    TriageResult,
    TriageSignal,
    TriageStatus,
)
from aurora_backend.contexts.conversation.services.triage.service import TriageService
from aurora_backend.main import create_app

ENDPOINT = "/api/chat/messages"
NO_ACUTE_FIXTURE = "Quero informações sobre serviços de apoio na minha cidade"


def assess_fixture(message: str) -> TriageResult:
    return asyncio.run(TriageService().assess(message))


@pytest.fixture
def client() -> TestClient:
    return TestClient(
        create_app(
            triage_service=TriageService(),
            chat_response_service=ChatResponseService(),
        )
    )


@pytest.mark.parametrize(
    ("message", "signal"),
    [
        ("Estou pensando em me matar", TriageSignal.SUICIDAL_IDEATION),
        ("Quero tirar minha vida", TriageSignal.SUICIDAL_IDEATION),
        ("Ele está me agredindo agora", TriageSignal.ONGOING_ASSAULT),
        ("Estou sendo atacada neste momento", TriageSignal.ONGOING_ASSAULT),
        ("Ele disse que vai me matar", TriageSignal.DEATH_THREAT),
        ("Recebi uma ameaça de morte", TriageSignal.DEATH_THREAT),
        ("Ele está com uma arma aqui", TriageSignal.WEAPON_PRESENT),
        ("Há uma arma no local agora", TriageSignal.WEAPON_PRESENT),
    ],
)
def test_exact_risk_fixtures_are_classified_as_acute(
    message: str,
    signal: TriageSignal,
) -> None:
    result = assess_fixture(message)

    assert result.status is TriageStatus.ACUTE
    assert result.signals == (signal,)
    assert result.guidance is not None
    assert "Simulação do protótipo" in result.guidance
    assert "não avalia situações reais" in result.guidance


def test_triage_normalizes_case_accents_whitespace_and_terminal_punctuation() -> None:
    result = assess_fixture("  ELE ESTA COM UMA ARMA AQUI!  ")

    assert result.status is TriageStatus.ACUTE
    assert result.signals == (TriageSignal.WEAPON_PRESENT,)


def test_multiple_exact_risk_fixtures_keep_all_signals() -> None:
    result = assess_fixture("Ele está me agredindo agora. Há uma arma no local agora.")

    assert result.status is TriageStatus.ACUTE
    assert result.signals == (
        TriageSignal.ONGOING_ASSAULT,
        TriageSignal.WEAPON_PRESENT,
    )


@pytest.mark.parametrize(
    "message",
    [
        "Não estou pensando em me matar",
        "Ele disse que talvez fosse me matar, mas não fez ameaça",
        "Estou pensando em me matar porque estou escrevendo um exemplo",
        "Preciso de informações sobre serviços de apoio",
        "mensagem aleatória",
        "Quero informações sobre serviços de apoio na minha cidade",
    ],
)
def test_messages_without_an_exact_risk_or_indeterminate_fixture_follow_normal_flow(
    message: str,
) -> None:
    result = assess_fixture(message)

    assert result.status is TriageStatus.NO_ACUTE_SIGNAL
    assert result.signals == ()
    assert result.guidance is None


def test_only_exact_indeterminate_fixture_returns_indeterminate() -> None:
    result = assess_fixture("  FRASE INCERTA! ")

    assert result.status is TriageStatus.INDETERMINATE
    assert result.signals == ()
    assert result.guidance is not None
    assert "Isso não significa ausência de risco" in result.guidance


@pytest.mark.parametrize(
    "message",
    [
        "frase incerta. Preciso de ajuda.",
        "frase incerta porque estou testando.",
    ],
)
def test_indeterminate_fixture_with_additional_text_follows_normal_flow(
    message: str,
) -> None:
    result = assess_fixture(message)

    assert result.status is TriageStatus.NO_ACUTE_SIGNAL


def test_only_explicit_control_fixture_is_no_acute_signal() -> None:
    result = assess_fixture(NO_ACUTE_FIXTURE)

    assert result.status is TriageStatus.NO_ACUTE_SIGNAL
    assert result.signals == ()
    assert result.guidance is None


def test_handler_does_not_call_chat_service_for_acute_or_indeterminate_results() -> None:
    class FixedTriageService:
        def __init__(self, result: TriageResult) -> None:
            self.result = result

        async def assess(self, _message: str) -> TriageResult:
            del _message
            return self.result

    class UnusedChatService:
        async def generate_reply(self, _message: str) -> str:
            del _message
            pytest.fail("Chat response service must not run for blocked triage results.")

    for triage_status in (TriageStatus.ACUTE, TriageStatus.INDETERMINATE):
        triage_result = TriageResult(
            status=triage_status,
            guidance="Orientação simulada.",
        )
        result = asyncio.run(
            handle_send_message(
                "Mensagem de teste",
                triage_service=FixedTriageService(triage_result),
                chat_response_service=UnusedChatService(),
            )
        )

        assert result.triage is triage_result
        assert result.reply is None


def test_handler_calls_chat_service_only_after_no_acute_triage() -> None:
    class FixedChatService:
        def __init__(self) -> None:
            self.messages: list[str] = []

        async def generate_reply(self, message: str) -> str:
            self.messages.append(message)
            return "Resposta mockada."

    chat_service = FixedChatService()
    result = asyncio.run(
        handle_send_message(
            NO_ACUTE_FIXTURE,
            triage_service=TriageService(),
            chat_response_service=chat_service,
        )
    )

    assert result.triage.status is TriageStatus.NO_ACUTE_SIGNAL
    assert result.reply == "Resposta mockada."
    assert chat_service.messages == [NO_ACUTE_FIXTURE]


def test_mock_chat_response_changes_with_generator(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(chat_service.random, "choice", lambda options: options[0])
    first_reply = asyncio.run(ChatResponseService().generate_reply("mensagem 1"))

    monkeypatch.setattr(chat_service.random, "choice", lambda options: options[-1])
    second_reply = asyncio.run(ChatResponseService().generate_reply("mensagem 2"))

    assert first_reply != second_reply
    assert first_reply.startswith(SIMULATED_REPLY_PREFIX)
    assert second_reply.startswith(SIMULATED_REPLY_PREFIX)


@pytest.mark.parametrize("message", ["", " ", "   \t\n "])
def test_empty_or_blank_message_is_rejected(client: TestClient, message: str) -> None:
    response = client.post(ENDPOINT, json={"message": message})

    assert response.status_code == 422


def test_missing_message_field_is_rejected(client: TestClient) -> None:
    response = client.post(ENDPOINT, json={})

    assert response.status_code == 422


def test_control_fixture_returns_chat_reply_after_five_seconds(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sleep_durations: list[float] = []

    async def record_processing_delay(seconds: float) -> None:
        sleep_durations.append(seconds)

    monkeypatch.setattr(
        send_message_router,
        "asyncio",
        SimpleNamespace(sleep=record_processing_delay),
    )
    response = client.post(ENDPOINT, json={"message": NO_ACUTE_FIXTURE})

    assert response.status_code == 200
    assert response.json()["triage_status"] == "no_acute_signal"
    assert response.json()["signals"] == []
    assert response.json()["guidance"] is None
    assert response.json()["reply"].startswith(f"{SIMULATED_REPLY_PREFIX}: ")
    assert sleep_durations == [5]


@pytest.mark.parametrize(
    ("message", "signal"),
    [
        ("Estou pensando em me matar", "suicidal_ideation"),
        ("Ele está me agredindo agora", "ongoing_assault"),
        ("Ele disse que vai me matar", "death_threat"),
        ("Ele está com uma arma aqui", "weapon_present"),
    ],
)
def test_acute_fixture_returns_service_guidance_without_chat_or_delay(
    client: TestClient,
    message: str,
    signal: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sleep_durations: list[float] = []

    async def record_processing_delay(seconds: float) -> None:
        sleep_durations.append(seconds)

    monkeypatch.setattr(
        send_message_router,
        "asyncio",
        SimpleNamespace(sleep=record_processing_delay),
    )
    response = client.post(ENDPOINT, json={"message": message})

    assert response.status_code == 200
    payload = response.json()
    assert payload["reply"] is None
    assert payload["triage_status"] == "acute"
    assert payload["signals"] == [signal]
    assert "Simulação do protótipo" in payload["guidance"]
    assert sleep_durations == []


def test_exact_indeterminate_fixture_returns_service_guidance_without_chat_or_delay(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sleep_durations: list[float] = []

    async def record_processing_delay(seconds: float) -> None:
        sleep_durations.append(seconds)

    monkeypatch.setattr(
        send_message_router,
        "asyncio",
        SimpleNamespace(sleep=record_processing_delay),
    )
    response = client.post(ENDPOINT, json={"message": "frase incerta"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["reply"] is None
    assert payload["triage_status"] == "indeterminate"
    assert payload["signals"] == []
    assert "Isso não significa ausência de risco" in payload["guidance"]
    assert sleep_durations == []


def test_unrecognized_message_uses_normal_chat_flow(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sleep_durations: list[float] = []

    async def record_processing_delay(seconds: float) -> None:
        sleep_durations.append(seconds)

    monkeypatch.setattr(
        send_message_router,
        "asyncio",
        SimpleNamespace(sleep=record_processing_delay),
    )
    response = client.post(ENDPOINT, json={"message": "Oi, gostaria de conversar"})

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload["reply"], str)
    assert payload["triage_status"] == "no_acute_signal"
    assert payload["signals"] == []
    assert payload["guidance"] is None
    assert sleep_durations == [5]


def test_get_is_not_allowed(client: TestClient) -> None:
    response = client.get(ENDPOINT)

    assert response.status_code == 405
