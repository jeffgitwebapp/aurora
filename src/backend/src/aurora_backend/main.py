"""Composição da aplicação FastAPI."""

from fastapi import FastAPI

from aurora_backend.contexts import conversation


def create_app() -> FastAPI:
    application = FastAPI(
        title="Aurora (protótipo local)",
        description=(
            "Protótipo que gera texto aleatório simulado, sem analisar a mensagem. "
            "Não é aconselhamento nem serviço de atendimento."
        ),
        version="0.1.0",
    )
    for router in conversation.routers:
        application.include_router(router)
    return application


app = create_app()
