"""Porta para um serviço substituível de ofertas de conteúdo."""

from typing import Protocol

from aurora_backend.contexts.conversation.services.content_offer.models import ContentOffer


class ContentOfferProvider(Protocol):
    async def suggest(self, message: str) -> ContentOffer | None: ...
