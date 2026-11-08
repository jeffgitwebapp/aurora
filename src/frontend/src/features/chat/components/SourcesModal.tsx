import { useEffect, useRef } from "react";

import type { SourceReference } from "../api/chatApi";

interface SourcesModalProps {
  sources: SourceReference[];
  /** Fonte (1-based) a destacar, quando o modal é aberto por um marcador [n]. */
  highlighted?: number | null;
  onClose: () => void;
  onQuickExit: () => void;
}

/**
 * Lista de fontes de uma resposta, aberta pelo link "Fontes" ou por um marcador [n].
 * O Esc continua sendo a Saída Rápida global, por isso o cancel nativo é bloqueado.
 */
export function SourcesModal({
  sources,
  highlighted = null,
  onClose,
  onQuickExit,
}: SourcesModalProps) {
  const dialogRef = useRef<HTMLDialogElement | null>(null);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (dialog && !dialog.open) {
      dialog.showModal();
    }
    const target =
      highlighted !== null
        ? dialog?.querySelector<HTMLElement>(`[data-source="${highlighted}"] a`)
        : null;
    (target ?? dialog)?.focus();
    target?.scrollIntoView({ block: "nearest" });
  }, [highlighted]);

  return (
    <dialog
      ref={dialogRef}
      className="sources-modal"
      aria-labelledby="sources-modal-title"
      aria-modal="true"
      tabIndex={-1}
      onCancel={(event) => event.preventDefault()}
    >
      <div className="sources-modal__content">
        <p className="sources-modal__eyebrow">Fontes</p>
        <h1 id="sources-modal-title">Fontes desta resposta</h1>
        <p className="sources-modal__intro">
          Cada link abre o documento original em outra aba.
        </p>
        <ol className="sources-modal__list">
          {sources.map((source, index) => {
            const number = index + 1;
            return (
              <li
                key={source.id}
                data-source={number}
                className={
                  number === highlighted
                    ? "sources-modal__item sources-modal__item--highlighted"
                    : "sources-modal__item"
                }
              >
                <span className="sources-modal__number" aria-hidden="true">
                  [{number}]
                </span>
                <div>
                  <a href={source.url} target="_blank" rel="noreferrer">
                    {source.title}, {source.locator}
                  </a>
                  <span className="sources-modal__meta">
                    {source.publisher}
                    {source.version ? ` · ${source.version}` : ""}
                  </span>
                </div>
              </li>
            );
          })}
        </ol>
      </div>
      <div className="sources-modal__actions">
        <button className="risk-screen__return" type="button" onClick={onClose}>
          Voltar à conversa
        </button>
        <button className="risk-screen__quick-exit" type="button" onClick={onQuickExit}>
          Saída rápida (Esc)
        </button>
      </div>
    </dialog>
  );
}
