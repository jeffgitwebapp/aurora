"""Adaptador HTTP da feature CriarConta."""

from fastapi import APIRouter, HTTPException, status

from aurora_backend.contexts.accounts.features.schemas import (
    CredentialsRequest,
    SessionResponse,
)
from aurora_backend.contexts.accounts.services.accounts.models import (
    InvalidRegistrationError,
    NicknameTakenError,
)
from aurora_backend.contexts.accounts.services.accounts.port import Accounts


def create_register_account_router(*, account_service: Accounts) -> APIRouter:
    router = APIRouter(prefix="/api/accounts", tags=["contas"])

    @router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
    async def register_account(request: CredentialsRequest) -> SessionResponse:
        try:
            session = await account_service.register(request.nickname, request.password)
        except InvalidRegistrationError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=str(exc),
            ) from exc
        except NicknameTakenError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
        return SessionResponse(nickname=session.nickname, token=session.token, demo=True)

    return router
