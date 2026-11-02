"""Adaptador HTTP da feature Diario."""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Response, status
from pydantic import BaseModel, Field

from aurora_backend.contexts.accounts.features.auth import bearer_token
from aurora_backend.contexts.accounts.services.accounts.models import (
    InvalidJournalEntryError,
    InvalidSessionError,
    JournalEntry,
    JournalEntryNotFoundError,
)
from aurora_backend.contexts.accounts.services.accounts.port import Accounts

Authorization = Annotated[str | None, Header()]


class JournalEntryRequest(BaseModel):
    date: str = Field(max_length=10)
    time: str | None = Field(default=None, max_length=5)
    description: str = Field(max_length=4000)


class JournalEntryResponse(BaseModel):
    id: str
    date: str
    time: str | None
    description: str
    updated_at: str


class JournalListResponse(BaseModel):
    entries: list[JournalEntryResponse]
    demo: bool


def _response(entry: JournalEntry) -> JournalEntryResponse:
    return JournalEntryResponse(
        id=entry.id,
        date=entry.entry_date,
        time=entry.entry_time,
        description=entry.description,
        updated_at=datetime.fromtimestamp(entry.updated_at, tz=UTC).isoformat(),
    )


def create_journal_router(*, account_service: Accounts) -> APIRouter:
    router = APIRouter(prefix="/api/account/journal", tags=["contas"])

    def translate(exc: Exception) -> HTTPException:
        if isinstance(exc, InvalidSessionError):
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
        if isinstance(exc, JournalEntryNotFoundError):
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
        return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc))

    async def save(
        entry_id: str | None,
        request: JournalEntryRequest,
        authorization: str | None,
    ) -> JournalEntryResponse:
        try:
            entry = await account_service.save_journal_entry(
                bearer_token(authorization),
                entry_id,
                request.date,
                request.time or None,
                request.description,
            )
        except (
            InvalidSessionError,
            InvalidJournalEntryError,
            JournalEntryNotFoundError,
        ) as exc:
            raise translate(exc) from exc
        return _response(entry)

    @router.get("", response_model=JournalListResponse)
    async def list_entries(authorization: Authorization = None) -> JournalListResponse:
        try:
            entries = await account_service.list_journal(bearer_token(authorization))
        except InvalidSessionError as exc:
            raise translate(exc) from exc
        return JournalListResponse(entries=[_response(entry) for entry in entries], demo=True)

    @router.post("", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED)
    async def create_entry(
        request: JournalEntryRequest,
        authorization: Authorization = None,
    ) -> JournalEntryResponse:
        return await save(None, request, authorization)

    @router.put("/{entry_id}", response_model=JournalEntryResponse)
    async def update_entry(
        entry_id: str,
        request: JournalEntryRequest,
        authorization: Authorization = None,
    ) -> JournalEntryResponse:
        return await save(entry_id, request, authorization)

    @router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_entry(entry_id: str, authorization: Authorization = None) -> Response:
        try:
            await account_service.delete_journal_entry(bearer_token(authorization), entry_id)
        except (InvalidSessionError, JournalEntryNotFoundError) as exc:
            raise translate(exc) from exc
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return router
