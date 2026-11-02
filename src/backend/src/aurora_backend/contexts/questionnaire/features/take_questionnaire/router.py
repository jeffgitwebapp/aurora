"""Adaptador HTTP da feature ResponderQuestionario."""

from fastapi import APIRouter, HTTPException, status

from aurora_backend.contexts.questionnaire.features.take_questionnaire.schemas import (
    AnswerOptionResponse,
    QuestionnaireResultResponse,
    QuestionResponse,
    QuestionsResponse,
    SubmitAnswersRequest,
)
from aurora_backend.contexts.questionnaire.services.questionnaire.models import (
    InvalidAnswersError,
)
from aurora_backend.contexts.questionnaire.services.questionnaire.port import Questionnaire


def create_take_questionnaire_router(*, questionnaire_service: Questionnaire) -> APIRouter:
    router = APIRouter(prefix="/api/questionnaire", tags=["questionário"])

    @router.get("/questions", response_model=QuestionsResponse)
    async def list_questions() -> QuestionsResponse:
        questions = await questionnaire_service.questions()
        return QuestionsResponse(
            questions=[
                QuestionResponse(
                    id=question.id,
                    title=question.title,
                    options=[
                        AnswerOptionResponse(id=option.id, label=option.label)
                        for option in question.options
                    ],
                )
                for question in questions
            ],
            demo=True,
        )

    @router.post("/results", response_model=QuestionnaireResultResponse)
    async def submit_answers(request: SubmitAnswersRequest) -> QuestionnaireResultResponse:
        try:
            result = await questionnaire_service.evaluate(request.answers)
        except InvalidAnswersError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=str(exc),
            ) from exc
        return QuestionnaireResultResponse(
            band=result.band.value,
            help_type=result.help_type,
            demo=result.demo,
        )

    return router
