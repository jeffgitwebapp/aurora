"""Bounded context Questionário."""

from fastapi import APIRouter

from aurora_backend.contexts.questionnaire.features.take_questionnaire.router import (
    create_take_questionnaire_router,
)
from aurora_backend.contexts.questionnaire.services.questionnaire.port import Questionnaire


def create_routers(*, questionnaire_service: Questionnaire) -> tuple[APIRouter, ...]:
    return (create_take_questionnaire_router(questionnaire_service=questionnaire_service),)


__all__ = ["create_routers"]
