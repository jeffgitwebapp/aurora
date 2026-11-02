"""Valida a localização informada e consulta o catálogo de serviços."""

from aurora_backend.contexts.referral.services.catalog.models import RecommendationResult
from aurora_backend.contexts.referral.services.catalog.port import ServiceCatalog

BRAZILIAN_STATES = frozenset(
    {
        "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA",
        "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
    }
)  # fmt: skip


class InvalidLocationError(ValueError):
    """Cidade vazia ou UF inexistente."""


async def handle_recommend_services(
    city: str,
    state: str,
    *,
    catalog_service: ServiceCatalog,
) -> RecommendationResult:
    normalized_city = " ".join(city.split())
    normalized_state = state.strip().upper()
    if not normalized_city or normalized_state not in BRAZILIAN_STATES:
        raise InvalidLocationError("Informe a cidade e uma UF válida.")
    return await catalog_service.recommend(city=normalized_city, state=normalized_state)
