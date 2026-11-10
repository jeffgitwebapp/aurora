"""Orquestra o envio de mensagem entre triagem, escopo, conhecimento e resposta."""

from dataclasses import dataclass

from aurora_backend.contexts.conversation.features.send_message.replies import (
    DISCLOSURE_NO_SOURCE_REPLY,
    NO_SOURCE_REPLY,
    OUT_OF_SCOPE_REPLY,
    SAFETY_GUIDE_OFFER_REPLY,
)
from aurora_backend.contexts.conversation.services.chat_response.port import (
    ChatResponseGenerator,
)
from aurora_backend.contexts.conversation.services.content_offer.models import ContentOffer
from aurora_backend.contexts.conversation.services.content_offer.port import (
    ContentOfferProvider,
)
from aurora_backend.contexts.conversation.services.disclosure.port import DisclosureDetector
from aurora_backend.contexts.conversation.services.disclosure.service import DisclosureService
from aurora_backend.contexts.conversation.services.guardrail.models import (
    GuardrailResult,
    ScopeDecision,
)
from aurora_backend.contexts.conversation.services.guardrail.port import ScopeGuardrail
from aurora_backend.contexts.conversation.services.knowledge.models import (
    KnowledgeResult,
    KnowledgeStatus,
)
from aurora_backend.contexts.conversation.services.knowledge.port import KnowledgeRetriever
from aurora_backend.contexts.conversation.services.small_talk.port import SmallTalkDetector
from aurora_backend.contexts.conversation.services.small_talk.service import (
    ConversationKind,
    SmallTalkService,
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
    guardrail: GuardrailResult | None = None
    knowledge: KnowledgeResult | None = None
    offer: ContentOffer | None = None
    conversation: ConversationKind | None = None


class EmptyMessageError(ValueError):
    """Mensagem vazia ou composta apenas por espaços."""


async def handle_send_message(
    message: str,
    *,
    triage_service: TriageEvaluator,
    guardrail_service: ScopeGuardrail,
    offer_service: ContentOfferProvider,
    knowledge_service: KnowledgeRetriever,
    chat_response_service: ChatResponseGenerator,
    small_talk_service: SmallTalkDetector | None = None,
    disclosure_service: DisclosureDetector | None = None,
) -> SendMessageResult:
    if not message.strip():
        raise EmptyMessageError("A mensagem não pode estar vazia.")

    triage = await triage_service.assess(message)
    if triage.status is not TriageStatus.NO_ACUTE_SIGNAL:
        return SendMessageResult(reply=None, triage=triage)

    guardrail = await guardrail_service.check_request(message)
    if guardrail.decision is not ScopeDecision.ALLOW:
        return SendMessageResult(reply=OUT_OF_SCOPE_REPLY, triage=triage, guardrail=guardrail)

    small_talk = await (small_talk_service or SmallTalkService()).respond(message)
    if small_talk is not None:
        return SendMessageResult(
            reply=small_talk.text,
            triage=triage,
            guardrail=guardrail,
            conversation=small_talk.kind,
        )

    offer = await offer_service.suggest(message)
    if offer is not None:
        return SendMessageResult(
            reply=SAFETY_GUIDE_OFFER_REPLY, triage=triage, guardrail=guardrail, offer=offer
        )

    knowledge = await knowledge_service.retrieve(message)
    if knowledge.status is not KnowledgeStatus.FOUND:
        # Relato pessoal sem fonte recebe acolhimento em vez do "não sei" (U-14).
        is_disclosure = await (disclosure_service or DisclosureService()).is_disclosure(message)
        return SendMessageResult(
            reply=DISCLOSURE_NO_SOURCE_REPLY if is_disclosure else NO_SOURCE_REPLY,
            triage=triage,
            guardrail=guardrail,
            knowledge=knowledge,
        )

    return SendMessageResult(
        reply=await chat_response_service.generate_reply(message, knowledge.passages),
        triage=triage,
        guardrail=guardrail,
        knowledge=knowledge,
    )
