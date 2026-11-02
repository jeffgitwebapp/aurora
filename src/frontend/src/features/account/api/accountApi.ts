export class AccountApiError extends Error { }

export interface AccountSession {
  nickname: string;
  token: string;
}

const STATUS_MESSAGES: Record<number, string> = {
  401: "Apelido ou senha incorretos.",
  409: "Este apelido já está em uso. Escolha outro.",
  429: "Muitas tentativas. Aguarde 1 minuto e tente novamente.",
};

async function postCredentials(
  endpoint: string,
  nickname: string,
  password: string,
): Promise<AccountSession> {
  let response: Response;
  try {
    response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nickname, password }),
      cache: "no-store",
      credentials: "omit",
    });
  } catch {
    throw new AccountApiError(
      "Não foi possível conectar ao serviço. Verifique a conexão e tente novamente.",
    );
  }

  let payload: unknown = null;
  try {
    payload = await response.json();
  } catch {
    // Mantém payload nulo; o status decide a mensagem abaixo.
  }

  if (!response.ok) {
    const detail = (payload as { detail?: unknown } | null)?.detail;
    throw new AccountApiError(
      STATUS_MESSAGES[response.status] ??
        (response.status === 422 && typeof detail === "string"
          ? detail
          : `Não foi possível concluir (HTTP ${response.status}). Tente novamente.`),
    );
  }

  const session = payload as Record<string, unknown> | null;
  if (typeof session?.nickname !== "string" || typeof session.token !== "string") {
    throw new AccountApiError("A resposta do servidor está em um formato inesperado.");
  }
  return { nickname: session.nickname, token: session.token };
}

export function registerAccount(nickname: string, password: string) {
  return postCredentials("/api/accounts", nickname, password);
}

export function login(nickname: string, password: string) {
  return postCredentials("/api/sessions", nickname, password);
}

/** Encerra a sessão no servidor sem bloquear a interface (também usado na Saída Rápida). */
export function logout(token: string): void {
  void fetch("/api/sessions/current", {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
    credentials: "omit",
    keepalive: true,
  }).catch(() => undefined);
}

/** Sessão encerrada ou expirada no servidor: a interface deve voltar ao estado sem conta. */
export class SessionExpiredError extends AccountApiError { }

export interface ConversationSummary {
  id: string;
  savedAt: string;
  messageCount: number;
  excerpt: string;
}

export interface SavedMessage {
  role: "user" | "assistant";
  text: string;
}

async function authorizedRequest(
  token: string,
  endpoint: string,
  init: RequestInit = {},
): Promise<unknown> {
  let response: Response;
  try {
    response = await fetch(endpoint, {
      ...init,
      headers: { ...init.headers, Authorization: `Bearer ${token}` },
      cache: "no-store",
      credentials: "omit",
    });
  } catch {
    throw new AccountApiError(
      "Não foi possível conectar ao serviço. Verifique a conexão e tente novamente.",
    );
  }
  if (response.status === 401) {
    throw new SessionExpiredError("Sua sessão terminou. Entre de novo para continuar.");
  }
  if (response.status === 204) {
    return null;
  }
  let payload: unknown = null;
  try {
    payload = await response.json();
  } catch {
    // O status decide a mensagem abaixo.
  }
  if (!response.ok) {
    const detail = (payload as { detail?: unknown } | null)?.detail;
    throw new AccountApiError(
      typeof detail === "string" && response.status < 500
        ? detail
        : `Não foi possível concluir (HTTP ${response.status}). Tente novamente.`,
    );
  }
  return payload;
}

const formatError = () =>
  new AccountApiError("A resposta do servidor está em um formato inesperado.");

function parseSummary(value: unknown): ConversationSummary {
  const summary = value as Record<string, unknown> | null;
  if (
    typeof summary?.id !== "string" ||
    typeof summary.saved_at !== "string" ||
    typeof summary.message_count !== "number" ||
    typeof summary.excerpt !== "string"
  ) {
    throw formatError();
  }
  return {
    id: summary.id,
    savedAt: summary.saved_at,
    messageCount: summary.message_count,
    excerpt: summary.excerpt,
  };
}

function isSavedMessage(value: unknown): value is SavedMessage {
  const message = value as Record<string, unknown> | null;
  return (
    (message?.role === "user" || message?.role === "assistant") &&
    typeof message.text === "string"
  );
}

/** Guarda só papel e texto das mensagens; o servidor cifra com a chave da sessão. */
export async function saveConversation(
  token: string,
  messages: SavedMessage[],
): Promise<ConversationSummary> {
  return parseSummary(
    await authorizedRequest(token, "/api/account/conversations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages }),
    }),
  );
}

export async function listConversations(token: string): Promise<ConversationSummary[]> {
  const payload = (await authorizedRequest(token, "/api/account/conversations")) as Record<
    string,
    unknown
  > | null;
  if (!Array.isArray(payload?.conversations)) {
    throw formatError();
  }
  return payload.conversations.map(parseSummary);
}

