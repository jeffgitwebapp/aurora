import {
  authorizedRequest,
  formatError,
} from "../../../shared/session/sessionApi";

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
