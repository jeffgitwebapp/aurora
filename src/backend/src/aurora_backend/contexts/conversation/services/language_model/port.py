"""Porta independente de provedor para chamadas ao LLM (D-13).

Os serviços de domínio (seleção de trechos, redação da resposta) dependem só desta
porta. Os adaptadores (Gemini, Claude) são os únicos que importam SDKs.
"""

from dataclasses import dataclass, field
from typing import Any, Protocol


class LanguageModelUnavailableError(RuntimeError):
    """Timeout, cota, bloqueio/recusa do provedor ou resposta fora do schema (falha fechada)."""


@dataclass(frozen=True)
class LanguageModelUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    cached_input_tokens: int = 0


@dataclass(frozen=True)
class LanguageModelResult:
    data: dict[str, Any]
    provider: str
    model: str
    usage: LanguageModelUsage = field(default_factory=LanguageModelUsage)


class LanguageModel(Protocol):
    @property
    def provider(self) -> str: ...

    @property
    def model(self) -> str: ...

    async def generate_json(
        self,
        *,
        system: str,
        prompt: str,
        schema: dict[str, Any],
        max_output_tokens: int,
    ) -> LanguageModelResult:
        """Objeto JSON que obedece a `schema`; senão, LanguageModelUnavailableError."""
        ...
