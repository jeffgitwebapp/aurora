"""Mede a recuperação da v1.2 sobre o dataset (F1/F3).

Uso (em src/backend):
  uv run python evals/v1_2/run_retrieval_eval.py            # só BM25, sem rede
  uv run python evals/v1_2/run_retrieval_eval.py --claude   # BM25 + seleção pelo Claude (D-12)

Com --claude, cada pergunta de recuperação e fora da base gera uma chamada à API
(ANTHROPIC_API_KEY ou perfil `ant auth login`); o custo estimado é exibido antes.
"""

import argparse
import asyncio
import json
import os
from pathlib import Path

import anthropic

from aurora_backend.contexts.conversation.services.knowledge.models import KnowledgeStatus
from aurora_backend.contexts.conversation.services.knowledge_base.repository import (
    KnowledgeBaseRepository,
)
from aurora_backend.contexts.conversation.services.knowledge_base.selector import (
    ClaudeChunkSelector,
)
from aurora_backend.contexts.conversation.services.knowledge_base.service import (
    KnowledgeBaseService,
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


async def claude_report(repository: KnowledgeBaseRepository, model: str) -> None:
    selector = ClaudeChunkSelector(anthropic.AsyncAnthropic(), model=model)
    service = KnowledgeBaseService(repository, selector=selector)
    retrieval = load({"retrieval"})
    out_of_base = load({"out_of_base"})
    hits = 0
    for row in retrieval:
        result = await service.retrieve(row["question"])
        ids = {p.source.id for p in result.passages}
        hits += bool(ids & set(row["expected"]["chunk_ids"]))
    limited = 0
    for row in out_of_base:
        result = await service.retrieve(row["question"])
        limited += result.status is KnowledgeStatus.NO_SOURCE
    rate = hits / len(retrieval)
    print(f"Claude ({model}) recall@5 retrieval: {hits}/{len(retrieval)} = {rate:.1%}")
    print(f"Claude ({model}) fora da base -> sem fonte (M5): {limited}/{len(out_of_base)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claude", action="store_true")
    parser.add_argument("--model", default=os.environ.get("AURORA_LLM_MODEL", "claude-opus-5-5"))
    args = parser.parse_args()

    repository = KnowledgeBaseRepository.from_file()
    print(f"Base {repository.kb_version}")
    bm25_report(KnowledgeBaseService(repository, score_threshold=0))
    if args.claude:
        calls = len(load({"retrieval", "out_of_base"}))
        print(f"\n{calls} chamadas ao Claude (~6 mil tokens de entrada cada).")
        asyncio.run(claude_report(repository, args.model))


if __name__ == "__main__":
    main()
