"""Serviço de resposta da conversa com redação estática de protótipo."""

from aurora_backend.contexts.conversation.services.knowledge.models import KnowledgePassage

REPLY_INTRODUCTION = "Este é o texto da lei sobre isso, sem opinar sobre o seu caso."


class ChatResponseService:
    """Redige a resposta somente com os trechos recebidos; o LLM aprovado substituirá
    esta redação estática sem decidir risco, encaminhamento nem criar fontes."""

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
        return "\n\n".join((REPLY_INTRODUCTION, *quotes))
