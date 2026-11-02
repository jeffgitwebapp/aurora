export class LearningApiError extends Error { }

export interface ModuleSummary {
  id: string;
  title: string;
  topic: string;
  sectionCount: number;
  inPreparation: boolean;
  demo: boolean;
}

export interface ModuleSection {
  title: string;
  paragraphs: string[];
  source: { title: string; locator: string; url: string } | null;
}

export interface LearningModule extends ModuleSummary {
  sections: ModuleSection[];
}

async function getJson(endpoint: string): Promise<unknown> {
  let response: Response;
  try {
    response = await fetch(endpoint, { cache: "no-store", credentials: "omit" });
  } catch {
    throw new LearningApiError(
      "Não foi possível carregar os módulos. Verifique a conexão e tente novamente.",
    );
  }
  if (!response.ok) {
    throw new LearningApiError(
      `Não foi possível carregar os módulos (HTTP ${response.status}). Tente novamente.`,
    );
  }
  try {
    return await response.json();
  } catch {
    throw new LearningApiError("A resposta do servidor não pôde ser lida.");
  }
}

const formatError = () =>
  new LearningApiError("A resposta do servidor está em um formato inesperado.");

function parseSummary(value: unknown): ModuleSummary {
  const module = value as Record<string, unknown> | null;
  if (
    typeof module?.id !== "string" ||
    typeof module.title !== "string" ||
    typeof module.topic !== "string" ||
    typeof module.section_count !== "number" ||
    typeof module.in_preparation !== "boolean" ||
    typeof module.demo !== "boolean"
  ) {
    throw formatError();
  }
  return {
    id: module.id,
    title: module.title,
    topic: module.topic,
    sectionCount: module.section_count,
    inPreparation: module.in_preparation,
    demo: module.demo,
  };
}

function parseSection(value: unknown): ModuleSection {
  const section = value as Record<string, unknown> | null;
  const source = section?.source as Record<string, unknown> | null | undefined;
  if (
    typeof section?.title !== "string" ||
    !Array.isArray(section.paragraphs) ||
    !section.paragraphs.every((paragraph) => typeof paragraph === "string") ||
    !(
      source === null ||
      (typeof source?.title === "string" &&
        typeof source.locator === "string" &&
        typeof source.url === "string" &&
        source.url.startsWith("https://"))
    )
  ) {
    throw formatError();
  }
  return {
    title: section.title,
    paragraphs: section.paragraphs as string[],
    source: source
      ? { title: source.title as string, locator: source.locator as string, url: source.url as string }
      : null,
  };
}

export async function listModules(): Promise<ModuleSummary[]> {
  const payload = (await getJson("/api/learning/modules")) as Record<string, unknown> | null;
  if (!Array.isArray(payload?.modules)) {
    throw formatError();
  }
  return payload.modules.map(parseSummary);
}

export async function getModule(id: string): Promise<LearningModule> {
  const payload = (await getJson(
    `/api/learning/modules/${encodeURIComponent(id)}`,
  )) as Record<string, unknown> | null;
  if (!Array.isArray(payload?.sections) || payload.sections.length === 0) {
    throw formatError();
  }
  return { ...parseSummary(payload), sections: payload.sections.map(parseSection) };
}
