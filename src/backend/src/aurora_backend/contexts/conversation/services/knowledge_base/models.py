"""Modelos da base de conhecimento curada e do snapshot versionado."""

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any


class ReviewStatus(StrEnum):
    APPROVED = "aprovado"
    PENDING = "pendente"


class CitableKind(StrEnum):
    """Origem do texto citável de um chunk."""

    OFFICIAL_TEXT = "official_text"
    SOURCE_EXCERPT = "source_excerpt"
    DATA = "data"
    CURATED_SUMMARY = "curated_summary"


@dataclass(frozen=True)
class KnowledgeChunk:
    id: str
    doc_id: str
    kind: str
    title: str
    section: str
    locator: str
    citable_text: str
    citable_kind: CitableKind
    plain_summary: str | None
    scope_notes: tuple[str, ...]
    topics: tuple[str, ...]
    test_questions: tuple[str, ...]
    url: str
    version: str | None
    publisher: str
    status: ReviewStatus
    internal: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "KnowledgeChunk":
        return cls(
            **{
                **data,
                "citable_kind": CitableKind(data["citable_kind"]),
                "status": ReviewStatus(data["status"]),
                "scope_notes": tuple(data["scope_notes"]),
                "topics": tuple(data["topics"]),
                "test_questions": tuple(data["test_questions"]),
            }
        )


@dataclass(frozen=True)
class KnowledgeBaseSnapshot:
    kb_version: str
    source_hash: str
    chunks: tuple[KnowledgeChunk, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "kb_version": self.kb_version,
            "source_hash": self.source_hash,
            "chunks": [chunk.to_dict() for chunk in self.chunks],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "KnowledgeBaseSnapshot":
        return cls(
            kb_version=data["kb_version"],
            source_hash=data["source_hash"],
            chunks=tuple(KnowledgeChunk.from_dict(chunk) for chunk in data["chunks"]),
        )
