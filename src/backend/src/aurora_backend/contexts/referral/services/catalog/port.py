"""Porta para um catálogo substituível de serviços da rede de apoio."""

from typing import Protocol

from aurora_backend.contexts.referral.services.catalog.models import RecommendationResult


class CatalogUnavailableError(RuntimeError):
    """Falha técnica do catálogo; distinta de ausência de serviço na cidade."""


class ServiceCatalog(Protocol):
    async def recommend(self, *, city: str, state: str) -> RecommendationResult: ...
