import asyncio
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from aurora_backend.contexts.conversation.features.send_message import router as send_message_router
from aurora_backend.contexts.conversation.features.send_message.handler import (
    handle_send_message,
)
from aurora_backend.contexts.conversation.services.chat_response.service import (
    REPLY_INTRODUCTION,
    ChatResponseService,
)
from aurora_backend.contexts.conversation.services.content_offer.service import (
    ContentOfferService,
)
from aurora_backend.contexts.conversation.services.guardrail.models import (
    GuardrailResult,
    OutOfScopeCategory,
    ScopeDecision,
)
from aurora_backend.contexts.conversation.services.guardrail.port import (
    GuardrailUnavailableError,
)
from aurora_backend.contexts.conversation.services.guardrail.service import GuardrailService
from aurora_backend.contexts.conversation.services.knowledge.models import (
    KnowledgePassage,
    KnowledgeResult,
    KnowledgeStatus,
    SourceReference,
)
from aurora_backend.contexts.conversation.services.knowledge.port import (
    KnowledgeUnavailableError,
)
from aurora_backend.contexts.conversation.services.knowledge.service import KnowledgeService
from aurora_backend.contexts.conversation.services.triage.models import (
    TriageResult,
    TriageSignal,
    TriageStatus,
)
from aurora_backend.contexts.conversation.services.triage.service import TriageService
from aurora_backend.main import create_app

ENDPOINT = "/api/chat/messages"
NO_ACUTE_FIXTURE = "Quero informações sobre serviços de apoio na minha cidade"
DEFINITION_QUESTION = "O que é violência psicológica?"
CRIME_QUESTION = "Violência psicológica é crime?"
TEST_SOURCE = SourceReference(
    id="fonte-teste",
    title="Fonte sintética de teste",
    locator="seção 1",
    publisher="Testes automatizados",
    url="https://example.org/fonte-teste",
)
TEST_PASSAGE = KnowledgePassage(text="Trecho sintético.", source=TEST_SOURCE)


def assess_fixture(message: str) -> TriageResult:
    return asyncio.run(TriageService().assess(message))


def retrieve_fixture(message: str) -> KnowledgeResult:
    return asyncio.run(KnowledgeService().retrieve(message))


class FixedKnowledgeService:
    def __init__(self, result: KnowledgeResult) -> None:
        self.result = result
        self.messages: list[str] = []

    async def retrieve(self, message: str) -> KnowledgeResult:
        self.messages.append(message)
        return self.result


class UnusedGuardrailService:
    async def check_request(self, _message: str) -> GuardrailResult:
        del _message
        pytest.fail("Guardrail must not run for blocked triage results.")


class FailingGuardrailService:
    async def check_request(self, _message: str) -> GuardrailResult:
        del _message
        raise GuardrailUnavailableError


class UnusedKnowledgeService:
    async def retrieve(self, _message: str) -> KnowledgeResult:
        del _message
        pytest.fail("Knowledge service must not run for blocked triage results.")


class UnusedChatService:
    async def generate_reply(
        self,
        _message: str,
        _passages: tuple[KnowledgePassage, ...],
    ) -> str:
        del _message, _passages
        pytest.fail("Chat response service must not run without a found source.")


class FixedChatService:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[KnowledgePassage, ...]]] = []

    async def generate_reply(
        self,
        message: str,
        passages: tuple[KnowledgePassage, ...],
    ) -> str:
        self.calls.append((message, passages))
        return "Resposta ancorada de teste."


@pytest.fixture
def client() -> TestClient:
    return TestClient(
        create_app(
            triage_service=TriageService(),
            guardrail_service=GuardrailService(),
            offer_service=ContentOfferService(),
            knowledge_service=KnowledgeService(),
            chat_response_service=ChatResponseService(),
        )
    )


