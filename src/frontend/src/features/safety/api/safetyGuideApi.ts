export class SafetyGuideApiError extends Error { }

export interface SafetyGuideContent {
  sections: Array<{ title: string; paragraphs: string[] }>;
  inPreparation: boolean;
}

export async function getSafetyGuide(): Promise<SafetyGuideContent> {
  let response: Response;
  try {
    response = await fetch("/api/learning/safety-guide", {
      cache: "no-store",
      credentials: "omit",
    });
  } catch {
    throw new SafetyGuideApiError(
      "Não foi possível carregar o guia. Verifique a conexão e tente novamente.",
    );
  }
  if (!response.ok) {
    throw new SafetyGuideApiError(
      `Não foi possível carregar o guia (HTTP ${response.status}). Tente novamente.`,
    );
  }

  let payload: Record<string, unknown> | null;
  try {
    payload = (await response.json()) as Record<string, unknown> | null;
  } catch {
    throw new SafetyGuideApiError("A resposta do servidor não pôde ser lida.");
  }
  const sections = payload?.sections;
  if (
    !Array.isArray(sections) ||
    !sections.every(
      (section) =>
        typeof section?.title === "string" &&
        Array.isArray(section.paragraphs) &&
        section.paragraphs.every((paragraph: unknown) => typeof paragraph === "string"),
    ) ||
    typeof payload?.in_preparation !== "boolean"
  ) {
    throw new SafetyGuideApiError("A resposta do servidor está em um formato inesperado.");
  }
  return { sections, inPreparation: payload.in_preparation };
}
