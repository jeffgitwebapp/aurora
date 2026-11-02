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
    SourceReferenceResponse,
)
from aurora_backend.contexts.conversation.services.chat_response.port import (
    ChatResponseGenerator,
)
from aurora_backend.contexts.conversation.services.knowledge.port import (
    KnowledgeRetriever,
    KnowledgeUnavailableError,
)
from aurora_backend.contexts.conversation.services.triage.port import TriageEvaluator

SIMULATED_PROCESSING_DELAY_SECONDS = 5


def create_send_message_router(
    *,
    triage_service: TriageEvaluator,
    knowledge_service: KnowledgeRetriever,
    chat_response_service: ChatResponseGenerator,
) -> APIRouter:
    router = APIRouter(prefix="/api/chat", tags=["conversa"])

    @router.post("/messages", response_model=SendMessageResponse)
    async def send_message(request: SendMessageRequest) -> SendMessageResponse:
        try:
            result = await handle_send_message(
                request.message,
                triage_service=triage_service,
                knowledge_service=knowledge_service,
                chat_response_service=chat_response_service,
            )
        except EmptyMessageError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=str(exc),
            ) from exc
        except KnowledgeUnavailableError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="O serviço de informações está indisponível no momento.",
            ) from exc

        knowledge = result.knowledge
        if knowledge is not None:
            await asyncio.sleep(SIMULATED_PROCESSING_DELAY_SECONDS)
        return SendMessageResponse(
            reply=result.reply,
            guidance=result.triage.guidance,
            triage_status=result.triage.status.value,
            signals=[signal.value for signal in result.triage.signals],
            knowledge_status=knowledge.status.value if knowledge is not None else None,
            sources=[
                SourceReferenceResponse(
                    id=source.id,
                    title=source.title,
                    locator=source.locator,
                    publisher=source.publisher,
                    url=source.url,
                    version=source.version,
                )
                for source in (knowledge.sources if knowledge is not None else ())
            ],
            demo=True,
        )

    return router
