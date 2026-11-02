"""Porta para um serviço substituível de triagem."""

from typing import Protocol

from aurora_backend.contexts.conversation.services.triage.models import TriageResult


class TriageEvaluator(Protocol):
    async def assess(self, message: str) -> TriageResult: ...
