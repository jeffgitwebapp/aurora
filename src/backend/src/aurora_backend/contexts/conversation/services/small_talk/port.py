"""Porta do reconhecimento de saudação, agradecimento e despedida."""

from typing import Protocol

from aurora_backend.contexts.conversation.services.small_talk.service import SmallTalkReply


class SmallTalkDetector(Protocol):
    async def respond(self, message: str) -> SmallTalkReply | None: ...
