"""Catálogo de serviços com registros fictícios de demonstração no protótipo."""

from aurora_backend.contexts.referral.services.catalog.models import (
    MAX_RECOMMENDATIONS,
    RecommendationResult,
    RecommendationStatus,
    ServiceOption,
    ServiceTier,
)
from aurora_backend.shared.fixture_text import (
    normalize_fixture_sentence,
)

_CATEGORY_LABELS = {
    ServiceTier.PUBLIC_BODY: "Órgão público",
    ServiceTier.SPECIALIZED_SERVICE: "Serviço especializado",
    ServiceTier.CIVIL_SOCIETY: "Sociedade civil",
    ServiceTier.VOLUNTEER: "Voluntariado",
}


def _demo_services(city_id: str) -> tuple[ServiceOption, ...]:
    # Registros fictícios aprovados pela usuária em 02/11/2026: sem contato,
    # horário, custo ou data de verificação reais. Fora de ordem de propósito,
    # para que a hierarquia seja aplicada pelo serviço.
    return (
        ServiceOption(
            id=f"{city_id}-sociedade-civil",
            name="Organização da sociedade civil — exemplo",
            tier=ServiceTier.CIVIL_SOCIETY,
            category=_CATEGORY_LABELS[ServiceTier.CIVIL_SOCIETY],
            description="Exemplo de grupo de apoio e acolhimento a mulheres.",
        ),
        ServiceOption(
            id=f"{city_id}-defensoria",
            name="Defensoria Pública do Estado — exemplo",
            tier=ServiceTier.PUBLIC_BODY,
            category=_CATEGORY_LABELS[ServiceTier.PUBLIC_BODY],
            description="Exemplo de orientação jurídica pública.",
        ),
        ServiceOption(
            id=f"{city_id}-centro-referencia",
            name="Centro de Referência de Atendimento à Mulher — exemplo",
            tier=ServiceTier.SPECIALIZED_SERVICE,
            category=_CATEGORY_LABELS[ServiceTier.SPECIALIZED_SERVICE],
            description="Exemplo de atendimento psicossocial e orientação especializada.",
        ),
    )


_CATALOG_FIXTURES: dict[tuple[str, str], tuple[ServiceOption, ...]] = {
    ("Recife", "PE"): _demo_services("recife-pe"),
    ("São Paulo", "SP"): _demo_services("sao-paulo-sp"),
}

_NORMALIZED_CATALOG = {
    (normalize_fixture_sentence(city), state.upper()): services
    for (city, state), services in _CATALOG_FIXTURES.items()
}


class CatalogService:
    """Consulta o catálogo fictício atual; não confirma serviços reais nem contatos."""

    async def recommend(self, *, city: str, state: str) -> RecommendationResult:
        services = _NORMALIZED_CATALOG.get((normalize_fixture_sentence(city), state.upper()))
        if not services:
            return RecommendationResult(status=RecommendationStatus.NO_VERIFIED_RESULT)
        prioritized = sorted(services, key=lambda service: service.tier)
        return RecommendationResult(
            status=RecommendationStatus.FOUND,
            services=tuple(prioritized[:MAX_RECOMMENDATIONS]),
        )
