"""Bounded context Conversa."""

from fastapi import APIRouter

from aurora_backend.contexts.conversation.features.send_message.router import (
    create_send_message_router,
)
from aurora_backend.contexts.conversation.services.chat_response.port import (
    ChatResponseGenerator,
)
from aurora_backend.contexts.conversation.services.triage.port import TriageEvaluator


def create_routers(
    *,
    triage_service: TriageEvaluator,
    chat_response_service: ChatResponseGenerator,
) -> tuple[APIRouter, ...]:
    return (
        create_send_message_router(
            triage_service=triage_service,
            chat_response_service=chat_response_service,
        ),
    )


__all__ = ["create_routers"]
