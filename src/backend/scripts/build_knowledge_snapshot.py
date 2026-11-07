"""Relê a versão vigente da base (maior docs/aurora-base-rag/vX.YY) e regenera o snapshot.

Uso (em src/backend):  uv run python scripts/build_knowledge_snapshot.py
Rodar sempre que a base mudar ou uma nova versão for adicionada; a CI falha se o
snapshot estiver desatualizado (tests/test_knowledge_base_snapshot.py).
"""

import json
from pathlib import Path

from aurora_backend.contexts.conversation.services.knowledge_base.ingestion import (
    build_latest_snapshot,
)
from aurora_backend.contexts.conversation.services.knowledge_base.repository import (
    SNAPSHOT_PATH,
)

BASE_ROOT = Path(__file__).resolve().parents[3] / "docs" / "aurora-base-rag"


def main() -> None:
    snapshot = build_latest_snapshot(BASE_ROOT)
    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_PATH.write_text(
        json.dumps(snapshot.to_dict(), ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    searchable = sum(1 for chunk in snapshot.chunks if not chunk.internal)
    kinds: dict[str, int] = {}
    for chunk in snapshot.chunks:
        if not chunk.internal:
            kinds[chunk.citable_kind.value] = kinds.get(chunk.citable_kind.value, 0) + 1
    print(
        f"Base {snapshot.kb_version} ({snapshot.source_hash[:12]}): {len(snapshot.chunks)} chunks"
    )
    print(f"  pesquisáveis: {searchable} {kinds}")
    print(f"  internos: {len(snapshot.chunks) - searchable}")


if __name__ == "__main__":
    main()
