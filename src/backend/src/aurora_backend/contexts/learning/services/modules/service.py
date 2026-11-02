"""Catálogo de módulos com conteúdo de demonstração no protótipo."""

from aurora_backend.contexts.learning.services.modules.models import (
    LearningModule,
    ModuleNotFoundError,
    ModuleSection,
    SourceCitation,
)
from aurora_backend.shared.legal_sources import (
    CODIGO_PENAL_ART_147_B,
    MARIA_DA_PENHA_ART_7_II,
    LegalExcerpt,
)

# Decisão da usuária em 02/11/2026: temas do backlog (E6-US1/US2); somente o
# primeiro módulo tem conteúdo, formado pelas citações legais já aprovadas no C-04.
# Os demais ficam como placeholders explícitos, sem afirmações inventadas.
_PLACEHOLDER = (
    "Conteúdo em preparação — demonstração. Este módulo ainda não tem texto "
    "aprovado por especialistas."
)


def _legal_section(title: str, excerpt: LegalExcerpt) -> ModuleSection:
    return ModuleSection(
        title=title,
        paragraphs=(f"“{excerpt.text}”",),
        source=SourceCitation(title=excerpt.title, locator=excerpt.locator, url=excerpt.url),
    )


def _placeholder_module(module_id: str, title: str, topic: str) -> LearningModule:
    return LearningModule(
        id=module_id,
        title=title,
        topic=topic,
        sections=(
            ModuleSection(title="Parte 1", paragraphs=(_PLACEHOLDER,)),
            ModuleSection(title="Parte 2", paragraphs=(_PLACEHOLDER,)),
        ),
        in_preparation=True,
    )


_MODULES = (
    LearningModule(
        id="o-que-e-violencia-psicologica",
        title="O que é violência psicológica",
        topic="Reconhecer",
        sections=(
            _legal_section("O que diz a Lei Maria da Penha", MARIA_DA_PENHA_ART_7_II),
            _legal_section("O que diz o Código Penal", CODIGO_PENAL_ART_147_B),
        ),
        in_preparation=False,
    ),
    _placeholder_module("ciclo-do-abuso", "Ciclo do abuso", "Reconhecer"),
    _placeholder_module("gaslighting", "Gaslighting", "Reconhecer"),
    _placeholder_module("isolamento-como-controle", "Isolamento como controle", "Reconhecer"),
    _placeholder_module("impactos-na-saude-mental", "Impactos na saúde mental", "Cuidar de si"),
    _placeholder_module("lei-maria-da-penha", "O que diz a Lei Maria da Penha", "Direitos"),
    _placeholder_module("medidas-protetivas", "Medidas protetivas", "Direitos"),
    _placeholder_module(
        "boletim-de-ocorrencia", "Como funciona um boletim de ocorrência", "Direitos"
    ),
)
_MODULES_BY_ID = {module.id: module for module in _MODULES}


class ModuleCatalogService:
    """Serve o catálogo estático atual; o painel de conteúdo o substituirá (E11)."""

    async def list_modules(self) -> tuple[LearningModule, ...]:
        return _MODULES

    async def get_module(self, module_id: str) -> LearningModule:
        module = _MODULES_BY_ID.get(module_id)
        if module is None:
            raise ModuleNotFoundError("Módulo não encontrado.")
        return module
