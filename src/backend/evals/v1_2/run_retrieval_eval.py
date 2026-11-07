"""Mede a recuperação da v1.2 sobre o dataset (F1/F3).

Uso (em src/backend):
  uv run python evals/v1_2/run_retrieval_eval.py                          # só BM25, sem rede
  uv run --env-file .env python evals/v1_2/run_retrieval_eval.py --llm    # BM25 + seleção (D-12)

Com --llm, o provedor vem do ambiente (D-13): AURORA_LLM_PROVIDER=gemini|claude,
AURORA_LLM_MODEL e a credencial (GEMINI_API_KEY ou ANTHROPIC_API_KEY). Cada pergunta de
recuperação e fora da base gera uma chamada; --rpm limita as chamadas por minuto
(plano gratuito do Gemini). Use só os dados sintéticos do dataset.
"""

import argparse
import asyncio
import json
import time
from pathlib import Path

from aurora_backend.contexts.conversation.services.knowledge.models import KnowledgeStatus
from aurora_backend.contexts.conversation.services.knowledge.port import (
    KnowledgeUnavailableError,
)
from aurora_backend.contexts.conversation.services.knowledge_base.repository import (
    KnowledgeBaseRepository,
)
from aurora_backend.contexts.conversation.services.knowledge_base.selector import (
    LanguageModelChunkSelector,
)
from aurora_backend.contexts.conversation.services.knowledge_base.service import (
    KnowledgeBaseService,
)
from aurora_backend.contexts.conversation.services.language_model.factory import (
    LanguageModelSettings,
    create_language_model,
)

DATASET = Path(__file__).resolve().parent / "dataset.jsonl"


def load(categories: set[str]) -> list[dict]:
    rows = [json.loads(line) for line in DATASET.read_text(encoding="utf-8").splitlines()]
    return [row for row in rows if row["category"] in categories]


def bm25_report(service: KnowledgeBaseService) -> None:
    retrieval = load({"retrieval"})
    variants = load({"retrieval_variant"})
    for k in (1, 5, 30):
        for name, rows in (("retrieval", retrieval), ("variantes", variants)):
            hits = sum(
                any(c.id in r["expected"]["chunk_ids"] for c, _ in service.rank(r["question"])[:k])
                for r in rows
            )
            print(f"BM25 recall@{k} {name}: {hits}/{len(rows)} = {hits / len(rows):.1%}")


async def llm_report(repository: KnowledgeBaseRepository, rpm: int) -> None:
    settings = LanguageModelSettings.from_env()
    selector = LanguageModelChunkSelector(create_language_model(settings))
    service = KnowledgeBaseService(repository, selector=selector)
    label = f"{settings.provider}/{settings.model}"
    interval = 60 / rpm if rpm > 0 else 0
    last_call = 0.0

    async def retrieve(question: str) -> tuple[KnowledgeStatus | None, set[str]]:
        nonlocal last_call
        wait = interval - (time.monotonic() - last_call)
        if wait > 0:
            await asyncio.sleep(wait)
        last_call = time.monotonic()
        try:
            result = await service.retrieve(question)
        except KnowledgeUnavailableError:
            return None, set()
        return result.status, {p.source.id for p in result.passages}

    retrieval = load({"retrieval"})
    out_of_base = load({"out_of_base"})
    hits = failures = limited = 0
    for row in retrieval:
        status, ids = await retrieve(row["question"])
        failures += status is None
        hits += bool(ids & set(row["expected"]["chunk_ids"]))
    for row in out_of_base:
        status, _ = await retrieve(row["question"])
        failures += status is None
        limited += status is KnowledgeStatus.NO_SOURCE
    print(f"{label} recall@5 retrieval: {hits}/{len(retrieval)} = {hits / len(retrieval):.1%}")
    print(f"{label} fora da base -> sem fonte (M5): {limited}/{len(out_of_base)}")
    print(f"{label} falhas técnicas (503): {failures}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--llm", action="store_true", help="mede também a seleção pelo LLM")
    parser.add_argument("--rpm", type=int, default=10, help="chamadas por minuto (0 = sem limite)")
    args = parser.parse_args()

    repository = KnowledgeBaseRepository.from_file()
    print(f"Base {repository.kb_version}")
    bm25_report(KnowledgeBaseService(repository, score_threshold=0))
    if args.llm:
        calls = len(load({"retrieval", "out_of_base"}))
        minutes = calls / args.rpm if args.rpm > 0 else 0
        print(f"\n{calls} chamadas ao LLM (~{minutes:.0f} min com --rpm {args.rpm}).")
        asyncio.run(llm_report(repository, args.rpm))


if __name__ == "__main__":
    main()
