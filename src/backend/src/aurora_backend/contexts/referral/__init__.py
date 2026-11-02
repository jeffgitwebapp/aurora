"""Bounded context Encaminhamento."""

from fastapi import APIRouter

from aurora_backend.contexts.referral.features.recommend_services.router import (
    create_recommend_services_router,
)
from aurora_backend.contexts.referral.services.catalog.port import ServiceCatalog


def create_routers(*, catalog_service: ServiceCatalog) -> tuple[APIRouter, ...]:
    return (create_recommend_services_router(catalog_service=catalog_service),)


__all__ = ["create_routers"]
