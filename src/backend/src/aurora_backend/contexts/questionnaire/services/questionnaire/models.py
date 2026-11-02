"""Modelos de domínio do questionário de reconhecimento."""

from dataclasses import dataclass
from enum import StrEnum


@dataclass(frozen=True)
class AnswerOption:
    id: str
    label: str


@dataclass(frozen=True)
class Question:
    id: str
    title: str
    options: tuple[AnswerOption, ...]


class DemoBand(StrEnum):
    """Faixas fictícias de demonstração; não representam padrão, risco nem diagnóstico."""

    A = "A"
    B = "B"
    C = "C"


@dataclass(frozen=True)
class QuestionnaireResult:
    band: DemoBand
    help_type: str | None
    demo: bool = True


class InvalidAnswersError(ValueError):
    """Respostas ausentes ou alternativas que não pertencem à pergunta."""
