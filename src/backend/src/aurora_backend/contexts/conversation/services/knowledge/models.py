"""Modelos de domínio para trechos recuperados e suas fontes."""

from dataclasses import dataclass
from enum import StrEnum


class KnowledgeStatus(StrEnum):
    FOUND = "found"
    NO_SOURCE = "no_source"


@dataclass(frozen=True)
class SourceReference:
    id: str
    title: str
    locator: str
    publisher: str
    url: str
    version: str | None = None


@dataclass(frozen=True)
class KnowledgePassage:
    text: str
    source: SourceReference


@dataclass(frozen=True)
class KnowledgeResult:
    status: KnowledgeStatus
    passages: tuple[KnowledgePassage, ...] = ()
    demo: bool = True

    def __post_init__(self) -> None:
        if self.status is KnowledgeStatus.FOUND and not self.passages:
            raise ValueError("Resultado com fonte exige ao menos um trecho.")
        if self.status is KnowledgeStatus.NO_SOURCE and self.passages:
            raise ValueError("Resultado sem fonte não pode conter trechos.")

    @property
    def sources(self) -> tuple[SourceReference, ...]:
        unique: dict[str, SourceReference] = {}
        for passage in self.passages:
            unique.setdefault(passage.source.id, passage.source)
        return tuple(unique.values())
