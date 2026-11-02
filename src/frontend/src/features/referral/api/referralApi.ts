const ENDPOINT = "/api/referral/recommendations";

export class ReferralApiError extends Error { }

export type RecommendationStatus = "found" | "no_verified_result";

export interface ServiceOption {
  id: string;
  name: string;
  priority: number;
  category: string;
  description: string;
  contact: string | null;
  hours: string | null;
  cost: string | null;
  lastVerifiedAt: string | null;
  demo: boolean;
}

export interface RecommendationResult {
  status: RecommendationStatus;
  city: string;
  state: string;
  services: ServiceOption[];
  demo: boolean;
}

const isNullableString = (value: unknown): value is string | null =>
  typeof value === "string" || value === null;

function parseService(value: unknown): ServiceOption | null {
  if (typeof value !== "object" || value === null) {
    return null;
  }
  const service = value as Record<string, unknown>;
  if (
    typeof service.id !== "string" ||
    typeof service.name !== "string" ||
    typeof service.priority !== "number" ||
    typeof service.category !== "string" ||
    typeof service.description !== "string" ||
    !isNullableString(service.contact) ||
    !isNullableString(service.hours) ||
    !isNullableString(service.cost) ||
    !isNullableString(service.last_verified_at) ||
    typeof service.demo !== "boolean"
  ) {
    return null;
  }
  return {
    id: service.id,
    name: service.name,
    priority: service.priority,
    category: service.category,
    description: service.description,
    contact: service.contact,
    hours: service.hours,
    cost: service.cost,
    lastVerifiedAt: service.last_verified_at,
    demo: service.demo,
  };
}

/** Consulta o catálogo com cidade/UF; coordenadas nunca são enviadas. */
export async function recommendServices(
  city: string,
  state: string,
  signal?: AbortSignal,
): Promise<RecommendationResult> {
  let response: Response;
  try {
    response = await fetch(ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ city, state }),
      cache: "no-store",
      credentials: "omit",
      signal,
    });
  } catch {
    throw new ReferralApiError(
      "Não foi possível consultar os serviços. Verifique a conexão e tente novamente.",
    );
  }

  if (!response.ok) {
    throw new ReferralApiError(
      `Não foi possível consultar os serviços (HTTP ${response.status}). Tente novamente.`,
    );
  }

  let payload: unknown;
  try {
    payload = await response.json();
  } catch {
    throw new ReferralApiError("A resposta do servidor não pôde ser lida.");
  }

  const result = (typeof payload === "object" && payload !== null ? payload : {}) as Record<
    string,
    unknown
  >;
  const services = Array.isArray(result.services) ? result.services.map(parseService) : null;
  const status = result.status;
  if (
    (status !== "found" && status !== "no_verified_result") ||
    typeof result.city !== "string" ||
    typeof result.state !== "string" ||
    typeof result.demo !== "boolean" ||
    services === null ||
    services.some((service) => service === null) ||
    services.length > 3 ||
    (status === "found") !== services.length > 0
  ) {
    throw new ReferralApiError("A resposta do servidor está em um formato inesperado.");
  }

  return {
    status,
    city: result.city,
    state: result.state,
    services: services as ServiceOption[],
    demo: result.demo,
  };
}
