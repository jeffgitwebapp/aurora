"""Saudação, agradecimento e despedida sem LLM (U-11)."""

from aurora_backend.contexts.conversation.services.small_talk.port import SmallTalkDetector
from aurora_backend.contexts.conversation.services.small_talk.service import (
    ConversationKind,
    SmallTalkReply,
    SmallTalkService,
)

__all__ = ["ConversationKind", "SmallTalkDetector", "SmallTalkReply", "SmallTalkService"]
