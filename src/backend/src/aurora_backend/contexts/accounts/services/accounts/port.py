"""Porta para um serviço substituível de contas, sessões e conversas salvas."""

from typing import Protocol

from aurora_backend.contexts.accounts.services.accounts.models import (
    AccountSession,
    ConversationSummary,
    JournalEntry,
    ModuleProgress,
    SafetyPlan,
    SavedConversation,
    SavedMessage,
    TrustedContact,
)


class Accounts(Protocol):
    async def register(self, nickname: str, password: str) -> AccountSession: ...

    async def login(self, nickname: str, password: str) -> AccountSession: ...

    async def current(self, token: str) -> str: ...

    async def logout(self, token: str) -> None: ...

    async def save_conversation(
        self,
        token: str,
        messages: tuple[SavedMessage, ...],
    ) -> ConversationSummary: ...

    async def list_conversations(self, token: str) -> tuple[ConversationSummary, ...]: ...

    async def get_conversation(self, token: str, conversation_id: str) -> SavedConversation: ...

    async def delete_conversation(self, token: str, conversation_id: str) -> None: ...

    async def list_module_progress(self, token: str) -> tuple[ModuleProgress, ...]: ...

    async def save_module_progress(
        self,
        token: str,
        module_id: str,
        section: int,
        completed: bool,
    ) -> ModuleProgress: ...

    async def list_journal(self, token: str) -> tuple[JournalEntry, ...]: ...

    async def save_journal_entry(
        self,
        token: str,
        entry_id: str | None,
        entry_date: str,
        entry_time: str | None,
        description: str,
    ) -> JournalEntry: ...

    async def delete_journal_entry(self, token: str, entry_id: str) -> None: ...

    async def get_safety_plan(self, token: str) -> SafetyPlan: ...

    async def save_safety_plan(
        self,
        token: str,
        contacts: tuple[TrustedContact, ...],
        notes: str,
    ) -> SafetyPlan: ...

    async def delete_account(self, token: str) -> None: ...
