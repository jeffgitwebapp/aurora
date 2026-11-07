const ENDPOINT = "/api/chat/messages";

export class ChatApiError extends Error { }

export type TriageStatus = "acute" | "no_acute_signal" | "indeterminate";

export type TriageSignal =
  | "suicidal_ideation"
  | "ongoing_assault"
  | "death_threat"
  | "weapon_present";

export type ScopeStatus = "allowed" | "out_of_scope";

export type OutOfScopeCategory =
  | "diagnosis"
  | "prescription"
  | "individual_legal_opinion";

export type ContentOffer = "safety_guide";

export type KnowledgeStatus = "found" | "no_source";

export type ConversationKind = "greeting" | "thanks" | "farewell";

export interface SourceReference {
  id: string;
  title: string;
  locator: string;
  publisher: string;
  url: string;
  version: string | null;
}

export interface ChatApiResult {
  reply: string | null;
  guidance: string | null;
  triageStatus: TriageStatus;
  signals: TriageSignal[];
  scopeStatus: ScopeStatus | null;
  outOfScopeCategory: OutOfScopeCategory | null;
  offer: ContentOffer | null;
  knowledgeStatus: KnowledgeStatus | null;
  conversation: ConversationKind | null;
  sources: SourceReference[];
  demo: boolean;
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

function isScopeStatus(value: unknown): value is ScopeStatus {
  return value === "allowed" || value === "out_of_scope";
}

function isOutOfScopeCategory(value: unknown): value is OutOfScopeCategory {
  return (
    value === "diagnosis" ||
    value === "prescription" ||
    value === "individual_legal_opinion"
  );
}

function isKnowledgeStatus(value: unknown): value is KnowledgeStatus {
  return value === "found" || value === "no_source";
}

function isConversationKind(value: unknown): value is ConversationKind {
  return value === "greeting" || value === "thanks" || value === "farewell";
}

function isSourceReference(value: unknown): value is SourceReference {
  if (typeof value !== "object" || value === null) {
    return false;
  }
  const source = value as Record<string, unknown>;
  return (
    ["id", "title", "locator", "publisher"].every(
      (field) => typeof source[field] === "string" && source[field] !== "",
    ) &&
    typeof source.url === "string" &&
    source.url.startsWith("https://") &&
    (typeof source.version === "string" || source.version === null)
  );
}

/** Envia a mensagem ao backend e devolve triagem, resposta e fontes do protótipo. */
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
    scope_status?: unknown;
    out_of_scope_category?: unknown;
    offer?: unknown;
    knowledge_status?: unknown;
    conversation?: unknown;
    sources?: unknown;
    demo?: unknown;
  };
  if (
    !isTriageStatus(result.triage_status) ||
    !Array.isArray(result.signals) ||
    !result.signals.every(isTriageSignal) ||
    !(typeof result.reply === "string" || result.reply === null) ||
    !(typeof result.guidance === "string" || result.guidance === null) ||
    !(isScopeStatus(result.scope_status) || result.scope_status === null) ||
    !(
      isOutOfScopeCategory(result.out_of_scope_category) ||
      result.out_of_scope_category === null
    ) ||
    !(result.offer === "safety_guide" || result.offer === null) ||
    !(isKnowledgeStatus(result.knowledge_status) || result.knowledge_status === null) ||
    !(
      isConversationKind(result.conversation) ||
      result.conversation === null ||
      result.conversation === undefined
    ) ||
    !Array.isArray(result.sources) ||
    !result.sources.every(isSourceReference) ||
    typeof result.demo !== "boolean"
  ) {
    throw new ChatApiError("A resposta do servidor está em um formato inesperado.");
  }

  const conversation = isConversationKind(result.conversation) ? result.conversation : null;
  const isAllowed =
    result.scope_status === "allowed" && result.out_of_scope_category === null;
  const isConversation =
    isAllowed &&
    conversation !== null &&
    result.offer === null &&
    result.knowledge_status === null &&
    typeof result.reply === "string" &&
    result.sources.length === 0;
  const isOffer =
    isAllowed &&
    result.offer !== null &&
    result.knowledge_status === null &&
    result.reply === null &&
    result.sources.length === 0;
  const isOutOfScope =
    result.offer === null &&
    result.scope_status === "out_of_scope" &&
    result.out_of_scope_category !== null &&
    result.knowledge_status === null &&
    result.reply === null &&
    result.sources.length === 0;
  const isFound =
    isAllowed &&
    result.offer === null &&
    result.knowledge_status === "found" &&
    typeof result.reply === "string" &&
    result.sources.length > 0;
  const isNoSource =
    isAllowed &&
    result.offer === null &&
    result.knowledge_status === "no_source" &&
    result.reply === null &&
    result.sources.length === 0;
  const isBlockedByTriage =
    result.offer === null &&
    result.scope_status === null &&
    result.out_of_scope_category === null &&
    result.knowledge_status === null &&
    result.reply === null &&
    result.sources.length === 0 &&
    typeof result.guidance === "string";
  if (
    (result.triage_status === "no_acute_signal" &&
      (result.guidance !== null ||
        !(isConversation || isOffer || isOutOfScope || isFound || isNoSource))) ||
    (result.triage_status !== "no_acute_signal" && !isBlockedByTriage) ||
    (conversation !== null && !isConversation)
  ) {
    throw new ChatApiError("A resposta do servidor está em um formato inesperado.");
  }

  return {
    reply: result.reply,
    guidance: result.guidance,
    triageStatus: result.triage_status,
    signals: result.signals,
    scopeStatus: result.scope_status,
    outOfScopeCategory: result.out_of_scope_category,
    offer: result.offer,
    knowledgeStatus: result.knowledge_status,
    conversation,
    sources: result.sources,
    demo: result.demo,
  };
}
