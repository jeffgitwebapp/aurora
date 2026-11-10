"""Adaptador HTTP da feature EnviarMensagem."""

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
    ChatResponseUnavailableError,
)
from aurora_backend.contexts.conversation.services.content_offer.port import (
    ContentOfferProvider,
)
from aurora_backend.contexts.conversation.services.guardrail.models import ScopeDecision
from aurora_backend.contexts.conversation.services.guardrail.port import (
    GuardrailUnavailableError,
    ScopeGuardrail,
)
from aurora_backend.contexts.conversation.services.knowledge.port import (
    KnowledgeRetriever,
    KnowledgeUnavailableError,
)
from aurora_backend.contexts.conversation.services.small_talk.port import SmallTalkDetector
from aurora_backend.contexts.conversation.services.triage.port import TriageEvaluator

_SCOPE_STATUS = {
    ScopeDecision.ALLOW: "allowed",
    ScopeDecision.OUT_OF_SCOPE: "out_of_scope",
}


def create_send_message_router(
    *,
    triage_service: TriageEvaluator,
    guardrail_service: ScopeGuardrail,
    offer_service: ContentOfferProvider,
    knowledge_service: KnowledgeRetriever,
    chat_response_service: ChatResponseGenerator,
    small_talk_service: SmallTalkDetector | None = None,
) -> APIRouter:
    router = APIRouter(prefix="/api/chat", tags=["conversa"])

    @router.post("/messages", response_model=SendMessageResponse)
    async def send_message(request: SendMessageRequest) -> SendMessageResponse:
        try:
            result = await handle_send_message(
                request.message,
                triage_service=triage_service,
                guardrail_service=guardrail_service,
                offer_service=offer_service,
                knowledge_service=knowledge_service,
                chat_response_service=chat_response_service,
                small_talk_service=small_talk_service,
            )
        except EmptyMessageError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=str(exc),
            ) from exc
        except (
            GuardrailUnavailableError,
            KnowledgeUnavailableError,
            ChatResponseUnavailableError,
        ) as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="O serviço de informações está indisponível no momento.",
            ) from exc

        guardrail = result.guardrail
        knowledge = result.knowledge
        return SendMessageResponse(
            reply=result.reply,
            guidance=result.triage.guidance,
            triage_status=result.triage.status.value,
            signals=[signal.value for signal in result.triage.signals],
            scope_status=_SCOPE_STATUS[guardrail.decision] if guardrail is not None else None,
            out_of_scope_category=(
                guardrail.category.value
                if guardrail is not None and guardrail.category is not None
                else None
            ),
            offer=result.offer.value if result.offer is not None else None,
            conversation=(result.conversation.value if result.conversation is not None else None),
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
