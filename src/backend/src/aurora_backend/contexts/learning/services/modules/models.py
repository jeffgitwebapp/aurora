"""Modelos de domínio dos módulos de psicoeducação."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceCitation:
    title: str
    locator: str
    url: str


@dataclass(frozen=True)
class ModuleSection:
    title: str
    paragraphs: tuple[str, ...]
    source: SourceCitation | None = None


@dataclass(frozen=True)
class LearningModule:
    id: str
    title: str
    topic: str
    sections: tuple[ModuleSection, ...]
    in_preparation: bool
    demo: bool = True


class ModuleNotFoundError(LookupError):
    """Módulo inexistente no catálogo."""