@pytest.fixture
def processing_delays(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    sleep_durations: list[float] = []

    async def record_processing_delay(seconds: float) -> None:
        sleep_durations.append(seconds)

    monkeypatch.setattr(
        send_message_router,
        "asyncio",
        SimpleNamespace(sleep=record_processing_delay),
    )
    return sleep_durations


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


def test_handler_does_not_call_knowledge_or_chat_for_acute_or_indeterminate() -> None:
    class FixedTriageService:
        def __init__(self, result: TriageResult) -> None:
            self.result = result

        async def assess(self, _message: str) -> TriageResult:
            del _message
            return self.result

    for triage_status in (TriageStatus.ACUTE, TriageStatus.INDETERMINATE):
        triage_result = TriageResult(
            status=triage_status,
            guidance="Orientação simulada.",
        )
        result = asyncio.run(
            handle_send_message(
                "Mensagem de teste",
                triage_service=FixedTriageService(triage_result),
                guardrail_service=UnusedGuardrailService(),
                offer_service=ContentOfferService(),
                knowledge_service=UnusedKnowledgeService(),
                chat_response_service=UnusedChatService(),
            )
        )

        assert result.triage is triage_result
        assert result.reply is None
        assert result.knowledge is None


def test_handler_returns_no_source_without_generating_reply() -> None:
    knowledge = FixedKnowledgeService(KnowledgeResult(status=KnowledgeStatus.NO_SOURCE))
    result = asyncio.run(
        handle_send_message(
            NO_ACUTE_FIXTURE,
            triage_service=TriageService(),
            guardrail_service=GuardrailService(),
            offer_service=ContentOfferService(),
            knowledge_service=knowledge,
            chat_response_service=UnusedChatService(),
        )
    )

    assert result.triage.status is TriageStatus.NO_ACUTE_SIGNAL
    assert result.reply is None
    assert result.knowledge is not None
    assert result.knowledge.status is KnowledgeStatus.NO_SOURCE
    assert knowledge.messages == [NO_ACUTE_FIXTURE]


def test_handler_generates_reply_only_from_retrieved_passages() -> None:
    knowledge_result = KnowledgeResult(
        status=KnowledgeStatus.FOUND,
        passages=(TEST_PASSAGE,),
    )
    chat_service = FixedChatService()
    result = asyncio.run(
        handle_send_message(
            DEFINITION_QUESTION,
            triage_service=TriageService(),
            guardrail_service=GuardrailService(),
            offer_service=ContentOfferService(),
            knowledge_service=FixedKnowledgeService(knowledge_result),
            chat_response_service=chat_service,
        )
    )

    assert result.reply == "Resposta ancorada de teste."
    assert result.knowledge is knowledge_result
    assert chat_service.calls == [(DEFINITION_QUESTION, (TEST_PASSAGE,))]


def test_handler_propagates_knowledge_failure_instead_of_answering() -> None:
    class FailingKnowledgeService:
        async def retrieve(self, _message: str) -> KnowledgeResult:
            del _message
            raise KnowledgeUnavailableError

    with pytest.raises(KnowledgeUnavailableError):
        asyncio.run(
            handle_send_message(
                DEFINITION_QUESTION,
                triage_service=TriageService(),
                guardrail_service=GuardrailService(),
                offer_service=ContentOfferService(),
                knowledge_service=FailingKnowledgeService(),
                chat_response_service=UnusedChatService(),
            )
        )


@pytest.mark.parametrize(
    ("message", "source_id"),
    [
        (DEFINITION_QUESTION, "lei-11340-2006-art-7-ii"),
        ("  o que e VIOLENCIA psicologica  ", "lei-11340-2006-art-7-ii"),
        (CRIME_QUESTION, "codigo-penal-art-147-b"),
    ],
)
def test_knowledge_fixtures_return_identified_demo_sources(
    message: str,
    source_id: str,
) -> None:
    result = retrieve_fixture(message)

    assert result.status is KnowledgeStatus.FOUND
    assert result.demo is True
    assert [source.id for source in result.sources] == [source_id]
    source = result.sources[0]
    assert source.url.startswith("https://www.planalto.gov.br/")
    assert source.title and source.locator and source.publisher


@pytest.mark.parametrize(
    "message",
    [
        NO_ACUTE_FIXTURE,
        "O que é violência psicológica? Ele faz isso comigo.",
        "Tenho dúvidas sobre meus direitos",
        "mensagem aleatória",
    ],
)
def test_messages_without_knowledge_fixture_return_no_source(message: str) -> None:
    result = retrieve_fixture(message)

    assert result.status is KnowledgeStatus.NO_SOURCE
    assert result.passages == ()
    assert result.sources == ()


def test_knowledge_result_rejects_found_without_passages() -> None:
    with pytest.raises(ValueError):
        KnowledgeResult(status=KnowledgeStatus.FOUND)


def test_chat_response_quotes_only_received_passages() -> None:
    reply = asyncio.run(ChatResponseService().generate_reply("pergunta", (TEST_PASSAGE,)))

    assert reply.startswith(REPLY_INTRODUCTION)
    assert "Fonte sintética de teste, seção 1: “Trecho sintético.”" in reply


def test_chat_response_refuses_to_answer_without_passages() -> None:
    with pytest.raises(ValueError):
        asyncio.run(ChatResponseService().generate_reply("pergunta", ()))


@pytest.mark.parametrize("message", ["", " ", "   \t\n "])
def test_empty_or_blank_message_is_rejected(client: TestClient, message: str) -> None:
    response = client.post(ENDPOINT, json={"message": message})

    assert response.status_code == 422


def test_missing_message_field_is_rejected(client: TestClient) -> None:
    response = client.post(ENDPOINT, json={})

    assert response.status_code == 422


@pytest.mark.parametrize(
    ("message", "source_id"),
    [
        (DEFINITION_QUESTION, "lei-11340-2006-art-7-ii"),
        (CRIME_QUESTION, "codigo-penal-art-147-b"),
    ],
)
def test_knowledge_fixture_returns_reply_with_sources_after_five_seconds(
    client: TestClient,
    processing_delays: list[float],
    message: str,
    source_id: str,
) -> None:
    response = client.post(ENDPOINT, json={"message": message})

    assert response.status_code == 200
    payload = response.json()
    assert payload["triage_status"] == "no_acute_signal"
    assert payload["signals"] == []
    assert payload["guidance"] is None
    assert payload["knowledge_status"] == "found"
    assert payload["demo"] is True
    assert payload["reply"].startswith(REPLY_INTRODUCTION)
    assert [source["id"] for source in payload["sources"]] == [source_id]
    assert set(payload["sources"][0]) == {
        "id",
        "title",
        "locator",
        "publisher",
        "url",
        "version",
    }
    assert processing_delays == [5]


def test_message_without_source_returns_no_source_state(
    client: TestClient,
    processing_delays: list[float],
) -> None:
    response = client.post(ENDPOINT, json={"message": NO_ACUTE_FIXTURE})

    assert response.status_code == 200
    payload = response.json()
    assert payload["triage_status"] == "no_acute_signal"
    assert payload["knowledge_status"] == "no_source"
    assert payload["reply"] is None
    assert payload["guidance"] is None
    assert payload["sources"] == []
    assert payload["demo"] is True
    assert processing_delays == [5]


def test_knowledge_failure_returns_503_without_reply(
    processing_delays: list[float],
) -> None:
    class FailingKnowledgeService:
        async def retrieve(self, _message: str) -> KnowledgeResult:
            del _message
            raise KnowledgeUnavailableError

    failing_client = TestClient(
        create_app(
            triage_service=TriageService(),
            guardrail_service=GuardrailService(),
            offer_service=ContentOfferService(),
            knowledge_service=FailingKnowledgeService(),
            chat_response_service=ChatResponseService(),
        )
    )
    response = failing_client.post(ENDPOINT, json={"message": DEFINITION_QUESTION})

    assert response.status_code == 503
    assert "reply" not in response.json()
    assert DEFINITION_QUESTION not in response.text
    assert processing_delays == []


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
    assert payload["knowledge_status"] is None
    assert payload["scope_status"] is None
    assert payload["out_of_scope_category"] is None
    assert payload["sources"] == []
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
    assert payload["knowledge_status"] is None
    assert payload["scope_status"] is None
    assert payload["out_of_scope_category"] is None
    assert payload["sources"] == []
    assert payload["signals"] == []
    assert "Isso não significa ausência de risco" in payload["guidance"]
    assert sleep_durations == []


OUT_OF_SCOPE_FIXTURES = [
    ("Eu tenho depressão?", OutOfScopeCategory.DIAGNOSIS),
    ("Que remédio devo tomar?", OutOfScopeCategory.PRESCRIPTION),
    ("O que acontece no meu caso?", OutOfScopeCategory.INDIVIDUAL_LEGAL_OPINION),
    ("Devo denunciar meu marido?", OutOfScopeCategory.INDIVIDUAL_LEGAL_OPINION),
]


def check_scope_fixture(message: str) -> GuardrailResult:
    return asyncio.run(GuardrailService().check_request(message))


@pytest.mark.parametrize(("message", "category"), OUT_OF_SCOPE_FIXTURES)
def test_exact_out_of_scope_fixtures_return_category(
    message: str,
    category: OutOfScopeCategory,
) -> None:
    result = check_scope_fixture(message)

    assert result.decision is ScopeDecision.OUT_OF_SCOPE
    assert result.category is category


def test_out_of_scope_fixture_normalizes_case_accents_and_punctuation() -> None:
    result = check_scope_fixture("  QUE REMEDIO devo tomar ")

    assert result.category is OutOfScopeCategory.PRESCRIPTION


@pytest.mark.parametrize(
    "message",
    [
        DEFINITION_QUESTION,
        CRIME_QUESTION,
        "Tenho dúvidas sobre meus direitos",
        "Quais são os direitos de uma mulher em situação de violência?",
        "Eu tenho depressão? Ou é só cansaço?",
        "O que acontece no meu caso? Ele grita comigo.",
    ],
)
def test_general_or_extended_questions_are_allowed(message: str) -> None:
    result = check_scope_fixture(message)

    assert result.decision is ScopeDecision.ALLOW
    assert result.category is None


def test_guardrail_result_requires_category_only_when_out_of_scope() -> None:
    with pytest.raises(ValueError):
        GuardrailResult(decision=ScopeDecision.OUT_OF_SCOPE)
    with pytest.raises(ValueError):
        GuardrailResult(
            decision=ScopeDecision.ALLOW,
            category=OutOfScopeCategory.DIAGNOSIS,
        )


def test_handler_stops_before_knowledge_and_chat_when_out_of_scope() -> None:
    result = asyncio.run(
        handle_send_message(
            "O que acontece no meu caso?",
            triage_service=TriageService(),
            guardrail_service=GuardrailService(),
            offer_service=ContentOfferService(),
            knowledge_service=UnusedKnowledgeService(),
            chat_response_service=UnusedChatService(),
        )
    )

    assert result.reply is None
    assert result.knowledge is None
    assert result.guardrail is not None
    assert result.guardrail.category is OutOfScopeCategory.INDIVIDUAL_LEGAL_OPINION


def test_triage_runs_before_scope_guardrail() -> None:
    result = asyncio.run(
        handle_send_message(
            "Ele disse que vai me matar",
            triage_service=TriageService(),
            guardrail_service=UnusedGuardrailService(),
            offer_service=ContentOfferService(),
            knowledge_service=UnusedKnowledgeService(),
            chat_response_service=UnusedChatService(),
        )
    )

    assert result.triage.status is TriageStatus.ACUTE
    assert result.guardrail is None


def test_handler_fails_closed_when_guardrail_is_unavailable() -> None:
    with pytest.raises(GuardrailUnavailableError):
        asyncio.run(
            handle_send_message(
                DEFINITION_QUESTION,
                triage_service=TriageService(),
                guardrail_service=FailingGuardrailService(),
                offer_service=ContentOfferService(),
                knowledge_service=UnusedKnowledgeService(),
                chat_response_service=UnusedChatService(),
            )
        )


@pytest.mark.parametrize(("message", "category"), OUT_OF_SCOPE_FIXTURES)
def test_out_of_scope_fixture_returns_limit_without_reply_sources_or_delay(
    client: TestClient,
    processing_delays: list[float],
    message: str,
    category: OutOfScopeCategory,
) -> None:
    response = client.post(ENDPOINT, json={"message": message})

    assert response.status_code == 200
    payload = response.json()
    assert payload["triage_status"] == "no_acute_signal"
    assert payload["scope_status"] == "out_of_scope"
    assert payload["out_of_scope_category"] == category.value
    assert payload["knowledge_status"] is None
    assert payload["reply"] is None
    assert payload["guidance"] is None
    assert payload["sources"] == []
    assert payload["demo"] is True
    assert processing_delays == []


def test_allowed_message_reports_allowed_scope(
    client: TestClient,
    processing_delays: list[float],
) -> None:
    response = client.post(ENDPOINT, json={"message": DEFINITION_QUESTION})

    payload = response.json()
    assert payload["scope_status"] == "allowed"
    assert payload["out_of_scope_category"] is None
    assert payload["knowledge_status"] == "found"
    assert processing_delays == [5]


def test_guardrail_failure_returns_503_without_reply(
    processing_delays: list[float],
) -> None:
    failing_client = TestClient(create_app(guardrail_service=FailingGuardrailService()))
    response = failing_client.post(ENDPOINT, json={"message": DEFINITION_QUESTION})

    assert response.status_code == 503
    assert "reply" not in response.json()
    assert DEFINITION_QUESTION not in response.text
    assert processing_delays == []


def test_get_is_not_allowed(client: TestClient) -> None:
    response = client.get(ENDPOINT)

    assert response.status_code == 405
