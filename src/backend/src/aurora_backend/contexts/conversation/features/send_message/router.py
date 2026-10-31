"""Adaptador HTTP da feature EnviarMensagem."""

import asyncio

from fastapi import APIRouter, HTTPException, status

from aurora_backend.contexts.conversation.features.send_message.handler import (
    EmptyMessageError,
    handle_send_message,
)
from aurora_backend.contexts.conversation.features.send_message.schemas import (
    SendMessageRequest,
    SendMessageResponse,
)
from aurora_backend.contexts.conversation.services.chat_response.port import (
    ChatResponseGenerator,
)
from aurora_backend.contexts.conversation.services.triage.port import TriageEvaluator

SIMULATED_PROCESSING_DELAY_SECONDS = 5


def create_send_message_router(
    *,
    triage_service: TriageEvaluator,
    chat_response_service: ChatResponseGenerator,
) -> APIRouter:
    router = APIRouter(prefix="/api/chat", tags=["conversa"])

    @router.post("/messages", response_model=SendMessageResponse)
    async def send_message(request: SendMessageRequest) -> SendMessageResponse:
        try:
            result = await handle_send_message(
                request.message,
                triage_service=triage_service,
                chat_response_service=chat_response_service,
            )
        except EmptyMessageError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=str(exc),
            ) from exc
        if result.reply is not None:
            await asyncio.sleep(SIMULATED_PROCESSING_DELAY_SECONDS)
        return SendMessageResponse(
            reply=result.reply,
            guidance=result.triage.guidance,
            triage_status=result.triage.status.value,
            signals=[signal.value for signal in result.triage.signals],
        )

    return router
