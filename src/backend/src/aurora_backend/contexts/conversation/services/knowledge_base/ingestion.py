"""Ingestão estrita da base Markdown em snapshot (uso em desenvolvimento e testes).

Depende de PyYAML (grupo dev); o app em produção lê apenas o snapshot JSON.
"""

import re
import unicodedata
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from aurora_backend.contexts.conversation.services.knowledge_base.models import (
    CitableKind,
    KnowledgeBaseSnapshot,
    KnowledgeChunk,
    ReviewStatus,
)
from aurora_backend.contexts.conversation.services.knowledge_base.versioning import (
    latest_base_dir,
    source_hash,
)

EXCLUDED_DIRS = frozenset({"catalogo"})
EXCLUDED_FILES = frozenset({"README.md", "fontes-candidatas.md"})
CHUNK_MARKER = re.compile(r"<!--\s*chunk:\s*(\S+)\s*-->")
FIELD_LINE = re.compile(r"^- \*\*(?P<label>[^*]+?)\*\*(?P<rest>.*)$")
QUOTED = re.compile(r"[\"“]([^\"”]+)[\"”]")
PLACEHOLDER = re.compile(r"\[colar\b", re.IGNORECASE)


class KnowledgeIngestionError(ValueError):
    """A base não está no formato esperado; nada é ingerido pela metade."""


def build_latest_snapshot(root: Path) -> KnowledgeBaseSnapshot:
    return build_snapshot(latest_base_dir(root))


def build_snapshot(base_dir: Path) -> KnowledgeBaseSnapshot:
    chunks: list[KnowledgeChunk] = []
    for path in sorted(base_dir.rglob("*.md"), key=lambda item: item.as_posix()):
        relative = path.relative_to(base_dir)
        if path.name in EXCLUDED_FILES or EXCLUDED_DIRS & set(relative.parts):
            continue
        chunks.extend(_parse_document(path, relative.as_posix()))
    ids = [chunk.id for chunk in chunks]
    duplicated = sorted({chunk_id for chunk_id in ids if ids.count(chunk_id) > 1})
    if duplicated:
        raise KnowledgeIngestionError(f"Chunks duplicados: {', '.join(duplicated)}")
    if not chunks:
        raise KnowledgeIngestionError(f"Nenhum chunk encontrado em {base_dir}")
    return KnowledgeBaseSnapshot(
        kb_version=base_dir.name,
        source_hash=source_hash(base_dir),
        chunks=tuple(chunks),
    )


def _parse_document(path: Path, relative: str) -> list[KnowledgeChunk]:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    front, body = _split_front_matter(text, relative)
    doc_id = _required(front, "id", relative)
    title = _required(front, "titulo", relative)
    url = _required(front, "url_oficial", relative)
    if not url.startswith("https://"):
        raise KnowledgeIngestionError(f"{relative}: url_oficial precisa ser https://")
    publisher = _text(front.get("orgao")) or _publisher_from_authorship(front)
    if not publisher:
        raise KnowledgeIngestionError(f"{relative}: sem orgao nem autoria")
    status = _status(front, relative)
    internal = _text(front.get("uso")).upper().startswith("INTERNO")
    document = {
        "doc_id": doc_id,
        "kind": _text(front.get("tipo")) or "desconhecido",
        "title": title,
        "url": url,
        "version": _text(front.get("versao")) or None,
        "publisher": publisher,
        "status": status,
        "internal": internal,
    }
    return [
        _build_chunk(chunk_id, section, lines, document, relative)
        for chunk_id, section, lines in _split_chunks(body)
    ]


