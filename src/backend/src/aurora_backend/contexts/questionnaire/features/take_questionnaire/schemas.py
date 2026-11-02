"""Contratos HTTP da feature ResponderQuestionario."""

from typing import Literal

from pydantic import BaseModel, Field


class AnswerOptionResponse(BaseModel):
    id: str
    label: str


class QuestionResponse(BaseModel):
    id: str
    title: str
    options: list[AnswerOptionResponse]


class QuestionsResponse(BaseModel):
    questions: list[QuestionResponse]
    demo: bool


class SubmitAnswersRequest(BaseModel):
    answers: dict[str, str] = Field(max_length=20)


class QuestionnaireResultResponse(BaseModel):
    band: Literal["A", "B", "C"]
    help_type: Literal["report", "legal", "psychological", "peer"] | None
    demo: bool
