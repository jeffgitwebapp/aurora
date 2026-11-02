import {
  authorizedRequest,
  formatError,
} from "../../../shared/session/sessionApi";

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