def _split_front_matter(text: str, relative: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        raise KnowledgeIngestionError(f"{relative}: cabeçalho YAML ausente")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise KnowledgeIngestionError(f"{relative}: cabeçalho YAML sem fechamento")
    try:
        front = yaml.safe_load(text[4:end]) or {}
    except yaml.YAMLError as exc:
        raise KnowledgeIngestionError(f"{relative}: YAML inválido ({exc})") from exc
    if not isinstance(front, dict):
        raise KnowledgeIngestionError(f"{relative}: cabeçalho YAML não é um mapeamento")
    return front, text[end + 5 :]


def _split_chunks(body: str) -> list[tuple[str, str, list[str]]]:
    """Cada chunk vai do marcador até o próximo título ## ou marcador."""
    chunks: list[tuple[str, str, list[str]]] = []
    section = ""
    current: tuple[str, str, list[str]] | None = None
    for line in body.split("\n"):
        if line.startswith("## "):
            section = line[3:].strip()
            current = None
            continue
        if marker := CHUNK_MARKER.search(line):
            current = (marker.group(1), section, [])
            chunks.append(current)
            continue
        if current is not None:
            current[2].append(line)
    return chunks


def _parse_fields(lines: list[str]) -> list[tuple[str, str]]:
    fields: list[tuple[str, list[str]]] = []
    for line in lines:
        if match := FIELD_LINE.match(line):
            label = match.group("label").strip().rstrip(":").strip()
            rest = match.group("rest")
            if not match.group("label").rstrip().endswith(":"):
                rest = rest.split(":", 1)[1] if ":" in rest else ""
            fields.append((label, [rest.strip()]))
        elif fields:
            fields[-1][1].append(_strip_quote(line))
    return [(label, _join(parts)) for label, parts in fields]


def _build_chunk(
    chunk_id: str,
    section: str,
    lines: list[str],
    document: dict[str, Any],
    relative: str,
) -> KnowledgeChunk:
    values: dict[str, list[str]] = {}
    for label, value in _parse_fields(lines):
        values.setdefault(_field_key(label), []).append(value)

    locator = _first(values, "localizador")
    if not locator:
        raise KnowledgeIngestionError(f"{relative}#{chunk_id}: sem Localizador")
    summary = _first(values, "resumo") or None
    citable_text, citable_kind = _citable(values, summary, f"{relative}#{chunk_id}")
    topics = tuple(topic.strip() for topic in _first(values, "temas").split(",") if topic.strip())
    questions = tuple(
        question.strip()
        for value in values.get("perguntas de teste", [])
        for question in QUOTED.findall(value)
    )
    scope_notes = tuple(
        value for key in ("atencao", "uso no aurora") for value in values.get(key, []) if value
    )
    return KnowledgeChunk(
        id=chunk_id,
        section=section,
        locator=locator,
        citable_text=citable_text,
        citable_kind=citable_kind,
        plain_summary=summary,
        scope_notes=scope_notes,
        topics=topics,
        test_questions=questions,
        **document,
    )


def _citable(
    values: dict[str, list[str]], summary: str | None, where: str
) -> tuple[str, CitableKind]:
    for key, kind in (
        ("texto oficial", CitableKind.OFFICIAL_TEXT),
        ("trecho da fonte", CitableKind.SOURCE_EXCERPT),
        ("dados", CitableKind.DATA),
    ):
        value = _first(values, key)
        if value and not PLACEHOLDER.search(value):
            return value, kind
    if summary:
        return summary, CitableKind.CURATED_SUMMARY
    raise KnowledgeIngestionError(f"{where}: sem texto citável nem resumo")


def _field_key(label: str) -> str:
    base = _ascii_lower(label.split("(", 1)[0]).strip()
    if base.startswith("atencao"):
        return "atencao"
    if base.startswith("resumo"):
        return "resumo"
    if base.startswith("dados"):
        return "dados"
    return base


def _strip_quote(line: str) -> str:
    stripped = line.strip()
    if stripped.startswith(">"):
        return stripped[1:].strip()
    return stripped


def _join(parts: list[str]) -> str:
    """Junta as linhas de um campo preservando quebras de parágrafo."""
    paragraphs: list[str] = []
    buffer: list[str] = []
    for part in parts:
        if part:
            buffer.append(part)
        elif buffer:
            paragraphs.append(" ".join(buffer))
            buffer = []
    if buffer:
        paragraphs.append(" ".join(buffer))
    return "\n\n".join(paragraphs).replace("**", "").strip()


def _first(values: dict[str, list[str]], key: str) -> str:
    return next((value for value in values.get(key, []) if value), "")


def _required(front: dict[str, Any], key: str, relative: str) -> str:
    value = _text(front.get(key))
    if not value:
        raise KnowledgeIngestionError(f"{relative}: campo obrigatório '{key}' ausente")
    return value


def _status(front: dict[str, Any], relative: str) -> ReviewStatus:
    raw = _ascii_lower(_text(front.get("status")))
    for status in ReviewStatus:
        if raw.startswith(status.value):
            return status
    raise KnowledgeIngestionError(f"{relative}: status desconhecido '{raw}'")


def _publisher_from_authorship(front: dict[str, Any]) -> str:
    parts = [_text(front.get("autoria")), _text(front.get("periodico"))]
    return " — ".join(part for part in parts if part)


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, date):
        return value.isoformat()
    return str(value).strip()


def _ascii_lower(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn").casefold()
