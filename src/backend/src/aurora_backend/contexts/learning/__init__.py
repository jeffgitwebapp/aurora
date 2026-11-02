"""Bounded context Aprendizagem (módulos de psicoeducação e guia de segurança)."""

from fastapi import APIRouter

from aurora_backend.contexts.learning.features.browse_modules.router import (
    create_browse_modules_router,
)
from aurora_backend.contexts.learning.features.read_safety_guide.router import (
    create_read_safety_guide_router,
)
from aurora_backend.contexts.learning.services.modules.port import ModuleCatalog
from aurora_backend.contexts.learning.services.safety_guide.port import SafetyGuide


def create_routers(
    *,
    module_catalog: ModuleCatalog,
    safety_guide: SafetyGuide,
) -> tuple[APIRouter, ...]:
    return (
        create_browse_modules_router(module_catalog=module_catalog),
        create_read_safety_guide_router(safety_guide=safety_guide),
    )


__all__ = ["create_routers"]
