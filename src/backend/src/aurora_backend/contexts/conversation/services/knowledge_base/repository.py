"""Acesso ao snapshot versionado da base de conhecimento."""

import json
from pathlib import Path

from aurora_backend.contexts.conversation.services.knowledge_base.models import (
    KnowledgeBaseSnapshot,
    KnowledgeChunk,
    ReviewStatus,
)

SNAPSHOT_PATH = Path(__file__).resolve().parent / "data" / "knowledge_base.json"


class KnowledgeBaseRepository:
    """Chunks do snapshot por id; também guarda os chunks internos (apoio ao prompt)."""

    def __init__(self, snapshot: KnowledgeBaseSnapshot):
        self.snapshot = snapshot
        self._by_id = {chunk.id: chunk for chunk in snapshot.chunks}

    @classmethod
    def from_file(cls, path: Path = SNAPSHOT_PATH) -> "KnowledgeBaseRepository":
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(KnowledgeBaseSnapshot.from_dict(data))

    @property
    def kb_version(self) -> str:
        return self.snapshot.kb_version

    def get(self, chunk_id: str) -> KnowledgeChunk | None:
        return self._by_id.get(chunk_id)

    def searchable_chunks(self, *, allow_pending: bool) -> tuple[KnowledgeChunk, ...]:
        return tuple(
            chunk
            for chunk in self.snapshot.chunks
            if not chunk.internal and (allow_pending or chunk.status is ReviewStatus.APPROVED)
        )

    def internal_chunks(self) -> tuple[KnowledgeChunk, ...]:
        return tuple(chunk for chunk in self.snapshot.chunks if chunk.internal)
