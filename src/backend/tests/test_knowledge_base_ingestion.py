"""Versão vigente, ingestão estrita e snapshot da base curada (F1 da v1.2)."""

import json
from pathlib import Path

import pytest

from aurora_backend.contexts.conversation.services.knowledge_base.ingestion import (
    KnowledgeIngestionError,
    build_latest_snapshot,
    build_snapshot,
)
from aurora_backend.contexts.conversation.services.knowledge_base.models import (
    CitableKind,
    ReviewStatus,
)
from aurora_backend.contexts.conversation.services.knowledge_base.repository import (
    SNAPSHOT_PATH,
    KnowledgeBaseRepository,
)
from aurora_backend.contexts.conversation.services.knowledge_base.versioning import (
    KnowledgeBaseVersionError,
    latest_base_dir,
    source_hash,
)

BASE_ROOT = Path(__file__).resolve().parents[3] / "docs" / "aurora-base-rag"

VALID_DOCUMENT = """---
id: lei-teste
titulo: "Lei de teste"
tipo: legislacao
orgao: Órgão de teste
versao: "Redação de teste"
url_oficial: https://exemplo.gov.br/lei
temas: [teste]
status: pendente  # comentário
---

# Lei de teste

## art. 1º — título da seção
<!-- chunk: lei-teste#art1 -->
- **Localizador:** Lei de teste, art. 1º
- **Temas:** teste, exemplo
- **Texto oficial:**

  > Art. 1º Texto **oficial** da lei.
  >
  > Parágrafo único. Segunda linha.

- **Resumo em linguagem simples (rascunho):** Resumo simples.
- **Perguntas de teste:** "Pergunta um?" · "Pergunta dois?"
- **Atenção (escopo):** não opinar sobre o caso.

## seção de guia
<!-- chunk: lei-teste#guia -->
- **Localizador:** p. 3
- **Temas:** guia
- **Trecho da fonte:** [colar — p. 3]
- **Resumo em linguagem simples (rascunho):** Resumo do guia.
"""


def write(base: Path, relative: str, content: str) -> None:
    path = base / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_latest_base_dir_uses_numeric_order_and_ignores_other_folders(tmp_path: Path) -> None:
    for name in ("v0.03", "v0.10", "v0.04", "v1.2-rascunho", "antigo"):
        (tmp_path / name).mkdir()

    assert latest_base_dir(tmp_path).name == "v0.10"


def test_latest_base_dir_without_versions_fails(tmp_path: Path) -> None:
    (tmp_path / "rascunho").mkdir()

    with pytest.raises(KnowledgeBaseVersionError):
        latest_base_dir(tmp_path)


def test_newer_version_replaces_older_one(tmp_path: Path) -> None:
    write(tmp_path, "v0.03/legislacao/lei.md", VALID_DOCUMENT)
    write(tmp_path, "v0.04/legislacao/lei.md", VALID_DOCUMENT.replace("lei-teste", "lei-nova"))

    snapshot = build_latest_snapshot(tmp_path)

    assert snapshot.kb_version == "v0.04"
    assert {chunk.id for chunk in snapshot.chunks} == {"lei-nova#art1", "lei-nova#guia"}


def test_source_hash_ignores_line_endings(tmp_path: Path) -> None:
    write(tmp_path, "lf/a.md", "linha 1\nlinha 2\n")
    (tmp_path / "crlf").mkdir()
    (tmp_path / "crlf" / "a.md").write_bytes(b"linha 1\r\nlinha 2\r\n")

    assert source_hash(tmp_path / "lf") == source_hash(tmp_path / "crlf")


