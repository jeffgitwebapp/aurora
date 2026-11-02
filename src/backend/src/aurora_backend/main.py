"""Composição da aplicação FastAPI."""

from fastapi import FastAPI

from aurora_backend.contexts import accounts, conversation, learning, questionnaire, referral
from aurora_backend.contexts.accounts.services.accounts.port import Accounts
from aurora_backend.contexts.accounts.services.accounts.service import AccountService
from aurora_backend.contexts.conversation.services.chat_response.port import (
    ChatResponseGenerator,
)
from aurora_backend.contexts.conversation.services.chat_response.service import (
    ChatResponseService,
)
from aurora_backend.contexts.conversation.services.content_offer.port import (
    ContentOfferProvider,
)
from aurora_backend.contexts.conversation.services.content_offer.service import (
    ContentOfferService,
)
from aurora_backend.contexts.conversation.services.guardrail.port import ScopeGuardrail
from aurora_backend.contexts.conversation.services.guardrail.service import GuardrailService
from aurora_backend.contexts.conversation.services.knowledge.port import KnowledgeRetriever
from aurora_backend.contexts.conversation.services.knowledge.service import KnowledgeService
from aurora_backend.contexts.conversation.services.triage.port import TriageEvaluator
from aurora_backend.contexts.conversation.services.triage.service import TriageService
from aurora_backend.contexts.learning.services.modules.port import ModuleCatalog
from aurora_backend.contexts.learning.services.modules.service import ModuleCatalogService
from aurora_backend.contexts.learning.services.safety_guide.port import SafetyGuide
from aurora_backend.contexts.learning.services.safety_guide.service import SafetyGuideService
from aurora_backend.contexts.questionnaire.services.questionnaire.port import Questionnaire
from aurora_backend.contexts.questionnaire.services.questionnaire.service import (
    QuestionnaireService,
)
from aurora_backend.contexts.referral.services.catalog.port import ServiceCatalog
from aurora_backend.contexts.referral.services.catalog.service import CatalogService


def create_app(
    *,
    triage_service: TriageEvaluator | None = None,
    guardrail_service: ScopeGuardrail | None = None,
    offer_service: ContentOfferProvider | None = None,
    knowledge_service: KnowledgeRetriever | None = None,
    chat_response_service: ChatResponseGenerator | None = None,
    catalog_service: ServiceCatalog | None = None,
    questionnaire_service: Questionnaire | None = None,
    account_service: Accounts | None = None,
    module_catalog: ModuleCatalog | None = None,
    safety_guide: SafetyGuide | None = None,
) -> FastAPI:
    application = FastAPI(
        title="Aurora (protótipo local)",
        description=(
            "Protótipo com serviços de triagem, limite de escopo, conhecimento, "
            "resposta, catálogo, questionário, contas e módulos usando dados estáticos ou "
            "em memória. As fixtures não avaliam risco nem escopo reais; fontes e "
            "serviços são demonstrativos, contas não são protegidas para uso real "
            "e a resposta não é aconselhamento nem atendimento."
        ),
        version="0.1.0",
    )
    composed_triage_service = triage_service if triage_service is not None else TriageService()
    composed_guardrail_service = (
        guardrail_service if guardrail_service is not None else GuardrailService()
    )
    composed_knowledge_service = (
        knowledge_service if knowledge_service is not None else KnowledgeService()
    )
    composed_chat_response_service = (
        chat_response_service if chat_response_service is not None else ChatResponseService()
    )
    for router in conversation.create_routers(
        triage_service=composed_triage_service,
        guardrail_service=composed_guardrail_service,
        offer_service=offer_service if offer_service is not None else ContentOfferService(),
        knowledge_service=composed_knowledge_service,
        chat_response_service=composed_chat_response_service,
    ):
        application.include_router(router)
    for router in referral.create_routers(
        catalog_service=catalog_service if catalog_service is not None else CatalogService(),
    ):
        application.include_router(router)
    for router in questionnaire.create_routers(
        questionnaire_service=(
            questionnaire_service if questionnaire_service is not None else QuestionnaireService()
        ),
    ):
        application.include_router(router)
    for router in accounts.create_routers(
        account_service=account_service if account_service is not None else AccountService(),
    ):
        application.include_router(router)
    for router in learning.create_routers(
        module_catalog=module_catalog if module_catalog is not None else ModuleCatalogService(),
        safety_guide=safety_guide if safety_guide is not None else SafetyGuideService(),
    ):
        application.include_router(router)
    return application


app = create_app()
