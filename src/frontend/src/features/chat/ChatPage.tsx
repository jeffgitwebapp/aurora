import { useEffect, useRef, useState } from "react";

import { EmergencyContacts } from "../emergency/EmergencyContacts";
import { sendMessage, ChatApiError } from "./api/chatApi";
import type { TriageSignal, TriageStatus } from "./api/chatApi";
import { MessageComposer } from "./components/MessageComposer";
import { MessageList } from "./components/MessageList";
import type { ChatMessage } from "./types";

interface ChatPageProps {
  initialMessage?: string;
  sendInitialMessage?: boolean;
}

export function ChatPage({
  initialMessage = "",
  sendInitialMessage = false,
}: ChatPageProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [retryMessage, setRetryMessage] = useState<string | null>(null);
  const [riskScreen, setRiskScreen] = useState<{
    status: Exclude<TriageStatus, "no_acute_signal">;
    signals: TriageSignal[];
  } | null>(null);
  const riskScreenRef = useRef<HTMLElement | null>(null);
  const initialMessageSent = useRef(false);
  const nextMessageId = useRef(0);
  const activeRequest = useRef(false);
  const abortController = useRef<AbortController | null>(null);

  const requestReply = async (text: string) => {
    if (activeRequest.current) {
      return;
    }

    activeRequest.current = true;
    setError(null);
    setRetryMessage(null);
    setIsLoading(true);
    const controller = new AbortController();
    abortController.current = controller;

    try {
      const result = await sendMessage(text, controller.signal);
      if (result.triageStatus !== "no_acute_signal") {
        setRiskScreen({
          status: result.triageStatus,
          signals: result.signals,
        });
        setError(null);
        setRetryMessage(null);
        return;
      }

      setRiskScreen(null);
      const replyText = result.reply;
      if (replyText === null) {
        throw new ChatApiError("A resposta simulada não foi disponibilizada.");
      }
      const assistantMessage: ChatMessage = {
        id: `message-${nextMessageId.current++}`,
        role: "assistant",
        text: replyText,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: unknown) {
      if (controller.signal.aborted) {
        return;
      }

      if (err instanceof ChatApiError) {
        setError(err.message);
      } else {
        setError("Ocorreu um erro inesperado ao se comunicar com o servidor.");
      }
      setRetryMessage(text);
    } finally {
      if (abortController.current === controller) {
        abortController.current = null;
        activeRequest.current = false;
        setIsLoading(false);
      }
    }
  };

  const handleSendMessage = async (text: string) => {
    if (activeRequest.current) {
      return;
    }

    setRiskScreen(null);
    setMessages((prev) => [
      ...prev,
      { id: `message-${nextMessageId.current++}`, role: "user", text },
    ]);
    await requestReply(text);
  };

  const handleRetry = () => {
    if (retryMessage) {
      void requestReply(retryMessage);
    }
  };

  const handleReturnToConversation = () => {
    window.requestAnimationFrame(() => {
      document
        .querySelector<HTMLElement>(".chat-page__conversation")
        ?.focus();
    });
    setRiskScreen(null);
  };

  useEffect(() => {
    if (riskScreen) {
      riskScreenRef.current?.focus();
    }
  }, [riskScreen]);

  useEffect(() => {
    if (sendInitialMessage && initialMessage && !initialMessageSent.current) {
      initialMessageSent.current = true;
      void handleSendMessage(initialMessage);
    }
  }, [initialMessage, sendInitialMessage]);

  useEffect(() => {
    const handleQuickExit = () => {
      abortController.current?.abort();
      abortController.current = null;
      activeRequest.current = false;
      setIsLoading(false);
    };

    window.addEventListener("aurora:quick-exit", handleQuickExit);
    return () => window.removeEventListener("aurora:quick-exit", handleQuickExit);
  }, []);

  if (riskScreen) {
    return (
      <section
        ref={riskScreenRef}
        className="risk-screen"
        aria-labelledby="risk-screen-title"
        tabIndex={-1}
      >
        <div className="risk-screen__content">
          {riskScreen.status === "acute" ? (
            <>
              <p className="risk-screen__eyebrow">Ajuda agora</p>
              <h1 id="risk-screen-title">Você pode estar em perigo agora.</h1>
              <p className="risk-screen__intro">
                Se puder, ligue para um destes números. As ligações são gratuitas
                e funcionam mesmo sem internet.
              </p>
              <EmergencyContacts variant="risk" signals={riskScreen.signals} />
              <p className="risk-screen__note">
                O Aurora não liga para ninguém por você. Você decide se e quando ligar.
              </p>
            </>
          ) : (
            <>
              <p className="risk-screen__eyebrow">Resultado incerto</p>
              <h1 id="risk-screen-title">Não foi possível avaliar esta mensagem.</h1>
              <p className="risk-screen__intro">
                Isso não significa que não exista risco. Se precisar, você pode
                escolher um dos canais de apoio abaixo. Nenhuma resposta informativa
                foi gerada.
              </p>
              <EmergencyContacts variant="risk" />
              <p className="risk-screen__note">
                O Aurora não liga para ninguém por você. Você decide se e quando ligar.
              </p>
            </>
          )}
          <p className="risk-screen__demo" role="note">
            Demonstração do protótipo: a triagem usa frases de teste e não avalia
            situações reais.
          </p>
          <button
            className="risk-screen__return"
            type="button"
            onClick={handleReturnToConversation}
          >
            Voltar à conversa
          </button>
        </div>
      </section>
    );
  }

  return (
    <div className="chat-page">
      <section
        className="chat-page__conversation"
        aria-label="Conversa"
        tabIndex={-1}
      >
        {error && (
          <div className="chat-page__alert" role="alert">
            <p className="chat-page__alert-text">{error}</p>
            <div className="chat-page__alert-actions">
              <button
                type="button"
                className="chat-page__alert-dismiss"
                onClick={() => setError(null)}
              >
                Fechar
              </button>
              {retryMessage && (
                <button
                  type="button"
                  className="chat-page__alert-dismiss"
                  onClick={handleRetry}
                >
                  Tentar novamente
                </button>
              )}
            </div>
          </div>
        )}

        <MessageList messages={messages} isLoading={isLoading} />

        <MessageComposer
          onSendMessage={handleSendMessage}
          disabled={isLoading}
          initialText={sendInitialMessage ? "" : initialMessage}
        />
      </section>

      <aside className="chat-page__sidebar" aria-label="Contatos úteis">
        <EmergencyContacts />

        <p className="chat-page__privacy">
          Esta conversa existe apenas enquanto a página está aberta. Ao sair, o
          histórico desta sessão é descartado.
        </p>
      </aside>
    </div>
  );
}
