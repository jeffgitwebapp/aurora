"""Adaptador HTTP da feature ExcluirConta."""

from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Response, status

from aurora_backend.contexts.accounts.features.auth import bearer_token
from aurora_backend.contexts.accounts.services.accounts.models import InvalidSessionError
from aurora_backend.contexts.accounts.services.accounts.port import Accounts


def create_delete_account_router(*, account_service: Accounts) -> APIRouter:
    router = APIRouter(prefix="/api/accounts", tags=["contas"])

    @router.delete("/current", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_account(authorization: Annotated[str | None, Header()] = None) -> Response:
        try:
            await account_service.delete_account(bearer_token(authorization))
        except InvalidSessionError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc),
            ) from exc
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return router
