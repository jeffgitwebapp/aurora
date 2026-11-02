"""Contratos HTTP da feature EnviarMensagem."""

from typing import Literal

from pydantic import BaseModel


class SendMessageRequest(BaseModel):
    message: str


class SourceReferenceResponse(BaseModel):
    id: str
    title: str
    locator: str
    publisher: str
    url: str
    version: str | None


class SendMessageResponse(BaseModel):
    reply: str | None
    guidance: str | None
    triage_status: Literal["acute", "no_acute_signal", "indeterminate"]
    signals: list[
        Literal[
            "suicidal_ideation",
            "ongoing_assault",
            "death_threat",
            "weapon_present",
        ]
    ]
    knowledge_status: Literal["found", "no_source"] | None
    sources: list[SourceReferenceResponse]
    demo: bool
