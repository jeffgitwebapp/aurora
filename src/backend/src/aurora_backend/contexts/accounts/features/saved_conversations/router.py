"""Adaptador HTTP da feature ConversasSalvas."""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Response, status

from aurora_backend.contexts.accounts.features.auth import bearer_token
from aurora_backend.contexts.accounts.features.saved_conversations.schemas import (
    ConversationListResponse,
    ConversationResponse,
    ConversationSummaryResponse,
    SaveConversationRequest,
    SavedMessageBody,
)
from aurora_backend.contexts.accounts.services.accounts.models import (
    ConversationNotFoundError,
    ConversationSummary,
    InvalidConversationError,
    InvalidSessionError,
    SavedMessage,
)
from aurora_backend.contexts.accounts.services.accounts.port import Accounts

Authorization = Annotated[str | None, Header()]


def _iso(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, tz=UTC).isoformat()


def _summary(summary: ConversationSummary) -> ConversationSummaryResponse:
    return ConversationSummaryResponse(
        id=summary.id,
        saved_at=_iso(summary.saved_at),
        message_count=summary.message_count,
        excerpt=summary.excerpt,
    )


def create_saved_conversations_router(*, account_service: Accounts) -> APIRouter:
    router = APIRouter(prefix="/api/account/conversations", tags=["contas"])

    def unauthorized(exc: Exception) -> HTTPException:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))

    def not_found(exc: Exception) -> HTTPException:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    @router.post(
        "",
        response_model=ConversationSummaryResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def save_conversation(
        request: SaveConversationRequest,
        authorization: Authorization = None,
    ) -> ConversationSummaryResponse:
        messages = tuple(
            SavedMessage(role=message.role, text=message.text) for message in request.messages
        )
        try:
            summary = await account_service.save_conversation(bearer_token(authorization), messages)
        except InvalidSessionError as exc:
            raise unauthorized(exc) from exc
        except InvalidConversationError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=str(exc),
            ) from exc
        return _summary(summary)

    @router.get("", response_model=ConversationListResponse)
    async def list_conversations(authorization: Authorization = None) -> ConversationListResponse:
        try:
            summaries = await account_service.list_conversations(bearer_token(authorization))
        except InvalidSessionError as exc:
            raise unauthorized(exc) from exc
        return ConversationListResponse(
            conversations=[_summary(summary) for summary in summaries],
            demo=True,
        )

    @router.get("/{conversation_id}", response_model=ConversationResponse)
    async def get_conversation(
        conversation_id: str,
        authorization: Authorization = None,
    ) -> ConversationResponse:
        try:
            conversation = await account_service.get_conversation(
                bearer_token(authorization), conversation_id
            )
        except InvalidSessionError as exc:
            raise unauthorized(exc) from exc
        except ConversationNotFoundError as exc:
            raise not_found(exc) from exc
        return ConversationResponse(
            id=conversation.id,
            saved_at=_iso(conversation.saved_at),
            messages=[
                SavedMessageBody(role=message.role, text=message.text)
                for message in conversation.messages
            ],
            demo=True,
        )

    @router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_conversation(
        conversation_id: str,
        authorization: Authorization = None,
    ) -> Response:
        try:
            await account_service.delete_conversation(bearer_token(authorization), conversation_id)
        except InvalidSessionError as exc:
            raise unauthorized(exc) from exc
        except ConversationNotFoundError as exc:
            raise not_found(exc) from exc
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return router
