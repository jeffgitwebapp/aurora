"""Localiza a versão vigente da base (maior pasta vX.YY) e calcula seu hash."""

import hashlib
import re
from pathlib import Path

VERSION_PATTERN = re.compile(r"^v(\d+)\.(\d+)$")


class KnowledgeBaseVersionError(RuntimeError):
    """Nenhuma pasta de versão válida encontrada."""


def parse_version(name: str) -> tuple[int, int] | None:
    match = VERSION_PATTERN.match(name)
    if match is None:
        return None
    return int(match.group(1)), int(match.group(2))


def latest_base_dir(root: Path) -> Path:
    """Maior pasta vX.YY em ordem numérica; as demais são ignoradas."""
    versions = [
        (version, path)
        for path in root.iterdir()
        if path.is_dir() and (version := parse_version(path.name)) is not None
    ]
    if not versions:
        raise KnowledgeBaseVersionError(f"Nenhuma pasta no padrão vX.YY em {root}")
    return max(versions)[1]


def source_hash(base_dir: Path) -> str:
    """SHA-256 dos Markdown da versão, com fins de linha normalizados (CRLF → LF)."""
    digest = hashlib.sha256()
    for path in sorted(base_dir.rglob("*.md"), key=lambda item: item.as_posix()):
        content = path.read_bytes().replace(b"\r\n", b"\n")
        digest.update(path.relative_to(base_dir).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(content)
        digest.update(b"\0")
    return digest.hexdigest()
