"""Contratos HTTP da feature EnviarMensagem."""

from pydantic import BaseModel


class SendMessageRequest(BaseModel):
    message: str


class SendMessageResponse(BaseModel):
    reply: str
