"""Adaptador HTTP da feature ProgressoModulos."""

from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field

from aurora_backend.contexts.accounts.features.auth import bearer_token
from aurora_backend.contexts.accounts.services.accounts.models import (
    InvalidModuleProgressError,
    InvalidSessionError,
    ModuleProgress,
)
from aurora_backend.contexts.accounts.services.accounts.port import Accounts

Authorization = Annotated[str | None, Header()]


class ModuleProgressRequest(BaseModel):
    section: int = Field(ge=0)
    completed: bool


class ModuleProgressResponse(BaseModel):
    module_id: str
    section: int
    completed: bool


class ModuleProgressListResponse(BaseModel):
    progress: list[ModuleProgressResponse]


def _response(progress: ModuleProgress) -> ModuleProgressResponse:
    return ModuleProgressResponse(
        module_id=progress.module_id,
        section=progress.section,
        completed=progress.completed,
    )


def create_module_progress_router(*, account_service: Accounts) -> APIRouter:
    router = APIRouter(prefix="/api/account/module-progress", tags=["contas"])

    @router.get("", response_model=ModuleProgressListResponse)
    async def list_progress(authorization: Authorization = None) -> ModuleProgressListResponse:
        try:
            progress = await account_service.list_module_progress(bearer_token(authorization))
        except InvalidSessionError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
        return ModuleProgressListResponse(progress=[_response(item) for item in progress])

    @router.put("/{module_id}", response_model=ModuleProgressResponse)
    async def save_progress(
        module_id: str,
        request: ModuleProgressRequest,
        authorization: Authorization = None,
    ) -> ModuleProgressResponse:
        try:
            progress = await account_service.save_module_progress(
                bearer_token(authorization),
                module_id,
                request.section,
                request.completed,
            )
        except InvalidSessionError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
        except InvalidModuleProgressError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=str(exc),
            ) from exc
        return _response(progress)

    return router
