"""Adaptador HTTP da feature ConsultarModulos."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from aurora_backend.contexts.learning.services.modules.models import (
    LearningModule,
    ModuleNotFoundError,
)
from aurora_backend.contexts.learning.services.modules.port import ModuleCatalog


class SourceCitationResponse(BaseModel):
    title: str
    locator: str
    url: str


class ModuleSectionResponse(BaseModel):
    title: str
    paragraphs: list[str]
    source: SourceCitationResponse | None


class ModuleSummaryResponse(BaseModel):
    id: str
    title: str
    topic: str
    section_count: int
    in_preparation: bool
    demo: bool


class ModuleListResponse(BaseModel):
    modules: list[ModuleSummaryResponse]


class ModuleResponse(ModuleSummaryResponse):
    sections: list[ModuleSectionResponse]


def _summary(module: LearningModule) -> dict[str, object]:
    return {
        "id": module.id,
        "title": module.title,
        "topic": module.topic,
        "section_count": len(module.sections),
        "in_preparation": module.in_preparation,
        "demo": module.demo,
    }


def create_browse_modules_router(*, module_catalog: ModuleCatalog) -> APIRouter:
    router = APIRouter(prefix="/api/learning/modules", tags=["aprendizagem"])

    @router.get("", response_model=ModuleListResponse)
    async def list_modules() -> ModuleListResponse:
        modules = await module_catalog.list_modules()
        return ModuleListResponse(
            modules=[ModuleSummaryResponse(**_summary(module)) for module in modules]
        )

    @router.get("/{module_id}", response_model=ModuleResponse)
    async def get_module(module_id: str) -> ModuleResponse:
        try:
            module = await module_catalog.get_module(module_id)
        except ModuleNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        return ModuleResponse(
            **_summary(module),
            sections=[
                ModuleSectionResponse(
                    title=section.title,
                    paragraphs=list(section.paragraphs),
                    source=(
                        SourceCitationResponse(
                            title=section.source.title,
                            locator=section.source.locator,
                            url=section.source.url,
                        )
                        if section.source is not None
                        else None
                    ),
                )
                for section in module.sections
            ],
        )

    return router
