"""Modelos de domínio para o resultado de triagem."""

from dataclasses import dataclass
from enum import StrEnum


class TriageStatus(StrEnum):
    ACUTE = "acute"
    NO_ACUTE_SIGNAL = "no_acute_signal"
    INDETERMINATE = "indeterminate"


class TriageSignal(StrEnum):
    SUICIDAL_IDEATION = "suicidal_ideation"
    ONGOING_ASSAULT = "ongoing_assault"
    DEATH_THREAT = "death_threat"
    WEAPON_PRESENT = "weapon_present"


@dataclass(frozen=True)
class TriageResult:
    status: TriageStatus
    signals: tuple[TriageSignal, ...] = ()
    guidance: str | None = None
