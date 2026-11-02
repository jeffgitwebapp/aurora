"""Orquestra o envio de mensagem entre triagem, conhecimento e resposta."""

from dataclasses import dataclass

from aurora_backend.contexts.conversation.services.chat_response.port import (
    ChatResponseGenerator,
)
from aurora_backend.contexts.conversation.services.knowledge.models import (
    KnowledgeResult,
    KnowledgeStatus,
)
from aurora_backend.contexts.conversation.services.knowledge.port import KnowledgeRetriever
from aurora_backend.contexts.conversation.services.triage.models import (
    TriageResult,
    TriageStatus,
)
from aurora_backend.contexts.conversation.services.triage.port import TriageEvaluator


@dataclass(frozen=True)
class SendMessageResult:
    reply: str | None
    triage: TriageResult
    knowledge: KnowledgeResult | None = None


class EmptyMessageError(ValueError):
    """Mensagem vazia ou composta apenas por espaços."""


async def handle_send_message(
    message: str,
    *,
    triage_service: TriageEvaluator,
    knowledge_service: KnowledgeRetriever,
    chat_response_service: ChatResponseGenerator,
) -> SendMessageResult:
    if not message.strip():
        raise EmptyMessageError("A mensagem não pode estar vazia.")

    triage = await triage_service.assess(message)
    if triage.status is not TriageStatus.NO_ACUTE_SIGNAL:
        return SendMessageResult(reply=None, triage=triage)

    knowledge = await knowledge_service.retrieve(message)
    if knowledge.status is not KnowledgeStatus.FOUND:
        return SendMessageResult(reply=None, triage=triage, knowledge=knowledge)

    return SendMessageResult(
        reply=await chat_response_service.generate_reply(message, knowledge.passages),
        triage=triage,
        knowledge=knowledge,
    )
