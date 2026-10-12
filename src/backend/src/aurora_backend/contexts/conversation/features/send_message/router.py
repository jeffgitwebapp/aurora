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

router = APIRouter(prefix="/api/chat", tags=["conversa"])
RESPONSE_DELAY_SECONDS = 10


@router.post("/messages", response_model=SendMessageResponse)
async def send_message(request: SendMessageRequest) -> SendMessageResponse:
    try:
        reply = handle_send_message(request.message)
    except EmptyMessageError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
    await asyncio.sleep(RESPONSE_DELAY_SECONDS)
    return SendMessageResponse(reply=reply)
