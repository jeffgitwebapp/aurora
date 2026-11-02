"""Modelos de domínio para a decisão de escopo do pedido."""

from dataclasses import dataclass
from enum import StrEnum


class ScopeDecision(StrEnum):
    ALLOW = "allow"
    OUT_OF_SCOPE = "out_of_scope"


class OutOfScopeCategory(StrEnum):
    DIAGNOSIS = "diagnosis"
    PRESCRIPTION = "prescription"
    INDIVIDUAL_LEGAL_OPINION = "individual_legal_opinion"


@dataclass(frozen=True)
class GuardrailResult:
    decision: ScopeDecision
    category: OutOfScopeCategory | None = None

    def __post_init__(self) -> None:
        if self.decision is ScopeDecision.OUT_OF_SCOPE and self.category is None:
            raise ValueError("Pedido fora do escopo exige uma categoria.")
        if self.decision is ScopeDecision.ALLOW and self.category is not None:
            raise ValueError("Pedido permitido não pode ter categoria de limite.")
