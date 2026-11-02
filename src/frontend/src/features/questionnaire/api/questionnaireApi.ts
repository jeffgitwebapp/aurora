const QUESTIONS_ENDPOINT = "/api/questionnaire/questions";
const RESULTS_ENDPOINT = "/api/questionnaire/results";

export class QuestionnaireApiError extends Error { }

export interface AnswerOption {
  id: string;
  label: string;
}

export interface Question {
  id: string;
  title: string;
  options: AnswerOption[];
}

export type HelpType = "report" | "legal" | "psychological" | "peer";

export interface QuestionnaireResult {
  band: "A" | "B" | "C";
  helpType: HelpType | null;
  demo: boolean;
}

async function requestJson(input: string, init?: RequestInit): Promise<unknown> {
  let response: Response;
  try {
    response = await fetch(input, { cache: "no-store", credentials: "omit", ...init });
  } catch {
    throw new QuestionnaireApiError(
      "Não foi possível carregar o questionário. Verifique a conexão e tente novamente.",
    );
  }
  if (!response.ok) {
    throw new QuestionnaireApiError(
      `Não foi possível concluir esta etapa (HTTP ${response.status}). Tente novamente.`,
    );
  }
  try {
    return await response.json();
  } catch {
    throw new QuestionnaireApiError("A resposta do servidor não pôde ser lida.");
  }
}

const formatError = () =>
  new QuestionnaireApiError("A resposta do servidor está em um formato inesperado.");

function isOption(value: unknown): value is AnswerOption {
  const option = value as Record<string, unknown> | null;
  return (
    typeof option === "object" &&
    option !== null &&
    typeof option.id === "string" &&
    typeof option.label === "string"
  );
}

function isQuestion(value: unknown): value is Question {
  const question = value as Record<string, unknown> | null;
  return (
    typeof question === "object" &&
    question !== null &&
    typeof question.id === "string" &&
    typeof question.title === "string" &&
    Array.isArray(question.options) &&
    question.options.length > 0 &&
    question.options.every(isOption)
  );
}

export async function fetchQuestions(signal?: AbortSignal): Promise<Question[]> {
  const payload = (await requestJson(QUESTIONS_ENDPOINT, { signal })) as Record<
    string,
    unknown
  > | null;
  const questions = payload?.questions;
  if (!Array.isArray(questions) || questions.length === 0 || !questions.every(isQuestion)) {
    throw formatError();
  }
  return questions;
}

/** Envia as respostas para o cálculo da faixa; nada é guardado no aparelho nem no servidor. */
export async function submitAnswers(
  answers: Record<string, string>,
  signal?: AbortSignal,
): Promise<QuestionnaireResult> {
  const payload = (await requestJson(RESULTS_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ answers }),
    signal,
  })) as Record<string, unknown> | null;
  const band = payload?.band;
  const helpType = payload?.help_type;
  if (
    (band !== "A" && band !== "B" && band !== "C") ||
    !(
      helpType === null ||
      helpType === "report" ||
      helpType === "legal" ||
      helpType === "psychological" ||
      helpType === "peer"
    ) ||
    typeof payload?.demo !== "boolean"
  ) {
    throw formatError();
  }
  return { band, helpType, demo: payload.demo };
}
