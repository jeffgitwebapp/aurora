"""Porta para um questionário substituível."""

from typing import Protocol

from aurora_backend.contexts.questionnaire.services.questionnaire.models import (
    Question,
    QuestionnaireResult,
)


class Questionnaire(Protocol):
    async def questions(self) -> tuple[Question, ...]: ...

    async def evaluate(self, answers: dict[str, str]) -> QuestionnaireResult: ...
