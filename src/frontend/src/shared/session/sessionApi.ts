/** Núcleo da sessão da área logada, compartilhado pelas features que exigem conta. */

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

/** Requisição com o token da sessão; 401 vira SessionExpiredError. */
export async function authorizedRequest(
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

export const formatError = () =>
  new AccountApiError("A resposta do servidor está em um formato inesperado.");
