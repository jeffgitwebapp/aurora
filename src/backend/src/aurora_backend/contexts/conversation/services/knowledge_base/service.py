"""Recuperação na versão vigente da base curada (porta KnowledgeRetriever).

BM25 traz até 30 candidatos; com um seletor (D-12), o Claude escolhe entre eles os
trechos que respondem à mensagem. Sem candidatos ou sem escolha, o resultado é
"sem fonte" e o LLM de resposta não é chamado. Falha do seletor é falha fechada.
"""

from aurora_backend.contexts.conversation.services.knowledge.models import (
    KnowledgePassage,
    KnowledgeResult,
    KnowledgeStatus,
    SourceReference,
)
from aurora_backend.contexts.conversation.services.knowledge.port import (
    KnowledgeUnavailableError,
)
from aurora_backend.contexts.conversation.services.knowledge_base.models import (
    CitableKind,
    KnowledgeChunk,
    ReviewStatus,
)
from aurora_backend.contexts.conversation.services.knowledge_base.repository import (
    KnowledgeBaseRepository,
)
from aurora_backend.contexts.conversation.services.knowledge_base.search import (
    BM25Index,
    tokenize,
)
from aurora_backend.contexts.conversation.services.knowledge_base.selector import (
    ChunkSelectionUnavailableError,
    ChunkSelector,
)

DEFAULT_TOP_K = 5
DEFAULT_CANDIDATES = 30
# Só para o modo sem seletor (BM25 puro); ver registro de execução da F1 no plano.
DEFAULT_SCORE_THRESHOLD = 2.0
CURATED_SUMMARY_LABEL = "resumo da curadoria Aurora, não é o texto da fonte"


def _index_text(chunk: KnowledgeChunk) -> str:
    """Texto indexado; as perguntas de teste ficam de fora (são gabarito)."""
    return " ".join(
        part
        for part in (
            chunk.title,
            chunk.section,
            chunk.locator,
            " ".join(chunk.topics).replace("-", " "),
            chunk.citable_text,
            chunk.plain_summary or "",
        )
        if part
    )


def _passage(chunk: KnowledgeChunk) -> KnowledgePassage:
    locator = chunk.locator
    if chunk.citable_kind is CitableKind.CURATED_SUMMARY:
        locator = f"{locator} ({CURATED_SUMMARY_LABEL})"
    return KnowledgePassage(
        text=chunk.citable_text,
        source=SourceReference(
            id=chunk.id,
            title=chunk.title,
            locator=locator,
            publisher=chunk.publisher,
            url=chunk.url,
            version=chunk.version,
        ),
    )


class KnowledgeBaseService:
    """Trechos relevantes da base vigente; sem trecho relevante, sem fonte."""

    def __init__(
        self,
        repository: KnowledgeBaseRepository,
        *,
        selector: ChunkSelector | None = None,
        top_k: int = DEFAULT_TOP_K,
        candidates: int = DEFAULT_CANDIDATES,
        score_threshold: float = DEFAULT_SCORE_THRESHOLD,
        allow_pending: bool = True,
    ):
        self._chunks = repository.searchable_chunks(allow_pending=allow_pending)
        self._index = BM25Index([tokenize(_index_text(chunk)) for chunk in self._chunks])
        self._selector = selector
        self._top_k = top_k
        self._candidates = candidates
        self._threshold = score_threshold
        self.kb_version = repository.kb_version

    def rank(self, message: str) -> list[tuple[KnowledgeChunk, float]]:
        scores = self._index.scores(tokenize(message))
        ranked = sorted(
            zip(self._chunks, scores, strict=True), key=lambda item: item[1], reverse=True
        )
        return [(chunk, score) for chunk, score in ranked if score > 0]

    async def retrieve(self, message: str) -> KnowledgeResult:
        ranked = self.rank(message)
        if self._selector is None:
            selected = [chunk for chunk, score in ranked[: self._top_k] if score >= self._threshold]
        else:
            selected = await self._select(message, [chunk for chunk, _ in ranked])
        if not selected:
            return KnowledgeResult(status=KnowledgeStatus.NO_SOURCE)
        return KnowledgeResult(
            status=KnowledgeStatus.FOUND,
            passages=tuple(_passage(chunk) for chunk in selected),
            demo=any(chunk.status is not ReviewStatus.APPROVED for chunk in selected),
        )

    async def _select(self, message: str, ranked: list[KnowledgeChunk]) -> list[KnowledgeChunk]:
        candidates = tuple(ranked[: self._candidates])
        if not candidates or self._selector is None:
            return []
        try:
            selected_ids = await self._selector.select(message, candidates)
        except ChunkSelectionUnavailableError as exc:
            raise KnowledgeUnavailableError("Seleção de trechos indisponível.") from exc
        by_id = {chunk.id: chunk for chunk in candidates}
        return [by_id[chunk_id] for chunk_id in selected_ids if chunk_id in by_id][: self._top_k]
