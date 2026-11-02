"""Adaptador HTTP da feature PlanoSeguranca."""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field

from aurora_backend.contexts.accounts.features.auth import bearer_token
from aurora_backend.contexts.accounts.services.accounts.models import (
    InvalidSafetyPlanError,
    InvalidSessionError,
    SafetyPlan,
    TrustedContact,
)
from aurora_backend.contexts.accounts.services.accounts.port import Accounts

Authorization = Annotated[str | None, Header()]


class TrustedContactBody(BaseModel):
    name: str = Field(max_length=60)
    phone: str = Field(max_length=20)


class SafetyPlanRequest(BaseModel):
    contacts: list[TrustedContactBody] = Field(max_length=5)
    notes: str = Field(max_length=4000)


class SafetyPlanResponse(BaseModel):
    contacts: list[TrustedContactBody]
    notes: str
    updated_at: str | None
    demo: bool


def _response(plan: SafetyPlan) -> SafetyPlanResponse:
    return SafetyPlanResponse(
        contacts=[
            TrustedContactBody(name=contact.name, phone=contact.phone) for contact in plan.contacts
        ],
        notes=plan.notes,
        updated_at=(
            datetime.fromtimestamp(plan.updated_at, tz=UTC).isoformat()
            if plan.updated_at is not None
            else None
        ),
        demo=True,
    )


def create_safety_plan_router(*, account_service: Accounts) -> APIRouter:
    router = APIRouter(prefix="/api/account/safety-plan", tags=["contas"])

    @router.get("", response_model=SafetyPlanResponse)
    async def get_plan(authorization: Authorization = None) -> SafetyPlanResponse:
        try:
            plan = await account_service.get_safety_plan(bearer_token(authorization))
        except InvalidSessionError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
        return _response(plan)

    @router.put("", response_model=SafetyPlanResponse)
    async def save_plan(
        request: SafetyPlanRequest,
        authorization: Authorization = None,
    ) -> SafetyPlanResponse:
        try:
            plan = await account_service.save_safety_plan(
                bearer_token(authorization),
                tuple(
                    TrustedContact(name=contact.name, phone=contact.phone)
                    for contact in request.contacts
                ),
                request.notes,
            )
        except InvalidSessionError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
        except InvalidSafetyPlanError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=str(exc),
            ) from exc
        return _response(plan)

    return router
