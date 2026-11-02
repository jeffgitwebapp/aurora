"""Serviço de limite de escopo com frases-fixture estáticas no protótipo."""

from aurora_backend.contexts.conversation.services.guardrail.models import (
    GuardrailResult,
    OutOfScopeCategory,
    ScopeDecision,
)
from aurora_backend.shared.fixture_text import (
    normalize_fixture_sentence,
)

# Frases de teste aprovadas pela usuária em 02/11/2026; casos limítrofes e
# gatilhos reais dependem de revisão jurídica, clínica e de produto.
_OUT_OF_SCOPE_FIXTURES: dict[OutOfScopeCategory, tuple[str, ...]] = {
    OutOfScopeCategory.DIAGNOSIS: ("Eu tenho depressão?",),
    OutOfScopeCategory.PRESCRIPTION: ("Que remédio devo tomar?",),
    OutOfScopeCategory.INDIVIDUAL_LEGAL_OPINION: (
        "O que acontece no meu caso?",
        "Devo denunciar meu marido?",
    ),
}

_NORMALIZED_OUT_OF_SCOPE_FIXTURES = {
    normalize_fixture_sentence(phrase): category
    for category, phrases in _OUT_OF_SCOPE_FIXTURES.items()
    for phrase in phrases
}


class GuardrailService:
    """Compara o pedido inteiro com as fixtures atuais; não classifica pedidos reais."""

    async def check_request(self, message: str) -> GuardrailResult:
        category = _NORMALIZED_OUT_OF_SCOPE_FIXTURES.get(normalize_fixture_sentence(message))
        if category is None:
            return GuardrailResult(decision=ScopeDecision.ALLOW)
        return GuardrailResult(decision=ScopeDecision.OUT_OF_SCOPE, category=category)
