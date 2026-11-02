"""Serviço de contas com armazenamento em memória do processo no protótipo."""

import hashlib
import hmac
import json
import os
import secrets
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from aurora_backend.contexts.accounts.services.accounts.models import (
    MAX_JOURNAL_ENTRIES,
    MAX_MODULE_SECTION,
    MAX_SAVED_CONVERSATIONS,
    MAX_TRACKED_MODULES,
    MODULE_ID_PATTERN,
    AccountLockedError,
    AccountSession,
    ConversationNotFoundError,
    ConversationSummary,
    InvalidConversationError,
    InvalidCredentialsError,
    InvalidJournalEntryError,
    InvalidModuleProgressError,
    InvalidSessionError,
    JournalEntry,
    JournalEntryNotFoundError,
    ModuleProgress,
    NicknameTakenError,
    SafetyPlan,
    SavedConversation,
    SavedMessage,
    TrustedContact,
    validate_journal_entry,
    validate_messages,
    validate_registration,
    validate_safety_plan,
)

MAX_FAILED_ATTEMPTS = 5
LOCK_SECONDS = 60
SESSION_TTL_SECONDS = 30 * 60
EXCERPT_LENGTH = 80
_SCRYPT_PARAMS = {"n": 2**14, "r": 8, "p": 1, "dklen": 32}


def _derive(password: str, salt: bytes) -> bytes:
    return hashlib.scrypt(password.encode(), salt=salt, **_SCRYPT_PARAMS)


@dataclass
class _EncryptedRecord:
    saved_at: float
    nonce: bytes
    ciphertext: bytes
    message_count: int = 0


@dataclass
class _Account:
    nickname: str
    salt: bytes
    password_hash: bytes
    # Sal separado para a chave de cifra: o hash de autenticação não abre as conversas.
    encryption_salt: bytes
    conversations: dict[str, _EncryptedRecord] = field(default_factory=dict)
    # Diário: data, hora e descrição cifradas por registro com a chave da sessão.
    journal: dict[str, _EncryptedRecord] = field(default_factory=dict)
    # Plano de segurança (contatos e anotações), cifrado como um único registro.
    safety_plan: _EncryptedRecord | None = None
    # Progresso nos módulos (sem conteúdo do relato); apagado junto com a conta.
    module_progress: dict[str, ModuleProgress] = field(default_factory=dict)


@dataclass
class _FailedAttempts:
    count: int = 0
    locked_until: float = 0.0


@dataclass
class _Session:
    account_key: str
    expires_at: float
    # Chave derivada da senha no login; existe só enquanto a sessão está aberta.
    encryption_key: bytes


