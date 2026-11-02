"""Modelos de domínio da conta pseudonimizada."""

import re
from dataclasses import dataclass
from datetime import date

NICKNAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]{3,30}$")
PASSWORD_MIN_LENGTH = 10
PASSWORD_MAX_LENGTH = 128
MAX_SAVED_CONVERSATIONS = 50
MAX_MESSAGES_PER_CONVERSATION = 200
MAX_MESSAGE_LENGTH = 4000
MESSAGE_ROLES = frozenset({"user", "assistant"})
MODULE_ID_PATTERN = re.compile(r"^[a-z0-9-]{1,60}$")
MAX_MODULE_SECTION = 49
MAX_TRACKED_MODULES = 100
MAX_JOURNAL_ENTRIES = 200
MAX_TRUSTED_CONTACTS = 5
MAX_SAFETY_NOTES = 4000
CONTACT_PHONE_PATTERN = re.compile(r"^[0-9+()\- ]{8,20}$")
MAX_JOURNAL_DESCRIPTION = 4000
JOURNAL_TIME_PATTERN = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


@dataclass(frozen=True)
class AccountSession:
    nickname: str
    token: str


@dataclass(frozen=True)
class SavedMessage:
    role: str
    text: str


@dataclass(frozen=True)
class ConversationSummary:
    id: str
    saved_at: float
    message_count: int
    excerpt: str


@dataclass(frozen=True)
class SavedConversation:
    id: str
    saved_at: float
    messages: tuple[SavedMessage, ...]


@dataclass(frozen=True)
class ModuleProgress:
    module_id: str
    section: int
    completed: bool


@dataclass(frozen=True)
class JournalEntry:
    id: str
    entry_date: str
    entry_time: str | None
    description: str
    updated_at: float


class InvalidJournalEntryError(ValueError):
    """Data, hora ou descrição fora das regras aprovadas."""


class JournalEntryNotFoundError(LookupError):
    """Registro inexistente para a conta da sessão."""


def validate_journal_entry(
    entry_date: str,
    entry_time: str | None,
    description: str,
    today: date,
) -> None:
    try:
        parsed = date.fromisoformat(entry_date)
    except ValueError as exc:
        raise InvalidJournalEntryError("Informe uma data válida.") from exc
    if parsed > today:
        raise InvalidJournalEntryError("A data não pode ser no futuro.")
    if entry_time is not None and not JOURNAL_TIME_PATTERN.fullmatch(entry_time):
        raise InvalidJournalEntryError("Informe uma hora válida (HH:MM).")
    if not description.strip():
        raise InvalidJournalEntryError("Escreva uma descrição.")
    if len(description) > MAX_JOURNAL_DESCRIPTION:
        raise InvalidJournalEntryError("A descrição pode ter até 4.000 caracteres.")


@dataclass(frozen=True)
class TrustedContact:
    name: str
    phone: str


@dataclass(frozen=True)
class SafetyPlan:
    contacts: tuple[TrustedContact, ...]
    notes: str
    updated_at: float | None


class InvalidSafetyPlanError(ValueError):
    """Contatos ou anotações fora das regras aprovadas."""


def validate_safety_plan(contacts: tuple[TrustedContact, ...], notes: str) -> None:
    if len(contacts) > MAX_TRUSTED_CONTACTS:
        raise InvalidSafetyPlanError("Você pode guardar até 5 contatos.")
    for contact in contacts:
        if not contact.name.strip() or len(contact.name) > 60:
            raise InvalidSafetyPlanError("Cada contato precisa de um nome ou apelido (até 60).")
        digits = sum(character.isdigit() for character in contact.phone)
        if not CONTACT_PHONE_PATTERN.fullmatch(contact.phone) or digits < 8:
            raise InvalidSafetyPlanError("Informe um telefone válido para cada contato.")
    if len(notes) > MAX_SAFETY_NOTES:
        raise InvalidSafetyPlanError("As anotações podem ter até 4.000 caracteres.")


class InvalidModuleProgressError(ValueError):
    """Identificador de módulo ou seção fora do formato aceito."""


class InvalidConversationError(ValueError):
    """Conversa vazia, mensagens inválidas ou limite de conversas atingido."""


class ConversationNotFoundError(LookupError):
    """Conversa inexistente para a conta da sessão."""


class InvalidRegistrationError(ValueError):
    """Apelido ou senha fora das regras aprovadas."""


class NicknameTakenError(ValueError):
    """Apelido já usado por outra conta."""


class InvalidCredentialsError(ValueError):
    """Apelido ou senha incorretos (sem revelar qual)."""


class AccountLockedError(RuntimeError):
    """Muitas tentativas erradas seguidas para o mesmo apelido."""


class InvalidSessionError(ValueError):
    """Token ausente, desconhecido ou expirado."""


def validate_messages(messages: tuple[SavedMessage, ...]) -> None:
    if not messages:
        raise InvalidConversationError("Ainda não há mensagens para salvar.")
    if len(messages) > MAX_MESSAGES_PER_CONVERSATION:
        raise InvalidConversationError("A conversa tem mensagens demais para salvar.")
    for message in messages:
        if (
            message.role not in MESSAGE_ROLES
            or not message.text.strip()
            or len(message.text) > MAX_MESSAGE_LENGTH
        ):
            raise InvalidConversationError("A conversa contém uma mensagem inválida.")


def validate_registration(nickname: str, password: str) -> None:
    if not NICKNAME_PATTERN.fullmatch(nickname):
        raise InvalidRegistrationError(
            "O apelido deve ter de 3 a 30 caracteres: letras, números, ponto, hífen ou sublinhado."
        )
    if (
        len(password) < PASSWORD_MIN_LENGTH
        or len(password) > PASSWORD_MAX_LENGTH
        or not any(character.isalpha() for character in password)
        or not any(character.isdigit() for character in password)
    ):
        raise InvalidRegistrationError(
            "A senha deve ter pelo menos 10 caracteres, com letras e números."
        )
