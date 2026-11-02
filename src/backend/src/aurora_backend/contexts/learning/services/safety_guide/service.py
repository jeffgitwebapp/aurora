"""Guia de segurança com seções de demonstração no protótipo."""

from aurora_backend.contexts.learning.services.safety_guide.models import (
    GuideSection,
    SafetyGuideContent,
)

_PLACEHOLDER = (
    "Conteúdo em preparação — demonstração. Esta seção ainda não tem texto aprovado "
    "por especialistas da rede de proteção."
)

# Decisão da usuária em 02/11/2026: títulos neutros com placeholder até haver
# conteúdo aprovado; orientações de segurança não são inventadas no protótipo.
_SECTIONS = (
    GuideSection(title="Pensar na sua segurança", paragraphs=(_PLACEHOLDER,)),
    GuideSection(title="Documentos e itens importantes", paragraphs=(_PLACEHOLDER,)),
    GuideSection(title="Pessoas e serviços de apoio", paragraphs=(_PLACEHOLDER,)),
)


class SafetyGuideService:
    """Serve o guia estático atual; o conteúdo aprovado substituirá os placeholders."""

    async def content(self) -> SafetyGuideContent:
        return SafetyGuideContent(sections=_SECTIONS, in_preparation=True)
