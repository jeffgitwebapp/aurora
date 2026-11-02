import { useCallback, useEffect, useRef, useState, type ComponentType } from "react";

import { useRedirects } from "../../shared/redirectsManagement/RedirectsProvider";
import { AccountForm } from "../../shared/session/AccountForm";
import { useSession, type AccountSectionProps } from "../../shared/session/SessionProvider";
import { AccountApiError, SessionExpiredError } from "../../shared/session/sessionApi";
import {
  deleteAccount,
  deleteConversation,
  getConversation,
  listConversations,
  type ConversationSummary,
  type SavedMessage,
} from "./api/accountApi";

/** Seção extra de “Minha conta”, fornecida pela composição do app. */
export interface AccountSection {
  title: string;
  Component: ComponentType<AccountSectionProps>;
}

interface AccountPageProps {
  sections: readonly AccountSection[];
}

type HistoryState =
  | { kind: "loading" }
  | { kind: "error"; message: string }
  | { kind: "ready"; conversations: ConversationSummary[] };

const formatDate = (iso: string) =>
  new Date(iso).toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });

const DEMO_NOTICE =
  "Demonstração: a conta, as conversas salvas, o diário e o plano de segurança ficam só na memória do servidor do protótipo, cifrados com uma chave derivada da sua senha, e são apagadas quando ele reinicia. Não guarde dados reais. Recarregar a página ou usar a Saída rápida encerra a sessão.";

