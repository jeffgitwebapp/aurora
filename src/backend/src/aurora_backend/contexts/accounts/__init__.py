"""Bounded context Contas (área logada pseudonimizada)."""

from fastapi import APIRouter

from aurora_backend.contexts.accounts.features.delete_account.router import (
    create_delete_account_router,
)
from aurora_backend.contexts.accounts.features.journal.router import create_journal_router
from aurora_backend.contexts.accounts.features.manage_session.router import (
    create_manage_session_router,
)
from aurora_backend.contexts.accounts.features.module_progress.router import (
    create_module_progress_router,
)
from aurora_backend.contexts.accounts.features.register_account.router import (
    create_register_account_router,
)
from aurora_backend.contexts.accounts.features.safety_plan.router import (
    create_safety_plan_router,
)
from aurora_backend.contexts.accounts.features.saved_conversations.router import (
    create_saved_conversations_router,
)
from aurora_backend.contexts.accounts.services.accounts.port import Accounts


def create_routers(*, account_service: Accounts) -> tuple[APIRouter, ...]:
    return (
        create_register_account_router(account_service=account_service),
        create_manage_session_router(account_service=account_service),
        create_saved_conversations_router(account_service=account_service),
        create_module_progress_router(account_service=account_service),
        create_journal_router(account_service=account_service),
        create_safety_plan_router(account_service=account_service),
        create_delete_account_router(account_service=account_service),
    )


__all__ = ["create_routers"]
