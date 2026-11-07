"""Escolhe o motor de conhecimento/resposta da conversa pelo ambiente.

AURORA_CHAT_ENGINE:
- fixtures (padrão): frases-fixture do protótipo (KnowledgeService + ChatResponseService);
- base: base curada vigente, só BM25, sem LLM (KnowledgeBaseService + SourceReplyService);
- llm: base curada com seleção de trechos pelo LLM do AURORA_LLM_PROVIDER (D-12/D-13).

AURORA_AGENTIC_SEARCH (só no motor llm; padrão false): com true, o LLM pode pedir
até 2 buscas extras com termos técnicos antes de escolher os trechos (F4).

Triagem, escopo e oferta continuam determinísticos em todos os motores (U-01).
Configuração inválida impede a subida do app; nunca há troca silenciosa de motor.
"""

import os
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum

from aurora_backend.contexts.conversation.services.chat_response.port import (
    ChatResponseGenerator,
)
from aurora_backend.contexts.conversation.services.chat_response.service import (
    ChatResponseService,
)
from aurora_backend.contexts.conversation.services.chat_response.source_reply import (
    SourceReplyService,
)
from aurora_backend.contexts.conversation.services.knowledge.port import KnowledgeRetriever
from aurora_backend.contexts.conversation.services.knowledge.service import KnowledgeService


class ChatEngine(StrEnum):
    FIXTURES = "fixtures"
    BASE = "base"
    LLM = "llm"


class ChatEngineConfigurationError(ValueError):
    """Motor desconhecido ou dependência do motor mal configurada."""


@dataclass(frozen=True)
class ConversationEngine:
    engine: ChatEngine
    knowledge_service: KnowledgeRetriever
    chat_response_service: ChatResponseGenerator
    description: str


def engine_from_env(env: Mapping[str, str] = os.environ) -> ChatEngine:
    raw = env.get("AURORA_CHAT_ENGINE", ChatEngine.FIXTURES.value).strip().lower()
    try:
        return ChatEngine(raw)
    except ValueError as exc:
        options = ", ".join(engine.value for engine in ChatEngine)
        raise ChatEngineConfigurationError(
            f"AURORA_CHAT_ENGINE inválido: {raw!r} (use {options})"
        ) from exc


def agentic_search_from_env(env: Mapping[str, str] = os.environ) -> bool:
    raw = env.get("AURORA_AGENTIC_SEARCH", "false").strip().lower()
    if raw in ("true", "1"):
        return True
    if raw in ("false", "0", ""):
        return False
    raise ChatEngineConfigurationError(
        f"AURORA_AGENTIC_SEARCH inválido: {raw!r} (use true ou false)"
    )


def build_conversation_engine(env: Mapping[str, str] = os.environ) -> ConversationEngine:
    engine = engine_from_env(env)
    if engine is ChatEngine.FIXTURES:
        return ConversationEngine(
            engine=engine,
            knowledge_service=KnowledgeService(),
            chat_response_service=ChatResponseService(),
            description="fixtures do protótipo",
        )

    from aurora_backend.contexts.conversation.services.knowledge_base.repository import (
        KnowledgeBaseRepository,
    )
    from aurora_backend.contexts.conversation.services.knowledge_base.service import (
        KnowledgeBaseService,
    )

    repository = KnowledgeBaseRepository.from_file()
    if engine is ChatEngine.BASE:
        return ConversationEngine(
            engine=engine,
            knowledge_service=KnowledgeBaseService(repository),
            chat_response_service=SourceReplyService(),
            description=f"base {repository.kb_version}, BM25 sem LLM",
        )

    from aurora_backend.contexts.conversation.services.answer_guardrail.service import (
        AnswerGuardrailService,
    )
    from aurora_backend.contexts.conversation.services.grounded_answer.service import (
        GroundedAnswerService,
    )
    from aurora_backend.contexts.conversation.services.knowledge_base.agentic_selector import (
        LanguageModelAgenticChunkSelector,
    )
    from aurora_backend.contexts.conversation.services.knowledge_base.selector import (
        LanguageModelChunkSelector,
    )
    from aurora_backend.contexts.conversation.services.language_model.factory import (
        LanguageModelConfigurationError,
        LanguageModelSettings,
        create_language_model,
    )

    agentic_search = agentic_search_from_env(env)
    try:
        settings = LanguageModelSettings.from_env(env)
        language_model = create_language_model(settings, env)
    except LanguageModelConfigurationError as exc:
        raise ChatEngineConfigurationError(f"AURORA_CHAT_ENGINE=llm: {exc}") from exc
    return ConversationEngine(
        engine=engine,
        knowledge_service=KnowledgeBaseService(
            repository,
            selector=(
                LanguageModelAgenticChunkSelector(language_model)
                if agentic_search
                else LanguageModelChunkSelector(language_model)
            ),
        ),
        chat_response_service=GroundedAnswerService(
            language_model, repository, AnswerGuardrailService()
        ),
        description=(
            f"base {repository.kb_version}, BM25 + seleção e redação por "
            f"{settings.provider}/{settings.model}"
            + (" com busca reformulada (até 2 buscas extras)" if agentic_search else "")
        ),
    )
