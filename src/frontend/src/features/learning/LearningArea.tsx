import { useCallback, useEffect, useRef, useState } from "react";

import type { AccountSectionProps } from "../../shared/session/SessionProvider";
import { AccountApiError, SessionExpiredError } from "../../shared/session/sessionApi";
import {
  getModule,
  LearningApiError,
  listModules,
  type LearningModule,
  type ModuleSummary,
} from "./api/learningApi";
import {
  listModuleProgress,
  saveModuleProgress,
  type ModuleProgress,
} from "./api/progressApi";

type ListState =
  | { kind: "loading" }
  | { kind: "error"; message: string }
  | { kind: "ready"; modules: ModuleSummary[]; progress: Map<string, ModuleProgress> };

const MEDIA_NOTICE =
  "Áudio e vídeo com legenda e transcrição: ainda não disponíveis nesta demonstração.";

function progressLabel(module: ModuleSummary, progress: ModuleProgress | undefined) {
  if (!progress) {
    return "Não iniciado";
  }
  if (progress.completed) {
    return "Concluído";
  }
  return `Parte ${progress.section + 1} de ${module.sectionCount}`;
}

export function LearningArea({
  token,
  onSessionExpired,
  onFocusChange: onReadingChange,
}: AccountSectionProps) {
  const [list, setList] = useState<ListState>({ kind: "loading" });
  const [reading, setReading] = useState<LearningModule | null>(null);
  const [section, setSection] = useState(0);
  const [completed, setCompleted] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [openError, setOpenError] = useState<string | null>(null);
  const headingRef = useRef<HTMLHeadingElement | null>(null);

  const loadList = useCallback(async () => {
    setList({ kind: "loading" });
    try {
      const [modules, progress] = await Promise.all([
        listModules(),
        listModuleProgress(token),
      ]);
      setList({
        kind: "ready",
        modules,
        progress: new Map(progress.map((item) => [item.moduleId, item])),
      });
    } catch (err: unknown) {
      if (err instanceof SessionExpiredError) {
        onSessionExpired(err.message);
        return;
      }
      setList({
        kind: "error",
        message:
          err instanceof LearningApiError || err instanceof AccountApiError
            ? err.message
            : "Não foi possível carregar os módulos.",
      });
    }
  }, [token, onSessionExpired]);

  useEffect(() => {
    void loadList();
  }, [loadList]);

  useEffect(() => {
    if (reading) {
      headingRef.current?.focus();
    }
  }, [reading, section, completed]);

  const persist = async (moduleId: string, nextSection: number, isCompleted: boolean) => {
    try {
      await saveModuleProgress(token, moduleId, nextSection, isCompleted);
      setSaveError(null);
    } catch (err: unknown) {
      if (err instanceof SessionExpiredError) {
        onSessionExpired(err.message);
        return;
      }
      setSaveError("Não foi possível salvar o progresso. Você pode continuar lendo.");
    }
  };

  const openModule = async (summary: ModuleSummary, progress: ModuleProgress | undefined) => {
    setOpenError(null);
    try {
      const module = await getModule(summary.id);
      const startSection =
        progress && !progress.completed
          ? Math.min(progress.section, module.sections.length - 1)
          : 0;
      setReading(module);
      setSection(startSection);
      setCompleted(false);
      setSaveError(null);
      onReadingChange(true);
      void persist(module.id, startSection, false);
    } catch (err: unknown) {
      setOpenError(
        err instanceof LearningApiError ? err.message : "Não foi possível abrir o módulo.",
      );
    }
  };

  const goTo = (nextSection: number) => {
    if (!reading) {
      return;
    }
    setSection(nextSection);
    void persist(reading.id, nextSection, false);
  };

  const finish = () => {
    if (!reading) {
      return;
    }
    setCompleted(true);
    void persist(reading.id, section, true);
  };

  const closeReader = () => {
    setReading(null);
    onReadingChange(false);
    void loadList();
  };

  if (reading) {
    const current = reading.sections[section];
    const isLast = section === reading.sections.length - 1;
    return (
      <section className="learning-reader" aria-labelledby="module-title">
        <button type="button" className="referral__back" onClick={closeReader}>
          ← Voltar aos módulos
        </button>
        <p className="account__history-meta">{reading.topic}</p>
        <h1 id="module-title" className="account__title" tabIndex={-1} ref={headingRef}>
          {completed ? "Módulo concluído" : reading.title}
        </h1>

        {completed ? (
          <>
            <p role="status">
              Você concluiu este módulo. Você decide o que fazer com o que leu.
            </p>
            <div className="account__actions">
              <button type="button" className="referral__submit" onClick={closeReader}>
                Voltar aos módulos
              </button>
            </div>
          </>
        ) : (
          <>
            <p className="questionnaire__progress">
              Parte {section + 1} de {reading.sections.length}
            </p>
            <h2 className="account__subtitle">{current.title}</h2>
            {current.paragraphs.map((paragraph, index) => (
              <p key={index} className="learning-reader__text">
                {paragraph}
              </p>
            ))}
            {current.source && (
              <p className="learning-reader__source">
                Fonte:{" "}
                <a href={current.source.url} target="_blank" rel="noreferrer">
                  {current.source.title}, {current.source.locator}
                </a>
              </p>
            )}
            <div className="account__actions">
              {section > 0 && (
                <button
                  type="button"
                  className="referral__action"
                  onClick={() => goTo(section - 1)}
                >
                  Anterior
                </button>
              )}
              {isLast ? (
                <button type="button" className="referral__submit" onClick={finish}>
                  Concluir módulo
                </button>
              ) : (
                <button
                  type="button"
                  className="referral__submit"
                  onClick={() => goTo(section + 1)}
                >
                  Próxima
                </button>
              )}
            </div>
          </>
        )}

        {saveError && (
          <p className="referral__error" role="alert">
            {saveError}
          </p>
        )}
        <p className="account__hint">{MEDIA_NOTICE}</p>
        <p className="account__demo" role="note">
          {reading.inPreparation
            ? "Demonstração: módulo em preparação, sem conteúdo aprovado por especialistas."
            : "Demonstração: trechos literais da lei escolhidos para teste, com revisão jurídica pendente. Não é orientação sobre o seu caso."}{" "}
          Você pode sair quando quiser; o progresso fica salvo.
        </p>
      </section>
    );
  }

  return (
    <div className="learning-list">
      {list.kind === "loading" && <p className="account__hint">Carregando módulos…</p>}
      {list.kind === "error" && (
        <div className="referral__alert" role="alert">
          <p>{list.message}</p>
          <button type="button" className="referral__action" onClick={loadList}>
            Tentar novamente
          </button>
        </div>
      )}
      {openError && (
        <p className="referral__error" role="alert">
          {openError}
        </p>
      )}
      {list.kind === "ready" && (
        <ul className="account__history">
          {list.modules.map((module) => {
            const progress = list.progress.get(module.id);
            return (
              <li key={module.id} className="account__history-item">
                <p className="account__history-meta">
                  {module.topic} · {progressLabel(module, progress)}
                  {module.inPreparation ? " · em preparação" : ""}
                </p>
                <p className="account__history-excerpt">{module.title}</p>
                <div className="account__actions">
                  <button
                    type="button"
                    className="referral__action"
                    aria-label={`${
                      !progress ? "Começar" : progress.completed ? "Rever" : "Continuar de onde parei"
                    }: ${module.title}`}
                    onClick={() => void openModule(module, progress)}
                  >
                    {!progress ? "Começar" : progress.completed ? "Rever" : "Continuar de onde parei"}
                  </button>
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