@dataclass
class AccountService:
    """Contas demonstrativas apagadas ao reiniciar o processo; não protegem contas reais."""

    clock: Callable[[], float] = time.monotonic
    wall_clock: Callable[[], float] = time.time
    _accounts: dict[str, _Account] = field(default_factory=dict)
    _sessions: dict[str, _Session] = field(default_factory=dict)
    # Contado por apelido, exista ou não a conta, para o bloqueio não revelar cadastros.
    _failures: dict[str, _FailedAttempts] = field(default_factory=dict)
    # Hash de referência para gastar o mesmo tempo quando o apelido não existe.
    _dummy_salt: bytes = field(default_factory=lambda: os.urandom(16))

    async def register(self, nickname: str, password: str) -> AccountSession:
        validate_registration(nickname, password)
        key = nickname.casefold()
        if key in self._accounts:
            raise NicknameTakenError("Este apelido já está em uso. Escolha outro.")
        salt = os.urandom(16)
        account = _Account(
            nickname=nickname,
            salt=salt,
            password_hash=_derive(password, salt),
            encryption_salt=os.urandom(16),
        )
        self._accounts[key] = account
        return self._start_session(key, _derive(password, account.encryption_salt))

    async def login(self, nickname: str, password: str) -> AccountSession:
        key = nickname.casefold()
        now = self.clock()
        failures = self._failures.setdefault(key, _FailedAttempts())
        if failures.locked_until > now:
            raise AccountLockedError("Muitas tentativas. Aguarde 1 minuto e tente novamente.")

        account = self._accounts.get(key)
        salt = account.salt if account is not None else self._dummy_salt
        password_hash = _derive(password, salt)
        if account is None or not hmac.compare_digest(password_hash, account.password_hash):
            failures.count += 1
            if failures.count >= MAX_FAILED_ATTEMPTS:
                failures.count = 0
                failures.locked_until = now + LOCK_SECONDS
            raise InvalidCredentialsError("Apelido ou senha incorretos.")

        self._failures.pop(key, None)
        return self._start_session(key, _derive(password, account.encryption_salt))

    async def current(self, token: str) -> str:
        return self._session_account(token)[1].nickname

    async def logout(self, token: str) -> None:
        self._sessions.pop(token, None)

    async def save_conversation(
        self,
        token: str,
        messages: tuple[SavedMessage, ...],
    ) -> ConversationSummary:
        session, account = self._session_account(token)
        validate_messages(messages)
        if len(account.conversations) >= MAX_SAVED_CONVERSATIONS:
            raise InvalidConversationError("Limite de conversas salvas atingido.")

        conversation_id = secrets.token_urlsafe(12)
        nonce = os.urandom(12)
        plaintext = json.dumps(
            [{"role": message.role, "text": message.text} for message in messages]
        ).encode()
        account.conversations[conversation_id] = _EncryptedRecord(
            saved_at=self.wall_clock(),
            message_count=len(messages),
            nonce=nonce,
            ciphertext=AESGCM(session.encryption_key).encrypt(
                nonce,
                plaintext,
                self._associated_data(session.account_key, conversation_id),
            ),
        )
        return self._summary(session, conversation_id, account.conversations[conversation_id])

    async def list_conversations(self, token: str) -> tuple[ConversationSummary, ...]:
        session, account = self._session_account(token)
        summaries = [
            self._summary(session, conversation_id, conversation)
            for conversation_id, conversation in account.conversations.items()
        ]
        return tuple(sorted(summaries, key=lambda summary: summary.saved_at, reverse=True))

    async def get_conversation(self, token: str, conversation_id: str) -> SavedConversation:
        session, account = self._session_account(token)
        conversation = account.conversations.get(conversation_id)
        if conversation is None:
            raise ConversationNotFoundError("Conversa não encontrada.")
        return SavedConversation(
            id=conversation_id,
            saved_at=conversation.saved_at,
            messages=self._decrypt(session, conversation_id, conversation),
        )

    async def delete_conversation(self, token: str, conversation_id: str) -> None:
        _, account = self._session_account(token)
        if account.conversations.pop(conversation_id, None) is None:
            raise ConversationNotFoundError("Conversa não encontrada.")

    async def list_module_progress(self, token: str) -> tuple[ModuleProgress, ...]:
        _, account = self._session_account(token)
        return tuple(account.module_progress.values())

    async def save_module_progress(
        self,
        token: str,
        module_id: str,
        section: int,
        completed: bool,
    ) -> ModuleProgress:
        _, account = self._session_account(token)
        if not MODULE_ID_PATTERN.fullmatch(module_id) or not 0 <= section <= MAX_MODULE_SECTION:
            raise InvalidModuleProgressError("Progresso inválido.")
        previous = account.module_progress.get(module_id)
        if previous is None and len(account.module_progress) >= MAX_TRACKED_MODULES:
            raise InvalidModuleProgressError("Limite de módulos acompanhados atingido.")
        progress = ModuleProgress(
            module_id=module_id,
            section=section,
            # Uma vez concluído, rever o módulo não desfaz a conclusão.
            completed=completed or (previous is not None and previous.completed),
        )
        account.module_progress[module_id] = progress
        return progress

    async def list_journal(self, token: str) -> tuple[JournalEntry, ...]:
        session, account = self._session_account(token)
        entries = [
            self._journal_entry(session, entry_id, stored)
            for entry_id, stored in account.journal.items()
        ]
        return tuple(
            sorted(
                entries,
                key=lambda entry: (entry.entry_date, entry.entry_time or ""),
                reverse=True,
            )
        )

    async def save_journal_entry(
        self,
        token: str,
        entry_id: str | None,
        entry_date: str,
        entry_time: str | None,
        description: str,
    ) -> JournalEntry:
        session, account = self._session_account(token)
        validate_journal_entry(
            entry_date,
            entry_time,
            description,
            datetime.fromtimestamp(self.wall_clock()).date(),
        )
        if entry_id is None:
            if len(account.journal) >= MAX_JOURNAL_ENTRIES:
                raise InvalidJournalEntryError("Limite de registros atingido.")
            entry_id = secrets.token_urlsafe(12)
        elif entry_id not in account.journal:
            raise JournalEntryNotFoundError("Registro não encontrado.")

        payload = {"date": entry_date, "time": entry_time, "description": description}
        nonce = os.urandom(12)
        account.journal[entry_id] = _EncryptedRecord(
            saved_at=self.wall_clock(),
            nonce=nonce,
            ciphertext=AESGCM(session.encryption_key).encrypt(
                nonce,
                json.dumps(payload).encode(),
                self._associated_data(session.account_key, f"journal:{entry_id}"),
            ),
        )
        return self._journal_entry(session, entry_id, account.journal[entry_id])

    async def delete_journal_entry(self, token: str, entry_id: str) -> None:
        _, account = self._session_account(token)
        if account.journal.pop(entry_id, None) is None:
            raise JournalEntryNotFoundError("Registro não encontrado.")

    async def get_safety_plan(self, token: str) -> SafetyPlan:
        session, account = self._session_account(token)
        if account.safety_plan is None:
            return SafetyPlan(contacts=(), notes="", updated_at=None)
        payload = json.loads(
            AESGCM(session.encryption_key).decrypt(
                account.safety_plan.nonce,
                account.safety_plan.ciphertext,
                self._associated_data(session.account_key, "safety-plan"),
            )
        )
        return SafetyPlan(
            contacts=tuple(TrustedContact(**contact) for contact in payload["contacts"]),
            notes=payload["notes"],
            updated_at=account.safety_plan.saved_at,
        )

    async def save_safety_plan(
        self,
        token: str,
        contacts: tuple[TrustedContact, ...],
        notes: str,
    ) -> SafetyPlan:
        session, account = self._session_account(token)
        validate_safety_plan(contacts, notes)
        payload = {
            "contacts": [{"name": c.name.strip(), "phone": c.phone.strip()} for c in contacts],
            "notes": notes,
        }
        nonce = os.urandom(12)
        account.safety_plan = _EncryptedRecord(
            saved_at=self.wall_clock(),
            nonce=nonce,
            ciphertext=AESGCM(session.encryption_key).encrypt(
                nonce,
                json.dumps(payload).encode(),
                self._associated_data(session.account_key, "safety-plan"),
            ),
        )
        return await self.get_safety_plan(token)

    async def delete_account(self, token: str) -> None:
        session, _ = self._session_account(token)
        del self._accounts[session.account_key]
        self._failures.pop(session.account_key, None)
        for other_token in [
            other_token
            for other_token, other in self._sessions.items()
            if other.account_key == session.account_key
        ]:
            del self._sessions[other_token]

    def _session_account(self, token: str) -> tuple[_Session, _Account]:
        session = self._sessions.get(token)
        if session is None or session.expires_at <= self.clock():
            self._sessions.pop(token, None)
            raise InvalidSessionError("Sessão encerrada.")
        return session, self._accounts[session.account_key]

    def _start_session(self, key: str, encryption_key: bytes) -> AccountSession:
        token = secrets.token_urlsafe(32)
        self._sessions[token] = _Session(
            account_key=key,
            expires_at=self.clock() + SESSION_TTL_SECONDS,
            encryption_key=encryption_key,
        )
        return AccountSession(nickname=self._accounts[key].nickname, token=token)

    @staticmethod
    def _associated_data(account_key: str, conversation_id: str) -> bytes:
        return f"{account_key}:{conversation_id}".encode()

    def _decrypt(
        self,
        session: _Session,
        conversation_id: str,
        conversation: _EncryptedRecord,
    ) -> tuple[SavedMessage, ...]:
        plaintext = AESGCM(session.encryption_key).decrypt(
            conversation.nonce,
            conversation.ciphertext,
            self._associated_data(session.account_key, conversation_id),
        )
        return tuple(SavedMessage(**message) for message in json.loads(plaintext))

    def _journal_entry(
        self,
        session: _Session,
        entry_id: str,
        stored: _EncryptedRecord,
    ) -> JournalEntry:
        payload = json.loads(
            AESGCM(session.encryption_key).decrypt(
                stored.nonce,
                stored.ciphertext,
                self._associated_data(session.account_key, f"journal:{entry_id}"),
            )
        )
        return JournalEntry(
            id=entry_id,
            entry_date=payload["date"],
            entry_time=payload["time"],
            description=payload["description"],
            updated_at=stored.saved_at,
        )

    def _summary(
        self,
        session: _Session,
        conversation_id: str,
        conversation: _EncryptedRecord,
    ) -> ConversationSummary:
        messages = self._decrypt(session, conversation_id, conversation)
        first_text = next(
            (message.text for message in messages if message.role == "user"),
            messages[0].text,
        )
        excerpt = " ".join(first_text.split())
        if len(excerpt) > EXCERPT_LENGTH:
            excerpt = f"{excerpt[:EXCERPT_LENGTH].rstrip()}…"
        return ConversationSummary(
            id=conversation_id,
            saved_at=conversation.saved_at,
            message_count=conversation.message_count,
            excerpt=excerpt,
        )