export async function getConversation(token: string, id: string): Promise<SavedMessage[]> {
  const payload = (await authorizedRequest(
    token,
    `/api/account/conversations/${encodeURIComponent(id)}`,
  )) as Record<string, unknown> | null;
  const messages = payload?.messages;
  if (!Array.isArray(messages) || !messages.every(isSavedMessage)) {
    throw formatError();
  }
  return messages;
}

export async function deleteConversation(token: string, id: string): Promise<void> {
  await authorizedRequest(token, `/api/account/conversations/${encodeURIComponent(id)}`, {
    method: "DELETE",
  });
}

export async function deleteAccount(token: string): Promise<void> {
  await authorizedRequest(token, "/api/accounts/current", { method: "DELETE" });
}

export interface ModuleProgress {
  moduleId: string;
  section: number;
  completed: boolean;
}

function parseProgress(value: unknown): ModuleProgress {
  const progress = value as Record<string, unknown> | null;
  if (
    typeof progress?.module_id !== "string" ||
    typeof progress.section !== "number" ||
    typeof progress.completed !== "boolean"
  ) {
    throw formatError();
  }
  return {
    moduleId: progress.module_id,
    section: progress.section,
    completed: progress.completed,
  };
}

export async function listModuleProgress(token: string): Promise<ModuleProgress[]> {
  const payload = (await authorizedRequest(token, "/api/account/module-progress")) as Record<
    string,
    unknown
  > | null;
  if (!Array.isArray(payload?.progress)) {
    throw formatError();
  }
  return payload.progress.map(parseProgress);
}

export async function saveModuleProgress(
  token: string,
  moduleId: string,
  section: number,
  completed: boolean,
): Promise<ModuleProgress> {
  return parseProgress(
    await authorizedRequest(
      token,
      `/api/account/module-progress/${encodeURIComponent(moduleId)}`,
      {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ section, completed }),
      },
    ),
  );
}

export interface JournalEntry {
  id: string;
  date: string;
  time: string | null;
  description: string;
}

export interface JournalEntryInput {
  date: string;
  time: string | null;
  description: string;
}

function parseJournalEntry(value: unknown): JournalEntry {
  const entry = value as Record<string, unknown> | null;
  if (
    typeof entry?.id !== "string" ||
    typeof entry.date !== "string" ||
    !(typeof entry.time === "string" || entry.time === null) ||
    typeof entry.description !== "string"
  ) {
    throw formatError();
  }
  return { id: entry.id, date: entry.date, time: entry.time, description: entry.description };
}

export async function listJournal(token: string): Promise<JournalEntry[]> {
  const payload = (await authorizedRequest(token, "/api/account/journal")) as Record<
    string,
    unknown
  > | null;
  if (!Array.isArray(payload?.entries)) {
    throw formatError();
  }
  return payload.entries.map(parseJournalEntry);
}

/** Cria (sem id) ou edita um registro; o servidor cifra com a chave da sessão. */
export async function saveJournalEntry(
  token: string,
  id: string | null,
  input: JournalEntryInput,
): Promise<JournalEntry> {
  return parseJournalEntry(
    await authorizedRequest(
      token,
      id ? `/api/account/journal/${encodeURIComponent(id)}` : "/api/account/journal",
      {
        method: id ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(input),
      },
    ),
  );
}

export async function deleteJournalEntry(token: string, id: string): Promise<void> {
  await authorizedRequest(token, `/api/account/journal/${encodeURIComponent(id)}`, {
    method: "DELETE",
  });
}

export interface TrustedContact {
  name: string;
  phone: string;
}

export interface SafetyPlan {
  contacts: TrustedContact[];
  notes: string;
  updatedAt: string | null;
}

function parseSafetyPlan(value: unknown): SafetyPlan {
  const plan = value as Record<string, unknown> | null;
  const contacts = plan?.contacts;
  if (
    !Array.isArray(contacts) ||
    !contacts.every(
      (contact) =>
        typeof (contact as TrustedContact | null)?.name === "string" &&
        typeof (contact as TrustedContact).phone === "string",
    ) ||
    typeof plan?.notes !== "string" ||
    !(typeof plan.updated_at === "string" || plan.updated_at === null)
  ) {
    throw formatError();
  }
  return {
    contacts: contacts as TrustedContact[],
    notes: plan.notes,
    updatedAt: plan.updated_at,
  };
}

export async function getSafetyPlan(token: string): Promise<SafetyPlan> {
  return parseSafetyPlan(await authorizedRequest(token, "/api/account/safety-plan"));
}

/** Salva contatos e anotações; o servidor cifra com a chave da sessão. */
export async function saveSafetyPlan(
  token: string,
  contacts: TrustedContact[],
  notes: string,
): Promise<SafetyPlan> {
  return parseSafetyPlan(
    await authorizedRequest(token, "/api/account/safety-plan", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ contacts, notes }),
    }),
  );
}
