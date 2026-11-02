"""Porta para um guia de segurança substituível."""

from typing import Protocol

from aurora_backend.contexts.learning.services.safety_guide.models import SafetyGuideContent


class SafetyGuide(Protocol):
    async def content(self) -> SafetyGuideContent: ...
