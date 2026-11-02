"""Questionário com perguntas de demonstração no protótipo."""

from aurora_backend.contexts.questionnaire.services.questionnaire.models import (
    AnswerOption,
    DemoBand,
    InvalidAnswersError,
    Question,
    QuestionnaireResult,
)

SKIP_OPTION = AnswerOption(id="skip", label="Prefiro não responder")

# Aprovado pela usuária em 02/11/2026: perguntas de reconhecimento são
# placeholders sem conteúdo clínico até o instrumento validado ser aprovado; a
# pergunta de tipo de ajuda vem do backlog (E4-US4).
_DEMO_OPTION_A = AnswerOption(id="a", label="Opção de demonstração A")
_DEMO_OPTION_B = AnswerOption(id="b", label="Opção de demonstração B")
_HELP_TYPE_QUESTION_ID = "help_type"

_QUESTIONS = (
    Question(
        id="demo_1",
        title="Pergunta de demonstração 1",
        options=(_DEMO_OPTION_A, _DEMO_OPTION_B, SKIP_OPTION),
    ),
    Question(
        id="demo_2",
        title="Pergunta de demonstração 2",
        options=(_DEMO_OPTION_A, _DEMO_OPTION_B, SKIP_OPTION),
    ),
    Question(
        id=_HELP_TYPE_QUESTION_ID,
        title="Que tipo de ajuda você procura?",
        options=(
            AnswerOption(id="report", label="Denúncia"),
            AnswerOption(id="legal", label="Orientação jurídica"),
            AnswerOption(id="psychological", label="Apoio psicológico"),
            AnswerOption(id="peer", label="Apoio entre pares"),
            SKIP_OPTION,
        ),
    ),
)

# Faixa fictícia: conta quantas perguntas de demonstração receberam a opção A.
_BANDS_BY_A_COUNT = {2: DemoBand.A, 1: DemoBand.B, 0: DemoBand.C}


class QuestionnaireService:
    """Serve as perguntas atuais e calcula uma faixa fictícia; não avalia situações reais."""

    async def questions(self) -> tuple[Question, ...]:
        return _QUESTIONS

    async def evaluate(self, answers: dict[str, str]) -> QuestionnaireResult:
        if set(answers) != {question.id for question in _QUESTIONS}:
            raise InvalidAnswersError("Responda todas as perguntas.")
        for question in _QUESTIONS:
            if answers[question.id] not in {option.id for option in question.options}:
                raise InvalidAnswersError("Alternativa inválida.")

        a_count = sum(
            answers[question.id] == _DEMO_OPTION_A.id
            for question in _QUESTIONS
            if question.id != _HELP_TYPE_QUESTION_ID
        )
        help_type = answers[_HELP_TYPE_QUESTION_ID]
        return QuestionnaireResult(
            band=_BANDS_BY_A_COUNT[a_count],
            help_type=None if help_type == SKIP_OPTION.id else help_type,
        )
