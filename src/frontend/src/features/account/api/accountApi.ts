import {
  authorizedRequest,
  formatError,
} from "../../../shared/session/sessionApi";

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
