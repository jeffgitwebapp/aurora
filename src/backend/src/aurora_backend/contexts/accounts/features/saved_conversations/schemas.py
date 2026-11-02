"""Contratos HTTP da feature ConversasSalvas."""

from typing import Literal

from pydantic import BaseModel, Field


class SavedMessageBody(BaseModel):
    role: Literal["user", "assistant"]
    text: str = Field(max_length=4000)


class SaveConversationRequest(BaseModel):
    messages: list[SavedMessageBody] = Field(max_length=200)


class ConversationSummaryResponse(BaseModel):
    id: str
    saved_at: str
    message_count: int
    excerpt: str


class ConversationListResponse(BaseModel):
    conversations: list[ConversationSummaryResponse]
    demo: bool


class ConversationResponse(BaseModel):
    id: str
    saved_at: str
    messages: list[SavedMessageBody]
    demo: bool
