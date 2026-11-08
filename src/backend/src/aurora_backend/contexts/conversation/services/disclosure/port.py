"""Porta do reconhecimento de relato pessoal (U-14)."""

from typing import Protocol


class DisclosureDetector(Protocol):
    async def is_disclosure(self, message: str) -> bool: ...
