"""Todo pacote importado pelo código da aplicação precisa estar nas dependências de produção.

A imagem Docker instala só as dependências de produção (`uv sync --no-dev`); os testes
rodam com as de desenvolvimento. Este teste impede que um import de pacote só de dev
(como `httpx`) passe nos testes e derrube o backend em produção.
"""

import ast
import re
import sys
from importlib import metadata
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src" / "aurora_backend"
PROJECT = "aurora-backend"
# Exceções conscientes: módulos usados só em desenvolvimento (script de snapshot e testes).
INGESTION = "contexts/conversation/services/knowledge_base/ingestion.py"
DEV_ONLY_IMPORTS = {"yaml": {INGESTION}}


def _canonical(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _requirement_name(requirement: str) -> str | None:
    if "extra ==" in requirement:
        return None
    return _canonical(re.split(r"[\s<>=!~;\[(]", requirement, maxsplit=1)[0])


def production_distributions() -> set[str]:
    pending = [_canonical(PROJECT)]
    seen: set[str] = set()
    while pending:
        name = pending.pop()
        if name in seen:
            continue
        seen.add(name)
        try:
            requirements = metadata.requires(name) or []
        except metadata.PackageNotFoundError:
            continue
        pending.extend(n for r in requirements if (n := _requirement_name(r)))
    return seen


def imported_top_level_modules() -> dict[str, set[str]]:
    modules: dict[str, set[str]] = {}
    for path in SRC.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                names = [node.module]
            else:
                continue
            for name in names:
                top = name.split(".")[0]
                if top not in sys.stdlib_module_names and top != "aurora_backend":
                    modules.setdefault(top, set()).add(path.relative_to(SRC).as_posix())
    return modules


def test_application_imports_only_production_dependencies() -> None:
    allowed = production_distributions()
    module_to_distributions = metadata.packages_distributions()

    offenders = {
        module: sorted(files)
        for module, files in imported_top_level_modules().items()
        if not {_canonical(d) for d in module_to_distributions.get(module, [])} & allowed
        and not files <= DEV_ONLY_IMPORTS.get(module, set())
    }

    assert offenders == {}, (
        "Pacotes importados pela aplicação que não estão nas dependências de produção "
        f"(adicione em [project.dependencies] ou remova o import): {offenders}"
    )


def test_guard_detects_dev_only_packages() -> None:
    allowed = production_distributions()

    assert "google-genai" in allowed
    assert "httpx2" in allowed
    assert "pytest" not in allowed
    assert "httpx" not in allowed


def test_dev_only_ingestion_is_never_imported_by_the_application() -> None:
    importers = [
        path.relative_to(SRC).as_posix()
        for path in SRC.rglob("*.py")
        if path.relative_to(SRC).as_posix() != INGESTION
        and "knowledge_base.ingestion" in path.read_text(encoding="utf-8")
    ]

    assert importers == []
