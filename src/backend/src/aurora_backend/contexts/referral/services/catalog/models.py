"""Modelos de domínio para opções de encaminhamento."""

from dataclasses import dataclass
from enum import IntEnum, StrEnum

MAX_RECOMMENDATIONS = 3


class ServiceTier(IntEnum):
    """Hierarquia jurídica: órgãos públicos formais precedem a sociedade civil."""

    PUBLIC_BODY = 1
    SPECIALIZED_SERVICE = 2
    CIVIL_SOCIETY = 3
    VOLUNTEER = 4


class RecommendationStatus(StrEnum):
    FOUND = "found"
    NO_VERIFIED_RESULT = "no_verified_result"


@dataclass(frozen=True)
class ServiceOption:
    id: str
    name: str
    tier: ServiceTier
    category: str
    description: str
    contact: str | None = None
    hours: str | None = None
    cost: str | None = None
    last_verified_at: str | None = None
    demo: bool = True


@dataclass(frozen=True)
class RecommendationResult:
    status: RecommendationStatus
    services: tuple[ServiceOption, ...] = ()
    demo: bool = True

    def __post_init__(self) -> None:
        if self.status is RecommendationStatus.FOUND and not self.services:
            raise ValueError("Resultado encontrado exige ao menos um serviço.")
        if self.status is RecommendationStatus.NO_VERIFIED_RESULT and self.services:
            raise ValueError("Resultado sem serviço verificado não pode listar serviços.")
        if len(self.services) > MAX_RECOMMENDATIONS:
            raise ValueError("O encaminhamento exibe no máximo três opções.")
