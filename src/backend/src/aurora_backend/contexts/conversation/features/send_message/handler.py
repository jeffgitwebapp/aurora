"""Orquestra o envio de mensagem entre triagem e serviço de conversa."""

from dataclasses import dataclass

from aurora_backend.contexts.conversation.services.chat_response.port import (
    ChatResponseGenerator,
)
from aurora_backend.contexts.conversation.services.triage.models import (
    TriageResult,
    TriageStatus,
)
from aurora_backend.contexts.conversation.services.triage.port import TriageEvaluator


@dataclass(frozen=True)
class SendMessageResult:
    reply: str | None
    triage: TriageResult


class EmptyMessageError(ValueError):
    """Mensagem vazia ou composta apenas por espaços."""


async def handle_send_message(
    message: str,
    *,
    triage_service: TriageEvaluator,
    chat_response_service: ChatResponseGenerator,
) -> SendMessageResult:
    if not message.strip():
        raise EmptyMessageError("A mensagem não pode estar vazia.")

    triage = await triage_service.assess(message)
    if triage.status is not TriageStatus.NO_ACUTE_SIGNAL:
        return SendMessageResult(reply=None, triage=triage)

    return SendMessageResult(
        reply=await chat_response_service.generate_reply(message),
        triage=triage,
    )
