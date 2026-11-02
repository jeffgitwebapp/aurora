"""Contratos HTTP compartilhados pelas features de Contas."""

from pydantic import BaseModel, Field


class CredentialsRequest(BaseModel):
    nickname: str = Field(max_length=30)
    password: str = Field(max_length=128)


class SessionResponse(BaseModel):
    nickname: str
    token: str
    demo: bool


class CurrentAccountResponse(BaseModel):
    nickname: str
    demo: bool
