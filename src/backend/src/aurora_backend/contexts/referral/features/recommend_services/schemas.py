"""Contratos HTTP da feature RecomendarServicos."""

from typing import Literal

from pydantic import BaseModel, Field


class RecommendServicesRequest(BaseModel):
    city: str = Field(max_length=80)
    state: str = Field(max_length=2)


class ServiceOptionResponse(BaseModel):
    id: str
    name: str
    priority: int
    category: str
    description: str
    contact: str | None
    hours: str | None
    cost: str | None
    last_verified_at: str | None
    demo: bool


class RecommendServicesResponse(BaseModel):
    status: Literal["found", "no_verified_result"]
    city: str
    state: str
    services: list[ServiceOptionResponse]
    demo: bool
