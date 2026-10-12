"""Bounded context Conversa.

Fronteira pública do contexto: expõe apenas os routers das features que o compõem.
"""

from fastapi import APIRouter

from aurora_backend.contexts.conversation.features.send_message.router import (
    router as send_message_router,
)

routers: tuple[APIRouter, ...] = (send_message_router,)

__all__ = ["routers"]
