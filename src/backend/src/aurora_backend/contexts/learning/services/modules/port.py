"""Porta para um catálogo substituível de módulos."""

from typing import Protocol

from aurora_backend.contexts.learning.services.modules.models import LearningModule


class ModuleCatalog(Protocol):
    async def list_modules(self) -> tuple[LearningModule, ...]: ...

    async def get_module(self, module_id: str) -> LearningModule: ...
