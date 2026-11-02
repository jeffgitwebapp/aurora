import {
  authorizedRequest,
  formatError,
} from "../../../shared/session/sessionApi";

export interface ModuleProgress {
  moduleId: string;
  section: number;
  completed: boolean;
}

function parseProgress(value: unknown): ModuleProgress {
  const progress = value as Record<string, unknown> | null;
  if (
    typeof progress?.module_id !== "string" ||
    typeof progress.section !== "number" ||
    typeof progress.completed !== "boolean"
  ) {
    throw formatError();
  }
  return {
    moduleId: progress.module_id,
    section: progress.section,
    completed: progress.completed,
  };
}

export async function listModuleProgress(token: string): Promise<ModuleProgress[]> {
  const payload = (await authorizedRequest(token, "/api/account/module-progress")) as Record<
    string,
    unknown
  > | null;
  if (!Array.isArray(payload?.progress)) {
    throw formatError();
  }
  return payload.progress.map(parseProgress);
}

export async function saveModuleProgress(
  token: string,
  moduleId: string,
  section: number,
  completed: boolean,
): Promise<ModuleProgress> {
  return parseProgress(
    await authorizedRequest(
      token,
      `/api/account/module-progress/${encodeURIComponent(moduleId)}`,
      {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ section, completed }),
      },
    ),
  );
}
