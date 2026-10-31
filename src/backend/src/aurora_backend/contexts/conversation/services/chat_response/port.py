"""Porta para um serviço de geração de resposta conversacional."""

from typing import Protocol


class ChatResponseGenerator(Protocol):
    async def generate_reply(self, message: str) -> str: ...