export function AccountPage({ sections }: AccountPageProps) {
  const { session, setSession: onSessionChange, endSession } = useSession();
  const { redirect } = useRedirects();
  const onOpenConversation = () => redirect("conversation");
  const onBack = () => redirect("welcome");
  const onQuickExit = () => redirect("quickExit");
  const [history, setHistory] = useState<HistoryState>({ kind: "loading" });
  const [viewing, setViewing] = useState<{
    summary: ConversationSummary;
    messages: SavedMessage[];
  } | null>(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);
  const [confirmAccountDeletion, setConfirmAccountDeletion] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [isBusy, setIsBusy] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [focusedSection, setFocusedSection] = useState<number | null>(null);
  const isFocused = focusedSection !== null;
  const titleRef = useRef<HTMLHeadingElement | null>(null);

  const handleFailure = useCallback(
    (err: unknown, fallback: string) => {
      if (err instanceof SessionExpiredError) {
        onSessionChange(null);
        setNotice(err.message);
        return;
      }
      // A mensagem da ação diz o que não aconteceu (por exemplo, "Nada foi apagado").
      setActionError(fallback);
    },
    [onSessionChange],
  );

  const handleSessionExpired = useCallback(
    (message: string) => {
      setFocusedSection(null);
      onSessionChange(null);
      setNotice(message);
    },
    [onSessionChange],
  );

  const loadHistory = useCallback(async () => {
    if (!session) {
      return;
    }
    setHistory({ kind: "loading" });
    try {
      setHistory({ kind: "ready", conversations: await listConversations(session.token) });
    } catch (err: unknown) {
      if (err instanceof SessionExpiredError) {
        handleFailure(err, "");
        return;
      }
      setHistory({
        kind: "error",
        message:
          err instanceof AccountApiError
            ? err.message
            : "Não foi possível carregar as conversas salvas.",
      });
    }
  }, [session, handleFailure]);

  useEffect(() => {
    void loadHistory();
  }, [loadHistory]);

  useEffect(() => {
    titleRef.current?.focus();
  }, [viewing, session]);

  const runAction = async (action: () => Promise<void>, fallback: string) => {
    setIsBusy(true);
    setActionError(null);
    try {
      await action();
    } catch (err: unknown) {
      handleFailure(err, fallback);
    } finally {
      setIsBusy(false);
    }
  };

  const handleView = (summary: ConversationSummary) =>
    runAction(async () => {
      if (session) {
        setViewing({ summary, messages: await getConversation(session.token, summary.id) });
      }
    }, "Não foi possível abrir a conversa.");

  const handleDeleteConversation = (id: string) =>
    runAction(async () => {
      if (session) {
        await deleteConversation(session.token, id);
        setConfirmDeleteId(null);
        setNotice("Conversa excluída.");
        await loadHistory();
      }
    }, "Não foi possível excluir a conversa. Nada foi apagado.");

  const handleDeleteAccount = () =>
    runAction(async () => {
      if (session) {
        await deleteAccount(session.token);
        setConfirmAccountDeletion(false);
        onSessionChange(null);
        setNotice("Conta e dados excluídos.");
      }
    }, "Não foi possível excluir a conta. Nada foi apagado; tente novamente.");

  const handleLogout = () => {
    endSession();
    setNotice(null);
  };

  const conversationCount = history.kind === "ready" ? history.conversations.length : 0;

  return (
    <div className="welcome-page account-page">
      <header className="welcome-header">
        <a className="welcome-header__brand" href="/" aria-label="Aurora, início">
          Aurora
        </a>
        <nav className="welcome-header__actions" aria-label="Ações de segurança">
          <a className="welcome-header__emergency" href="tel:190">
            Emergência
          </a>
          <button className="welcome-header__exit" type="button" onClick={onQuickExit}>
            Sair
          </button>
        </nav>
      </header>

      <main className="account">
        <button type="button" className="referral__back" onClick={onBack}>
          ← Voltar ao início
        </button>

        {!session && (
          <section className="account__card" aria-labelledby="account-title">
            <AccountForm
              notice={notice}
              onAuthenticated={(created) => {
                setNotice(null);
                onSessionChange(created);
              }}
            />
            <p className="account__demo" role="note">
              {DEMO_NOTICE}
            </p>
          </section>
        )}

        {session && viewing && (
          <section className="account__card" aria-labelledby="account-title">
            <button
              type="button"
              className="referral__back"
              onClick={() => setViewing(null)}
            >
              ← Voltar ao histórico
            </button>
            <h1 id="account-title" className="account__title" tabIndex={-1} ref={titleRef}>
              Conversa salva em {formatDate(viewing.summary.savedAt)}
            </h1>
            <p className="account__hint">Somente leitura.</p>
            <ol className="account__transcript">
              {viewing.messages.map((message, index) => (
                <li key={index} className={`account__transcript-item--${message.role}`}>
                  <span className="message-item__sender">
                    {message.role === "user" ? "Você" : "Aurora"}
                  </span>
                  <p>{message.text}</p>
                </li>
              ))}
            </ol>
          </section>
        )}

        {session && !viewing && (
          <section
            className="account__card"
            aria-labelledby={isFocused ? undefined : "account-title"}
          >
            {!isFocused && (
              <>
                <h1 id="account-title" className="account__title" tabIndex={-1} ref={titleRef}>
                  Olá, {session.nickname}
                </h1>
                {notice && (
                  <p className="account__notice" role="status">
                    {notice}
                  </p>
                )}
                <div className="account__actions">
                  <button type="button" className="referral__submit" onClick={onOpenConversation}>
                    Ir para a conversa
                  </button>
                  <button type="button" className="referral__action" onClick={handleLogout}>
                    Sair da conta
                  </button>
                </div>

                <h2 className="account__subtitle">Conversas salvas</h2>
                {history.kind === "loading" && <p className="account__hint">Carregando…</p>}
                {history.kind === "error" && (
                  <div className="referral__alert" role="alert">
                    <p>{history.message}</p>
                    <button type="button" className="referral__action" onClick={loadHistory}>
                      Tentar novamente
                    </button>
                  </div>
                )}
                {history.kind === "ready" && history.conversations.length === 0 && (
                  <p className="account__hint">
                    Nenhuma conversa salva. Na conversa, use “Salvar conversa na conta”.
                  </p>
                )}
                {history.kind === "ready" && history.conversations.length > 0 && (
                  <ul className="account__history">
                    {history.conversations.map((conversation) => (
                      <li key={conversation.id} className="account__history-item">
                        <p className="account__history-meta">
                          {formatDate(conversation.savedAt)} · {conversation.messageCount}{" "}
                          {conversation.messageCount === 1 ? "mensagem" : "mensagens"}
                        </p>
                        <p className="account__history-excerpt">{conversation.excerpt}</p>
                        {confirmDeleteId === conversation.id ? (
                          <div className="account__confirm" role="group" aria-label="Confirmar exclusão">
                            <p>Excluir esta conversa? Não dá para desfazer.</p>
                            <div className="account__actions">
                              <button
                                type="button"
                                className="account__danger"
                                disabled={isBusy}
                                onClick={() => void handleDeleteConversation(conversation.id)}
                              >
                                Excluir conversa
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
                              disabled={isBusy}
                              onClick={() => void handleView(conversation)}
                            >
                              Ver
                            </button>
                            <button
                              type="button"
                              className="referral__action"
                              onClick={() => setConfirmDeleteId(conversation.id)}
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

              </>
            )}

            {sections.map(({ title, Component }, index) => (
              <div key={title} hidden={isFocused && focusedSection !== index}>
                {!isFocused && <h2 className="account__subtitle">{title}</h2>}
                <Component
                  token={session.token}
                  onSessionExpired={handleSessionExpired}
                  onFocusChange={(focused) => setFocusedSection(focused ? index : null)}
                />
              </div>
            ))}

            {!isFocused && (
              <>
                <h2 className="account__subtitle">Excluir conta</h2>
                {confirmAccountDeletion ? (
                  <div className="account__confirm" role="group" aria-label="Confirmar exclusão da conta">
                    <p>
                      Isto apaga a conta e {conversationCount}{" "}
                      {conversationCount === 1 ? "conversa salva" : "conversas salvas"}. Não dá
                      para desfazer.
                    </p>
                    <div className="account__actions">
                      <button
                        type="button"
                        className="account__danger"
                        disabled={isBusy}
                        onClick={() => void handleDeleteAccount()}
                      >
                        Excluir agora
                      </button>
                      <button
                        type="button"
                        className="referral__action"
                        onClick={() => setConfirmAccountDeletion(false)}
                      >
                        Cancelar
                      </button>
                    </div>
                  </div>
                ) : (
                  <button
                    type="button"
                    className="account__danger account__danger--outline"
                    onClick={() => setConfirmAccountDeletion(true)}
                  >
                    Excluir conta e todos os dados
                  </button>
                )}

                <p className="account__demo" role="note">
                  {DEMO_NOTICE}
                </p>
              </>
            )}
          </section>
        )}
      </main>
    </div>
  );
}
