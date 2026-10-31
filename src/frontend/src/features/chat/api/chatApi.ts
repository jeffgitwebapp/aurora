const ENDPOINT = "/api/chat/messages";

export class ChatApiError extends Error { }

/** Envia a mensagem ao backend local e devolve a resposta textual. */
export async function sendMessage(message: string, signal?: AbortSignal): Promise<string> {
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

  if (
    typeof payload !== "object" ||
    payload === null ||
    typeof (payload as { reply?: unknown }).reply !== "string"
  ) {
    throw new ChatApiError("A resposta do servidor está em um formato inesperado.");
  }

  return (payload as { reply: string }).reply;
}
