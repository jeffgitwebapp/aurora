import { useCallback, useEffect, useRef, useState, type ChangeEvent, type FormEvent } from "react";

import {
  AccountApiError,
  deleteJournalEntry,
  listJournal,
  saveJournalEntry,
  SessionExpiredError,
  type JournalEntry,
} from "../account/api/accountApi";

interface JournalAreaProps {
  token: string;
  onSessionExpired: (message: string) => void;
}

interface Draft {
  id: string | null;
  date: string;
  time: string;
  description: string;
  attachment: { name: string; size: number } | null;
}

type ListState =
  | { kind: "loading" }
  | { kind: "error"; message: string }
  | { kind: "ready"; entries: JournalEntry[] };

const MAX_DESCRIPTION = 4000;

function today(): string {
  const now = new Date();
  const offset = now.getTimezoneOffset() * 60000;
  return new Date(now.getTime() - offset).toISOString().slice(0, 10);
}

function formatEntryDate(entry: { date: string; time: string | null }) {
  const [year, month, day] = entry.date.split("-");
  return `${day}/${month}/${year}${entry.time ? ` às ${entry.time}` : ""}`;
}

function formatSize(bytes: number) {
  return bytes < 1024 * 1024
    ? `${Math.max(1, Math.round(bytes / 1024))} KB`
    : `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function JournalArea({ token, onSessionExpired }: JournalAreaProps) {
  const [list, setList] = useState<ListState>({ kind: "loading" });
  const [draft, setDraft] = useState<Draft | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [exportStep, setExportStep] = useState<"warning" | "preview" | null>(null);
  const formHeadingRef = useRef<HTMLHeadingElement | null>(null);
  const previewHeadingRef = useRef<HTMLHeadingElement | null>(null);

  const handleError = useCallback(
    (err: unknown, fallback: string, setError: (message: string) => void) => {
      if (err instanceof SessionExpiredError) {
        onSessionExpired(err.message);
        return;
      }
      setError(err instanceof AccountApiError && fallback === "" ? err.message : fallback);
    },
    [onSessionExpired],
  );

  const loadEntries = useCallback(async () => {
    setList({ kind: "loading" });
    try {
      setList({ kind: "ready", entries: await listJournal(token) });
    } catch (err: unknown) {
      handleError(err, "Não foi possível carregar o diário.", (message) =>
        setList({ kind: "error", message }),
      );
    }
  }, [token, handleError]);

  useEffect(() => {
    void loadEntries();
  }, [loadEntries]);

  const draftKey = draft ? (draft.id ?? "new") : null;
  useEffect(() => {
    if (draftKey) {
      formHeadingRef.current?.focus();
    }
  }, [draftKey]);

  useEffect(() => {
    if (exportStep === "preview") {
      previewHeadingRef.current?.focus();
    }
  }, [exportStep]);

  const openForm = (entry: JournalEntry | null) => {
    setNotice(null);
    setFormError(null);
    setExportStep(null);
    setDraft(
      entry
        ? {
            id: entry.id,
            date: entry.date,
            time: entry.time ?? "",
            description: entry.description,
            attachment: null,
          }
        : { id: null, date: today(), time: "", description: "", attachment: null },
    );
  };

  const handleAttachment = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    // Anexo simulado: só nome e tamanho são lidos; o arquivo é descartado.
    event.target.value = "";
    if (file && draft) {
      setDraft({ ...draft, attachment: { name: file.name, size: file.size } });
    }
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!draft) {
      return;
    }
    if (!draft.date || draft.date > today()) {
      setFormError("Informe uma data que não seja no futuro.");
      return;
    }
    if (!draft.description.trim()) {
      setFormError("Escreva uma descrição.");
      return;
    }
    setIsSaving(true);
    setFormError(null);
    try {
      await saveJournalEntry(token, draft.id, {
        date: draft.date,
        time: draft.time || null,
        description: draft.description,
      });
      setNotice(draft.id ? "Registro atualizado." : "Registro salvo.");
      setDraft(null);
      await loadEntries();
    } catch (err: unknown) {
      handleError(err, "", (message) => setFormError(`${message} Nada foi salvo.`));
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    setActionError(null);
    try {
      await deleteJournalEntry(token, id);
      setConfirmDeleteId(null);
      setNotice("Registro excluído.");
      await loadEntries();
    } catch (err: unknown) {
      handleError(err, "Não foi possível excluir o registro. Nada foi apagado.", setActionError);
    }
  };

  const entries = list.kind === "ready" ? list.entries : [];

  return (
    <div className="journal">
      <p className="account__hint">
        Um registro pessoal com data, hora e descrição. Você escreve só o que quiser.
      </p>
      {notice && (
        <p className="account__notice" role="status">
          {notice}
        </p>
      )}

      {draft ? (
        <form className="account__form journal__form" onSubmit={handleSubmit} noValidate>
          <h3 className="account__subtitle" tabIndex={-1} ref={formHeadingRef}>
            {draft.id ? "Editar registro" : "Novo registro"}
          </h3>
          <p className="account__warning">
            Antes de salvar: o registro fica cifrado com uma chave derivada da sua senha, na
            memória do servidor de demonstração, e some quando ele reinicia. Não escreva dados
            reais. O Aurora não garante segurança se o aparelho for monitorado.
          </p>

          <label htmlFor="journal-date">Data</label>
          <input
            id="journal-date"
            className="referral__input"
            type="date"
            max={today()}
            value={draft.date}
            onChange={(event) => setDraft({ ...draft, date: event.target.value })}
          />

          <label htmlFor="journal-time">Hora (opcional)</label>
          <input
            id="journal-time"
            className="referral__input"
            type="time"
            value={draft.time}
            onChange={(event) => setDraft({ ...draft, time: event.target.value })}
          />

          <label htmlFor="journal-description">Descrição</label>
          <textarea
            id="journal-description"
            className="referral__input journal__textarea"
            rows={6}
            maxLength={MAX_DESCRIPTION}
            value={draft.description}
            onChange={(event) => setDraft({ ...draft, description: event.target.value })}
            aria-describedby="journal-description-count"
          />
          <p className="account__hint" id="journal-description-count">
            {draft.description.length} de {MAX_DESCRIPTION} caracteres
          </p>

          <label htmlFor="journal-attachment">Anexo de foto ou áudio (simulado)</label>
          <input
            id="journal-attachment"
            type="file"
            accept="image/*,audio/*"
            onChange={handleAttachment}
            aria-describedby="journal-attachment-note"
          />
          <p className="account__hint" id="journal-attachment-note">
            {draft.attachment
              ? `Anexo simulado: ${draft.attachment.name} (${formatSize(draft.attachment.size)}). O arquivo não foi enviado nem será guardado.`
              : "Demonstração: o arquivo escolhido não é enviado nem guardado; só o nome e o tamanho aparecem aqui."}
          </p>
          {draft.attachment && (
            <button
              type="button"
              className="referral__action journal__remove"
              onClick={() => setDraft({ ...draft, attachment: null })}
            >
              Remover anexo
            </button>
          )}

          {formError && (
            <p className="referral__error" role="alert">
              {formError}
            </p>
          )}
          <div className="account__actions">
            <button type="submit" className="referral__submit" disabled={isSaving}>
              {isSaving ? "Salvando..." : "Salvar registro"}
            </button>
            <button
              type="button"
              className="referral__action"
              onClick={() => {
                setDraft(null);
                setNotice("Nada foi salvo.");
              }}
            >
              Cancelar
            </button>
          </div>
        </form>
      ) : (
        <div className="account__actions">
          <button type="button" className="referral__submit" onClick={() => openForm(null)}>
            Novo registro
          </button>
          <button
            type="button"
            className="referral__action"
            disabled={entries.length === 0}
            onClick={() => setExportStep("warning")}
          >
            Exportar (demonstração)
          </button>
        </div>
      )}

      {exportStep === "warning" && (
        <div className="account__confirm" role="group" aria-label="Aviso antes de exportar">
          <p>
            Antes de exportar: um arquivo baixado pode ficar no aparelho e ser visto por quem
            tiver acesso a ele. A exportação não garante valor jurídico. Nesta demonstração,
            nada é baixado: você verá só uma prévia na tela.
          </p>
          <div className="account__actions">
            <button
              type="button"
              className="referral__submit"
              onClick={() => setExportStep("preview")}
            >
              Continuar
            </button>
            <button type="button" className="referral__action" onClick={() => setExportStep(null)}>
              Cancelar
            </button>
          </div>
        </div>
      )}

      {exportStep === "preview" && (
        <section className="journal__preview" aria-labelledby="journal-preview-title">
          <h3
            id="journal-preview-title"
            className="account__subtitle"
            tabIndex={-1}
            ref={previewHeadingRef}
          >
            Diário — prévia de exportação (demonstração)
          </h3>
          <p className="account__hint">
            Gerado em {new Date().toLocaleString("pt-BR")} · {entries.length}{" "}
            {entries.length === 1 ? "registro" : "registros"} · nenhum arquivo foi criado.
          </p>
          <ol className="journal__preview-list">
            {entries.map((entry) => (
              <li key={entry.id}>
                <p className="account__history-meta">{formatEntryDate(entry)}</p>
                <p className="journal__description">{entry.description}</p>
              </li>
            ))}
          </ol>
          <button type="button" className="referral__action" onClick={() => setExportStep(null)}>
            Fechar prévia
          </button>
        </section>
      )}

      {list.kind === "loading" && <p className="account__hint">Carregando diário…</p>}
      {list.kind === "error" && (
        <div className="referral__alert" role="alert">
          <p>{list.message}</p>
          <button type="button" className="referral__action" onClick={loadEntries}>
            Tentar novamente
          </button>
        </div>
      )}
      {list.kind === "ready" && entries.length === 0 && !draft && (
        <p className="account__hint">Nenhum registro.</p>
      )}
      {entries.length > 0 && (
        <ul className="account__history">
          {entries.map((entry) => (
            <li key={entry.id} className="account__history-item">
              <p className="account__history-meta">{formatEntryDate(entry)}</p>
              <p className="journal__description">{entry.description}</p>
              {confirmDeleteId === entry.id ? (
                <div className="account__confirm" role="group" aria-label="Confirmar exclusão">
                  <p>Excluir este registro? Não dá para desfazer.</p>
                  <div className="account__actions">
                    <button
                      type="button"
                      className="account__danger"
                      onClick={() => void handleDelete(entry.id)}
                    >
                      Excluir registro
                    </button>
                    <button
                      type="button"
                      className="referral__action"
                      onClick={() => setConfirmDeleteId(null)}
                    >
                      Cancelar
                    </button>
                  </div>
                </div>
              ) : (
                <div className="account__actions">
                  <button
                    type="button"
                    className="referral__action"
                    aria-label={`Editar registro de ${formatEntryDate(entry)}`}
                    onClick={() => openForm(entry)}
                  >
                    Editar
                  </button>
                  <button
                    type="button"
                    className="referral__action"
                    aria-label={`Excluir registro de ${formatEntryDate(entry)}`}
                    onClick={() => setConfirmDeleteId(entry.id)}
                  >
                    Excluir
                  </button>
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
      {actionError && (
        <p className="referral__error" role="alert">
          {actionError}
        </p>
      )}
    </div>
  );
}
