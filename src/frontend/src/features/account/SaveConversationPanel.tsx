import { useEffect, useRef, useState } from "react";

import { useRedirects } from "../../shared/redirectsManagement/RedirectsProvider";
import { AccountForm } from "../../shared/session/AccountForm";
import { useSession } from "../../shared/session/SessionProvider";
import { AccountApiError, SessionExpiredError } from "../../shared/session/sessionApi";
import { useTranscript } from "../../shared/transcript/TranscriptProvider";
import { saveConversation } from "./api/accountApi";

type SaveState =
  | { kind: "confirm" }
  | { kind: "saving" }
  | { kind: "saved" }
  | { kind: "error"; message: string };

/** Painel exibido dentro da conversa; lê a transcrição sem depender da feature de conversa. */
export function SaveConversationPanel() {
  const { messages } = useTranscript();
  const { session, setSession: onSessionChange } = useSession();
  const { redirect } = useRedirects();
  const onBack = () => redirect("closePanel");
  const onOpenAccount = () => redirect("account");
  const [state, setState] = useState<SaveState>({ kind: "confirm" });
  const [notice, setNotice] = useState<string | null>(null);
  const titleRef = useRef<HTMLHeadingElement | null>(null);

  useEffect(() => {
    titleRef.current?.focus();
  }, [session, state.kind]);

  const handleSave = async () => {
    if (!session) {
      return;
    }
    setState({ kind: "saving" });
    try {
      await saveConversation(session.token, messages);
      setState({ kind: "saved" });
    } catch (err: unknown) {
      if (err instanceof SessionExpiredError) {
        onSessionChange(null);
        setNotice(err.message);
        setState({ kind: "confirm" });
        return;
      }
      setState({
        kind: "error",
        message:
          err instanceof AccountApiError
            ? err.message
            : "Não foi possível salvar. Nada foi guardado.",
      });
    }
  };

  const count = messages.length;

  return (
    <section className="questionnaire save-conversation" aria-labelledby="account-title">
      <button type="button" className="referral__back" onClick={onBack}>
        ← Voltar à conversa
      </button>

      {count === 0 && (
        <>
          <h1 id="account-title" className="account__title" tabIndex={-1} ref={titleRef}>
            Salvar conversa na conta
          </h1>
          <p>Ainda não há mensagens para salvar.</p>
        </>
      )}

      {count > 0 && !session && (
        <div className="save-conversation__form">
          <AccountForm
            title="Entre para salvar esta conversa"
            notice={notice}
            onAuthenticated={(created) => {
              setNotice(null);
              onSessionChange(created);
            }}
          />
          <p className="account__hint">
            A conversa continua aberta enquanto você entra; nada é salvo sem a sua
            confirmação.
          </p>
        </div>
      )}

      {count > 0 && session && state.kind !== "saved" && (
        <>
          <h1 id="account-title" className="account__title" tabIndex={-1} ref={titleRef}>
            Salvar conversa na conta
          </h1>
          <p>
            Isto vai guardar {count} {count === 1 ? "mensagem" : "mensagens"} desta conversa
            na conta <strong>{session.nickname}</strong>. Salvar?
          </p>
          <p className="account__hint">
            Ficam guardados só o texto e quem escreveu cada mensagem, cifrados com uma
            chave derivada da sua senha, na memória do servidor de demonstração. Fontes e
            blocos especiais não são guardados.
          </p>
          {state.kind === "error" && (
            <p className="referral__error" role="alert">
              {state.message}
            </p>
          )}
          <div className="questionnaire__nav">
            <button
              type="button"
              className="referral__submit"
              disabled={state.kind === "saving"}
              onClick={() => void handleSave()}
            >
              {state.kind === "saving" ? "Salvando..." : "Salvar"}
            </button>
            <button type="button" className="referral__action" onClick={onBack}>
              Cancelar
            </button>
          </div>
        </>
      )}

      {session && state.kind === "saved" && (
        <>
          <h1 id="account-title" className="account__title" tabIndex={-1} ref={titleRef}>
            Conversa salva
          </h1>
          <p role="status">
            A conversa foi guardada na conta {session.nickname}. Você pode vê-la em “Minha
            conta”.
          </p>
          <div className="questionnaire__nav">
            <button type="button" className="referral__submit" onClick={onBack}>
              Voltar à conversa
            </button>
            <button type="button" className="referral__action" onClick={onOpenAccount}>
              Ver em Minha conta
            </button>
          </div>
          <p className="account__hint">
            Ao abrir “Minha conta”, esta conversa é fechada; a cópia salva continua na
            conta.
          </p>
        </>
      )}
    </section>
  );
}
