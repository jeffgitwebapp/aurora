const ENDPOINT = "/api/chat/messages";

export class ChatApiError extends Error { }

export type TriageStatus = "acute" | "no_acute_signal" | "indeterminate";

export type TriageSignal =
  | "suicidal_ideation"
  | "ongoing_assault"
  | "death_threat"
  | "weapon_present";

export interface ChatApiResult {
  reply: string | null;
  guidance: string | null;
  triageStatus: TriageStatus;
  signals: TriageSignal[];
}

function isTriageStatus(value: unknown): value is TriageStatus {
  return (
    value === "acute" ||
    value === "no_acute_signal" ||
    value === "indeterminate"
  );
}

function isTriageSignal(value: unknown): value is TriageSignal {
  return (
    value === "suicidal_ideation" ||
    value === "ongoing_assault" ||
    value === "death_threat" ||
    value === "weapon_present"
  );
}

/** Envia a mensagem ao backend e devolve a resposta e o estado de triagem do mock. */
export async function sendMessage(
  message: string,
  signal?: AbortSignal,
): Promise<ChatApiResult> {
  let response: Response;

  try {
    response = await fetch(ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
      cache: "no-store",
      credentials: "omit",
      signal,
    });
  } catch {
    throw new ChatApiError(
      "Não foi possível conectar ao serviço. Verifique a conexão e tente novamente.",
    );
  }

  if (!response.ok) {
    throw new ChatApiError(
      `O servidor recusou a mensagem (HTTP ${response.status}). Tente novamente.`,
    );
  }

  let payload: unknown;

  try {
    payload = await response.json();
  } catch {
    throw new ChatApiError("A resposta do servidor não pôde ser lida.");
  }

  if (typeof payload !== "object" || payload === null) {
    throw new ChatApiError("A resposta do servidor está em um formato inesperado.");
  }

  const result = payload as {
    reply?: unknown;
    guidance?: unknown;
    triage_status?: unknown;
    signals?: unknown;
  };
  if (
    !isTriageStatus(result.triage_status) ||
    !Array.isArray(result.signals) ||
    !result.signals.every(isTriageSignal) ||
    !(typeof result.reply === "string" || result.reply === null) ||
    !(typeof result.guidance === "string" || result.guidance === null)
  ) {
    throw new ChatApiError("A resposta do servidor está em um formato inesperado.");
  }

  if (
    (result.triage_status === "no_acute_signal" &&
      (typeof result.reply !== "string" || result.guidance !== null)) ||
    (result.triage_status !== "no_acute_signal" &&
      (result.reply !== null || typeof result.guidance !== "string"))
  ) {
    throw new ChatApiError("A resposta do servidor está em um formato inesperado.");
  }

  return {
    reply: result.reply,
    guidance: result.guidance,
    triageStatus: result.triage_status,
    signals: result.signals,
  };
}