def test_ingestion_parses_fields_and_prefers_official_text(tmp_path: Path) -> None:
    write(tmp_path, "legislacao/lei.md", VALID_DOCUMENT)

    chunk = build_snapshot(tmp_path).chunks[0]

    assert chunk.id == "lei-teste#art1"
    assert chunk.section == "art. 1º — título da seção"
    assert chunk.locator == "Lei de teste, art. 1º"
    assert chunk.citable_kind is CitableKind.OFFICIAL_TEXT
    assert chunk.citable_text == "Art. 1º Texto oficial da lei.\n\nParágrafo único. Segunda linha."
    assert chunk.plain_summary == "Resumo simples."
    assert chunk.test_questions == ("Pergunta um?", "Pergunta dois?")
    assert chunk.scope_notes == ("não opinar sobre o caso.",)
    assert chunk.topics == ("teste", "exemplo")
    assert chunk.status is ReviewStatus.PENDING
    assert chunk.publisher == "Órgão de teste"
    assert not chunk.internal


def test_placeholder_excerpt_falls_back_to_curated_summary(tmp_path: Path) -> None:
    write(tmp_path, "guias/guia.md", VALID_DOCUMENT)

    chunk = build_snapshot(tmp_path).chunks[1]

    assert chunk.citable_kind is CitableKind.CURATED_SUMMARY
    assert chunk.citable_text == "Resumo do guia."
    assert "[colar" not in chunk.citable_text


def test_internal_documents_are_kept_but_flagged(tmp_path: Path) -> None:
    write(
        tmp_path,
        "guias/interno.md",
        VALID_DOCUMENT.replace("status: pendente", "uso: INTERNO — não indexar\nstatus: pendente"),
    )

    assert all(chunk.internal for chunk in build_snapshot(tmp_path).chunks)


def test_catalog_readme_and_candidate_sources_are_excluded(tmp_path: Path) -> None:
    write(tmp_path, "legislacao/lei.md", VALID_DOCUMENT)
    write(tmp_path, "legislacao/README.md", "<!-- chunk: id#localizador -->")
    write(tmp_path, "catalogo/servicos.md", VALID_DOCUMENT.replace("lei-teste", "catalogo"))
    write(tmp_path, "guias/fontes-candidatas.md", VALID_DOCUMENT.replace("lei-teste", "cand"))

    assert {chunk.doc_id for chunk in build_snapshot(tmp_path).chunks} == {"lei-teste"}


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (("---\nid", "id"), "cabeçalho YAML"),
        (("url_oficial: https://", "url_oficial: http://"), "https://"),
        (("status: pendente", "status: desconhecido"), "status"),
        (("- **Localizador:** Lei de teste, art. 1º\n", ""), "Localizador"),
    ],
)
def test_ingestion_fails_loudly_on_unexpected_format(
    tmp_path: Path, change: tuple[str, str], message: str
) -> None:
    write(tmp_path, "legislacao/lei.md", VALID_DOCUMENT.replace(*change, 1))

    with pytest.raises(KnowledgeIngestionError, match=message):
        build_snapshot(tmp_path)


def test_duplicated_chunk_ids_fail(tmp_path: Path) -> None:
    write(tmp_path, "a/lei.md", VALID_DOCUMENT)
    write(tmp_path, "b/lei.md", VALID_DOCUMENT)

    with pytest.raises(KnowledgeIngestionError, match="duplicados"):
        build_snapshot(tmp_path)


def test_snapshot_matches_latest_base() -> None:
    """Gate da CI: nova versão ou mudança na base exige regenerar o snapshot.

    Corrigir com:  uv run python scripts/build_knowledge_snapshot.py
    """
    latest = latest_base_dir(BASE_ROOT)
    stored = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))

    assert stored["kb_version"] == latest.name
    assert stored["source_hash"] == source_hash(latest)
    assert stored == json.loads(json.dumps(build_snapshot(latest).to_dict()))


def test_repository_separates_searchable_and_internal_chunks() -> None:
    repository = KnowledgeBaseRepository.from_file()
    searchable = repository.searchable_chunks(allow_pending=True)

    assert searchable
    assert not any(chunk.internal for chunk in searchable)
    assert repository.internal_chunks()
    assert all(chunk.url.startswith("https://") for chunk in searchable)
    assert repository.searchable_chunks(allow_pending=False) == ()
