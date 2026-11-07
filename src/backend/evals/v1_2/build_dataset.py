"""Gera o dataset de avaliação da v1.2 a partir da versão vigente da base RAG.

Uso (em src/backend):  uv run python evals/v1_2/build_dataset.py

- Lê a maior pasta docs/aurora-base-rag/vX.YY (ordem numérica) e extrai as
  "Perguntas de teste" de cada chunk como gabarito de recuperação.
- Gera variantes sem acento e em maiúsculas (exigência D-03).
- Acrescenta os casos manuais de cases_manual.jsonl (adversariais, fora da base, risco).
- Escreve dataset.jsonl ao lado deste arquivo.

As perguntas de teste são gabarito: não devem entrar no índice de busca (plano §5.8).
"""

import json
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
BASE_ROOT = REPO_ROOT / "docs" / "aurora-base-rag"
VERSION_PATTERN = re.compile(r"^v(\d+)\.(\d+)$")
CHUNK_MARKER = re.compile(r"<!--\s*chunk:\s*(\S+)\s*-->")
TEST_QUESTIONS_LINE = re.compile(r"^\s*-\s*\*\*Perguntas de teste:\*\*(.*)$")
QUOTED = re.compile(r"[\"“]([^\"”]+)[\"”]")
EXCLUDED_FILES = {"README.md", "fontes-candidatas.md"}
EXCLUDED_DIRS = {"catalogo"}


def latest_base_dir() -> Path:
    candidates = [
        (int(match.group(1)), int(match.group(2)), path)
        for path in BASE_ROOT.iterdir()
        if path.is_dir() and (match := VERSION_PATTERN.match(path.name))
    ]
    if not candidates:
        raise SystemExit(f"Nenhuma pasta vX.YY em {BASE_ROOT}")
    return max(candidates)[2]


def strip_accents(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")


def extract_retrieval_cases(base_dir: Path) -> list[dict]:
    cases: list[dict] = []
    for path in sorted(base_dir.rglob("*.md")):
        if path.name in EXCLUDED_FILES or EXCLUDED_DIRS & set(path.relative_to(base_dir).parts):
            continue
        current_chunk: str | None = None
        for line in path.read_text(encoding="utf-8").splitlines():
            if marker := CHUNK_MARKER.search(line):
                current_chunk = marker.group(1)
                continue
            match = TEST_QUESTIONS_LINE.match(line)
            if not match or current_chunk is None:
                continue
            for question in QUOTED.findall(match.group(1)):
                cases.append(
                    {
                        "category": "retrieval",
                        "question": question.strip(),
                        "expected": {"outcome": "found", "chunk_ids": [current_chunk]},
                        "source": f"{path.relative_to(base_dir).as_posix()}#{current_chunk}",
                    }
                )
    return merge_duplicate_questions(cases)


def merge_duplicate_questions(cases: list[dict]) -> list[dict]:
    merged: dict[str, dict] = {}
    for case in cases:
        key = strip_accents(case["question"]).casefold()
        if key in merged:
            chunk_ids = merged[key]["expected"]["chunk_ids"]
            for chunk_id in case["expected"]["chunk_ids"]:
                if chunk_id not in chunk_ids:
                    chunk_ids.append(chunk_id)
        else:
            merged[key] = case
    return list(merged.values())


def variants(cases: list[dict]) -> list[dict]:
    generated: list[dict] = []
    for case in cases:
        no_accents = strip_accents(case["question"])
        for label, text in (("sem_acento", no_accents.lower()), ("maiusculas", no_accents.upper())):
            generated.append(
                {
                    **case,
                    "category": "retrieval_variant",
                    "variant": label,
                    "question": text,
                    "expected": {
                        **case["expected"],
                        "chunk_ids": list(case["expected"]["chunk_ids"]),
                    },
                }
            )
    return generated


def manual_cases() -> list[dict]:
    path = HERE / "cases_manual.jsonl"
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def main() -> None:
    base_dir = latest_base_dir()
    retrieval = extract_retrieval_cases(base_dir)
    rows = retrieval + variants(retrieval) + manual_cases()
    for index, row in enumerate(rows, start=1):
        row["id"] = f"v12-{index:04d}"
        row["kb_version"] = base_dir.name
    output = HERE / "dataset.jsonl"
    output.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
    )
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["category"]] = counts.get(row["category"], 0) + 1
    print(f"Base {base_dir.name}: {len(rows)} casos em {output.relative_to(REPO_ROOT)}")
    for category, total in sorted(counts.items()):
        print(f"  {category}: {total}")


if __name__ == "__main__":
    main()
