import asyncio

import pytest
from fastapi.testclient import TestClient

from aurora_backend.contexts.accounts.services.accounts.models import (
    InvalidSafetyPlanError,
    TrustedContact,
)
from aurora_backend.contexts.accounts.services.accounts.service import AccountService
from aurora_backend.contexts.conversation.features.send_message.handler import (
    handle_send_message,
)
from aurora_backend.contexts.conversation.features.send_message.replies import (
    SAFETY_GUIDE_OFFER_REPLY,
)
from aurora_backend.contexts.conversation.services.chat_response.service import (
    ChatResponseService,
)
from aurora_backend.contexts.conversation.services.content_offer.models import ContentOffer
from aurora_backend.contexts.conversation.services.content_offer.service import (
    ContentOfferService,
)
from aurora_backend.contexts.conversation.services.guardrail.service import GuardrailService
from aurora_backend.contexts.conversation.services.knowledge.models import KnowledgeResult
from aurora_backend.contexts.conversation.services.triage.service import TriageService
from aurora_backend.contexts.learning.services.safety_guide.service import SafetyGuideService
from aurora_backend.main import create_app

PASSWORD = "senhaforte1"
OFFER_PHRASE = "Quero pensar na minha segurança"
CONTACTS = (TrustedContact(name="Amiga Ana", phone="(81) 99999-0000"),)


def run(coroutine):
    return asyncio.run(coroutine)


@pytest.fixture
def service() -> AccountService:
    return AccountService()


@pytest.fixture
def token(service: AccountService) -> str:
    return run(service.register("lua_azul", PASSWORD)).token


def test_guide_has_only_placeholder_sections() -> None:
    content = run(SafetyGuideService().content())

    assert content.in_preparation is True
    assert [section.title for section in content.sections] == [
        "Pensar na sua segurança",
        "Documentos e itens importantes",
        "Pessoas e serviços de apoio",
    ]
    assert all(
        paragraph.startswith("Conteúdo em preparação — demonstração")
        for section in content.sections
        for paragraph in section.paragraphs
    )


def test_empty_plan_then_save_and_read(service: AccountService, token: str) -> None:
    empty = run(service.get_safety_plan(token))
    assert empty.contacts == ()
    assert empty.updated_at is None

    saved = run(service.save_safety_plan(token, CONTACTS, "Minhas anotações sintéticas"))
    assert saved.contacts == CONTACTS
    assert saved.notes == "Minhas anotações sintéticas"
    assert run(service.get_safety_plan(token)) == saved


def test_plan_is_encrypted_at_rest(service: AccountService, token: str) -> None:
    run(service.save_safety_plan(token, CONTACTS, "Anotação secreta"))

    stored = service._accounts["lua_azul"].safety_plan
    assert stored is not None
    assert b"Ana" not in stored.ciphertext
    assert b"secreta" not in stored.ciphertext
    assert "secreta" not in repr(service._accounts)


@pytest.mark.parametrize(
    ("contacts", "notes"),
    [
        (CONTACTS * 6, ""),
        ((TrustedContact(name="  ", phone="81999990000"),), ""),
        ((TrustedContact(name="Ana", phone="123"),), ""),
        ((TrustedContact(name="Ana", phone="abcdefghij"),), ""),
        ((), "x" * 4001),
    ],
)
def test_invalid_plan_is_rejected(
    service: AccountService,
    token: str,
    contacts: tuple[TrustedContact, ...],
    notes: str,
) -> None:
    with pytest.raises(InvalidSafetyPlanError):
        run(service.save_safety_plan(token, contacts, notes))


def test_plan_is_deleted_with_account(service: AccountService, token: str) -> None:
    run(service.save_safety_plan(token, CONTACTS, "Notas"))
    run(service.delete_account(token))

    new_token = run(service.register("lua_azul", PASSWORD)).token
    assert run(service.get_safety_plan(new_token)).contacts == ()


@pytest.mark.parametrize("message", [OFFER_PHRASE, "  quero pensar na minha seguranca! "])
def test_offer_fixture_suggests_safety_guide(message: str) -> None:
    assert run(ContentOfferService().suggest(message)) is ContentOffer.SAFETY_GUIDE


@pytest.mark.parametrize("message", ["Quero pensar na minha segurança agora mesmo", "Oi"])
def test_other_messages_get_no_offer(message: str) -> None:
    assert run(ContentOfferService().suggest(message)) is None


def test_handler_returns_offer_without_knowledge_or_generation() -> None:
    class UnusedKnowledge:
        async def retrieve(self, _message: str) -> KnowledgeResult:
            pytest.fail("Offer must not consult knowledge.")

    result = run(
        handle_send_message(
            OFFER_PHRASE,
            triage_service=TriageService(),
            guardrail_service=GuardrailService(),
            offer_service=ContentOfferService(),
            knowledge_service=UnusedKnowledge(),
            chat_response_service=ChatResponseService(),
        )
    )

    assert result.offer is ContentOffer.SAFETY_GUIDE
    assert result.reply == SAFETY_GUIDE_OFFER_REPLY
    assert result.knowledge is None


def test_http_offer_guide_and_plan() -> None:
    client = TestClient(create_app(account_service=AccountService()))

    offer = client.post("/api/chat/messages", json={"message": OFFER_PHRASE}).json()
    assert offer["offer"] == "safety_guide"
    assert offer["knowledge_status"] is None
    assert offer["reply"] == SAFETY_GUIDE_OFFER_REPLY
    risk = client.post("/api/chat/messages", json={"message": "Ele disse que vai me matar"}).json()
    assert risk["offer"] is None

    guide = client.get("/api/learning/safety-guide").json()
    assert guide["in_preparation"] is True
    assert len(guide["sections"]) == 3

    token = client.post(
        "/api/accounts", json={"nickname": "lua_azul", "password": PASSWORD}
    ).json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get("/api/account/safety-plan", headers=headers).json()["updated_at"] is None
    saved = client.put(
        "/api/account/safety-plan",
        json={"contacts": [{"name": "Amiga Ana", "phone": "81 99999-0000"}], "notes": "Notas"},
        headers=headers,
    )
    assert saved.status_code == 200
    assert saved.json()["contacts"] == [{"name": "Amiga Ana", "phone": "81 99999-0000"}]
    assert saved.json()["demo"] is True
    bad = client.put(
        "/api/account/safety-plan",
        json={"contacts": [{"name": "Ana", "phone": "12"}], "notes": ""},
        headers=headers,
    )
    assert bad.status_code == 422
    assert client.get("/api/account/safety-plan").status_code == 401
