"""Adaptador HTTP da feature RecomendarServicos."""

from fastapi import APIRouter, HTTPException, status

from aurora_backend.contexts.referral.features.recommend_services.handler import (
    InvalidLocationError,
    handle_recommend_services,
)
from aurora_backend.contexts.referral.features.recommend_services.schemas import (
    RecommendServicesRequest,
    RecommendServicesResponse,
    ServiceOptionResponse,
)
from aurora_backend.contexts.referral.services.catalog.port import (
    CatalogUnavailableError,
    ServiceCatalog,
)


def create_recommend_services_router(*, catalog_service: ServiceCatalog) -> APIRouter:
    router = APIRouter(prefix="/api/referral", tags=["encaminhamento"])

    @router.post("/recommendations", response_model=RecommendServicesResponse)
    async def recommend_services(
        request: RecommendServicesRequest,
    ) -> RecommendServicesResponse:
        try:
            result = await handle_recommend_services(
                request.city,
                request.state,
                catalog_service=catalog_service,
            )
        except InvalidLocationError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=str(exc),
            ) from exc
        except CatalogUnavailableError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="O catálogo de serviços está indisponível no momento.",
            ) from exc

        return RecommendServicesResponse(
            status=result.status.value,
            city=" ".join(request.city.split()),
            state=request.state.strip().upper(),
            services=[
                ServiceOptionResponse(
                    id=service.id,
                    name=service.name,
                    priority=position,
                    category=service.category,
                    description=service.description,
                    contact=service.contact,
                    hours=service.hours,
                    cost=service.cost,
                    last_verified_at=service.last_verified_at,
                    demo=service.demo,
                )
                for position, service in enumerate(result.services, start=1)
            ],
            demo=result.demo,
        )

    return router
