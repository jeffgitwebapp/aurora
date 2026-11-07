"""Roteamento do motor da conversa por AURORA_CHAT_ENGINE (fixtures | base | llm)."""

import asyncio

import pytest
from fastapi.testclient import TestClient

from aurora_backend.contexts.conversation.engine import (
    ChatEngine,
    ChatEngineConfigurationError,
    build_conversation_engine,
)
from aurora_backend.contexts.conversation.services.chat_response.service import (
    ChatResponseService,
)
from aurora_backend.contexts.conversation.services.chat_response.source_reply import (
    SOURCE_REPLY_INTRODUCTION,
    SourceReplyService,
)
from aurora_backend.contexts.conversation.services.grounded_answer.service import (
    GroundedAnswerService,
)
from aurora_backend.contexts.conversation.services.knowledge.models import (
    KnowledgePassage,
    SourceReference,
)
from aurora_backend.contexts.conversation.services.knowledge.service import KnowledgeService
from aurora_backend.contexts.conversation.services.knowledge_base.selector import (
    LanguageModelChunkSelector,
)
from aurora_backend.contexts.conversation.services.knowledge_base.service import (
    KnowledgeBaseService,
)
from aurora_backend.main import create_app


def test_default_engine_is_fixtures() -> None:
    engine = build_conversation_engine({})

    assert engine.engine is ChatEngine.FIXTURES
    assert isinstance(engine.knowledge_service, KnowledgeService)
    assert isinstance(engine.chat_response_service, ChatResponseService)


def test_base_engine_uses_curated_base_without_llm() -> None:
    engine = build_conversation_engine({"AURORA_CHAT_ENGINE": "BASE"})

    assert engine.engine is ChatEngine.BASE
    assert isinstance(engine.knowledge_service, KnowledgeBaseService)
    assert engine.knowledge_service._selector is None
    assert isinstance(engine.chat_response_service, SourceReplyService)
    assert "BM25 sem LLM" in engine.description


def test_llm_engine_uses_selector_from_configured_provider() -> None:
    engine = build_conversation_engine(
        {"AURORA_CHAT_ENGINE": "llm", "AURORA_LLM_PROVIDER": "gemini", "GEMINI_API_KEY": "teste"}
    )

    assert engine.engine is ChatEngine.LLM
    assert isinstance(engine.knowledge_service, KnowledgeBaseService)
    assert isinstance(engine.knowledge_service._selector, LanguageModelChunkSelector)
    assert isinstance(engine.chat_response_service, GroundedAnswerService)
    assert "gemini/" in engine.description
    assert "teste" not in engine.description


def test_llm_engine_without_key_fails_at_startup() -> None:
    with pytest.raises(ChatEngineConfigurationError, match="GEMINI_API_KEY"):
        build_conversation_engine({"AURORA_CHAT_ENGINE": "llm"})


def test_unknown_engine_fails_at_startup() -> None:
    with pytest.raises(ChatEngineConfigurationError, match="fixtures, base, llm"):
        build_conversation_engine({"AURORA_CHAT_ENGINE": "mock"})


def test_create_app_fails_instead_of_falling_back(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AURORA_CHAT_ENGINE", "llm")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(ChatEngineConfigurationError):
        create_app()


def test_base_engine_answers_through_existing_http_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AURORA_CHAT_ENGINE", "base")
    client = TestClient(create_app())

    payload = client.post(
        "/api/chat/messages", json={"message": "violencia psicologica e crime"}
    ).json()

    assert payload["knowledge_status"] == "found"
    assert payload["reply"].startswith(SOURCE_REPLY_INTRODUCTION)
    assert "[1]" in payload["reply"]
    assert "cp-art147b#caput" in [source["id"] for source in payload["sources"]]
    assert all(source["url"].startswith("https://") for source in payload["sources"])
    assert payload["demo"] is True


def test_base_engine_keeps_deterministic_triage_first(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AURORA_CHAT_ENGINE", "base")
    client = TestClient(create_app())

    payload = client.post(
        "/api/chat/messages", json={"message": "Ele disse que vai me matar"}
    ).json()

    assert payload["triage_status"] == "acute"
    assert payload["knowledge_status"] is None
    assert payload["reply"] is None


def test_source_reply_numbers_sources_in_order() -> None:
    def passage(source_id: str, text: str) -> KnowledgePassage:
        return KnowledgePassage(
            text=text,
            source=SourceReference(
                id=source_id,
                title=f"Fonte {source_id}",
                locator="art. 1º",
                publisher="Órgão",
                url="https://exemplo.gov.br",
            ),
        )

    reply = asyncio.run(
        SourceReplyService().generate_reply(
            "pergunta", (passage("a", "primeiro"), passage("b", "segundo"))
        )
    )

    assert reply.split("\n\n") == [
        SOURCE_REPLY_INTRODUCTION,
        "Fonte a, art. 1º: “primeiro” [1]",
        "Fonte b, art. 1º: “segundo” [2]",
    ]
