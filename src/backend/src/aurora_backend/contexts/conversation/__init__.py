"""Bounded context Conversa."""

from fastapi import APIRouter

from aurora_backend.contexts.conversation.features.send_message.router import (
    create_send_message_router,
)
from aurora_backend.contexts.conversation.services.chat_response.port import (
    ChatResponseGenerator,
)
from aurora_backend.contexts.conversation.services.content_offer.port import (
    ContentOfferProvider,
)
from aurora_backend.contexts.conversation.services.guardrail.port import ScopeGuardrail
from aurora_backend.contexts.conversation.services.knowledge.port import KnowledgeRetriever
from aurora_backend.contexts.conversation.services.triage.port import TriageEvaluator


def create_routers(
    *,
    triage_service: TriageEvaluator,
    guardrail_service: ScopeGuardrail,
    offer_service: ContentOfferProvider,
    knowledge_service: KnowledgeRetriever,
    chat_response_service: ChatResponseGenerator,
) -> tuple[APIRouter, ...]:
    return (
        create_send_message_router(
            triage_service=triage_service,
            guardrail_service=guardrail_service,
            offer_service=offer_service,
            knowledge_service=knowledge_service,
            chat_response_service=chat_response_service,
        ),
    )


__all__ = ["create_routers"]
