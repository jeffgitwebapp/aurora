"""Adaptador HTTP da feature GerenciarSessao."""

from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Response, status

from aurora_backend.contexts.accounts.features.auth import bearer_token
from aurora_backend.contexts.accounts.features.schemas import (
    CredentialsRequest,
    CurrentAccountResponse,
    SessionResponse,
)
from aurora_backend.contexts.accounts.services.accounts.models import (
    AccountLockedError,
    InvalidCredentialsError,
    InvalidSessionError,
)
from aurora_backend.contexts.accounts.services.accounts.port import Accounts


def create_manage_session_router(*, account_service: Accounts) -> APIRouter:
    router = APIRouter(prefix="/api/sessions", tags=["contas"])

    @router.post("", response_model=SessionResponse)
    async def login(request: CredentialsRequest) -> SessionResponse:
        try:
            session = await account_service.login(request.nickname, request.password)
        except InvalidCredentialsError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc),
            ) from exc
        except AccountLockedError as exc:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=str(exc),
            ) from exc
        return SessionResponse(nickname=session.nickname, token=session.token, demo=True)

    @router.get("/current", response_model=CurrentAccountResponse)
    async def current(
        authorization: Annotated[str | None, Header()] = None,
    ) -> CurrentAccountResponse:
        try:
            nickname = await account_service.current(bearer_token(authorization))
        except InvalidSessionError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc),
            ) from exc
        return CurrentAccountResponse(nickname=nickname, demo=True)

    @router.delete("/current", status_code=status.HTTP_204_NO_CONTENT)
    async def logout(authorization: Annotated[str | None, Header()] = None) -> Response:
        await account_service.logout(bearer_token(authorization))
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return router
