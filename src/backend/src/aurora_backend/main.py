"""Composição da aplicação FastAPI."""

from fastapi import FastAPI

from aurora_backend.contexts import conversation
from aurora_backend.contexts.conversation.services.chat_response.port import (
    ChatResponseGenerator,
)
from aurora_backend.contexts.conversation.services.chat_response.service import (
    ChatResponseService,
)
from aurora_backend.contexts.conversation.services.knowledge.port import KnowledgeRetriever
from aurora_backend.contexts.conversation.services.knowledge.service import KnowledgeService
from aurora_backend.contexts.conversation.services.triage.port import TriageEvaluator
from aurora_backend.contexts.conversation.services.triage.service import TriageService


def create_app(
    *,
    triage_service: TriageEvaluator | None = None,
    knowledge_service: KnowledgeRetriever | None = None,
    chat_response_service: ChatResponseGenerator | None = None,
) -> FastAPI:
    application = FastAPI(
        title="Aurora (protótipo local)",
        description=(
            "Protótipo com serviços de triagem, conhecimento e resposta usando dados "
            "estáticos. As fixtures não avaliam risco real; as fontes são "
            "demonstrativas e a resposta não é aconselhamento nem atendimento."
        ),
        version="0.1.0",
    )
    composed_triage_service = triage_service if triage_service is not None else TriageService()
    composed_knowledge_service = (
        knowledge_service if knowledge_service is not None else KnowledgeService()
    )
    composed_chat_response_service = (
        chat_response_service if chat_response_service is not None else ChatResponseService()
    )
    for router in conversation.create_routers(
        triage_service=composed_triage_service,
        knowledge_service=composed_knowledge_service,
        chat_response_service=composed_chat_response_service,
    ):
        application.include_router(router)
    return application


app = create_app()
