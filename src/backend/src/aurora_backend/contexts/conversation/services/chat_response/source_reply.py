"""Resposta montada a partir dos trechos da base curada (motores `base` e `llm`).

Diferente da fixture, as fontes podem ser leis, guias, dados ou literatura, então a
abertura é neutra. Cada citação recebe o marcador [n] na ordem de `sources` (U-03).
Na F2, a redação passa a ser feita pelo LLM (GroundedAnswerService).
"""

from aurora_backend.contexts.conversation.services.knowledge.models import KnowledgePassage

SOURCE_REPLY_INTRODUCTION = "Encontrei estas informações nas fontes, sem opinar sobre o seu caso:"


class SourceReplyService:
    """Lista os trechos recebidos com a fonte de cada um; não cria conteúdo."""

    async def generate_reply(
        self,
        message: str,
        passages: tuple[KnowledgePassage, ...],
    ) -> str:
        del message
        if not passages:
            raise ValueError("A resposta exige ao menos um trecho de fonte.")
        numbers: dict[str, int] = {}
        for passage in passages:
            numbers.setdefault(passage.source.id, len(numbers) + 1)
        quotes = (
            f"{passage.source.title}, {passage.source.locator}: “{passage.text}” "
            f"[{numbers[passage.source.id]}]"
            for passage in passages
        )
        return "\n\n".join((SOURCE_REPLY_INTRODUCTION, *quotes))
