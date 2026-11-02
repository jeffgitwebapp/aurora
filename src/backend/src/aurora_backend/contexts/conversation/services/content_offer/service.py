"""Ofertas de conteúdo acionadas por frases-fixture no protótipo."""

from aurora_backend.contexts.conversation.services.content_offer.models import ContentOffer
from aurora_backend.shared.fixture_text import normalize_fixture_sentence

# Frase de teste aprovada pela usuária em 02/11/2026 (E8-US4). Critérios reais de
# "quando o contexto indicar" dependem de especialistas e não são inferidos aqui.
_OFFER_FIXTURES = {
    normalize_fixture_sentence("Quero pensar na minha segurança"): ContentOffer.SAFETY_GUIDE,
}


class ContentOfferService:
    """Sugere conteúdo opcional só para as frases-fixture atuais."""

    async def suggest(self, message: str) -> ContentOffer | None:
        return _OFFER_FIXTURES.get(normalize_fixture_sentence(message))
