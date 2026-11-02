"""Adaptador HTTP da feature LerGuiaSeguranca."""

from fastapi import APIRouter
from pydantic import BaseModel

from aurora_backend.contexts.learning.services.safety_guide.port import SafetyGuide


class GuideSectionResponse(BaseModel):
    title: str
    paragraphs: list[str]


class SafetyGuideResponse(BaseModel):
    sections: list[GuideSectionResponse]
    in_preparation: bool
    demo: bool


def create_read_safety_guide_router(*, safety_guide: SafetyGuide) -> APIRouter:
    router = APIRouter(prefix="/api/learning/safety-guide", tags=["aprendizagem"])

    @router.get("", response_model=SafetyGuideResponse)
    async def read_guide() -> SafetyGuideResponse:
        content = await safety_guide.content()
        return SafetyGuideResponse(
            sections=[
                GuideSectionResponse(title=section.title, paragraphs=list(section.paragraphs))
                for section in content.sections
            ],
            in_preparation=content.in_preparation,
            demo=content.demo,
        )

    return router
