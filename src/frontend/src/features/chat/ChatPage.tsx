import { useEffect, useRef, useState } from "react";

import {
  EmergencyContacts,
  type EmergencyNumber,
} from "../../shared/components/EmergencyContacts";
import { RiskScreen } from "../../shared/components/RiskScreen";
import {
  PanelOutlet,
  useRedirects,
} from "../../shared/redirectsManagement/RedirectsProvider";
import { QUICK_EXIT_EVENT } from "../../shared/redirectsManagement/targets";
import { useTranscript } from "../../shared/transcript/TranscriptProvider";
import { sendMessage, ChatApiError } from "./api/chatApi";
import type { TriageSignal, TriageStatus } from "./api/chatApi";
import { MessageComposer } from "./components/MessageComposer";
import { MessageList } from "./components/MessageList";
import type { ChatMessage } from "./types";

const LAW_QUESTION = "O que é violência psicológica?";

/** Canal destacado por sinal de risco; regra provisória de produto (C-03). */
function priorityNumbers(signals: TriageSignal[]): EmergencyNumber[] {
  const numbers: EmergencyNumber[] = [];
  if (
    signals.some(
      (signal) =>
        signal === "ongoing_assault" || signal === "death_threat" || signal === "weapon_present",
    )
  ) {
    numbers.push("190");
  }
  if (signals.includes("suicidal_ideation")) {
    numbers.push("188");
  }
  return numbers;
}

export function ChatPage() {
  const { entry, panel, redirect } = useRedirects();
  const { setMessages: publishTranscript } = useTranscript();
  const initialMessage = entry.message;
  const sendInitialMessage = entry.sendImmediately;
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [retryMessage, setRetryMessage] = useState<string | null>(null);
  const [riskScreen, setRiskScreen] = useState<{
    status: Exclude<TriageStatus, "no_acute_signal">;
    signals: TriageSignal[];
  } | null>(null);
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
      const id = `message-${nextMessageId.current++}`;
      // Texto decidido pelo backend em todos os desfechos; o front só exibe.
      const reply = result.reply ?? "";
      let assistantMessage: ChatMessage;
      if (result.conversation !== null) {
        assistantMessage = { id, role: "assistant", text: reply };
      } else if (result.offer !== null) {
        assistantMessage = {
          id,
          role: "assistant",
          text: reply,
          offer: result.offer,
          demo: result.demo,
        };
      } else if (result.outOfScopeCategory !== null) {
        assistantMessage = {
          id,
          role: "assistant",
          text: reply,
          outOfScopeCategory: result.outOfScopeCategory,
          demo: result.demo,
        };
      } else if (result.knowledgeStatus === "found") {
        assistantMessage = {
          id,
          role: "assistant",
          text: reply,
          knowledgeStatus: "found",
          sources: result.sources,
          demo: result.demo,
        };
      } else {
        assistantMessage = {
          id,
          role: "assistant",
          text: reply,
          knowledgeStatus: "no_source",
          demo: result.demo,
        };
      }
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

  const handleAskLaw = () => {
    void handleSendMessage(LAW_QUESTION);
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
    publishTranscript(messages.map(({ role, text }) => ({ role, text })));
  }, [messages, publishTranscript]);

  useEffect(() => () => publishTranscript([]), [publishTranscript]);

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

    window.addEventListener(QUICK_EXIT_EVENT, handleQuickExit);
    return () => window.removeEventListener(QUICK_EXIT_EVENT, handleQuickExit);
  }, []);

  return (
    <div className="chat-page">
      {panel !== null && (
        <div className="chat-page__referral">
          <PanelOutlet />
        </div>
      )}

      <section
        className="chat-page__conversation"
        aria-label="Conversa"
        tabIndex={-1}
        hidden={panel !== null}
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

        <MessageList
          messages={messages}
          isLoading={isLoading}
          onAskLaw={handleAskLaw}
          onOpenContacts={() => redirect("emergencyContacts")}
          onOpenSafetyGuide={() => redirect("safetyGuide")}
        />

        <MessageComposer
          onSendMessage={handleSendMessage}
          disabled={isLoading}
          initialText={sendInitialMessage ? "" : initialMessage}
        />
      </section>

      <aside className="chat-page__sidebar" aria-label="Contatos úteis">
        {panel === null && (
          <>
            <button
              type="button"
              className="chat-page__referral-button"
              onClick={() => redirect("referral")}
            >
              Onde buscar ajuda
            </button>
            <button
              type="button"
              className="chat-page__questionnaire-button"
              onClick={() => redirect("questionnaire")}
            >
              Responder questionário
            </button>
            <button
              type="button"
              className="chat-page__questionnaire-button"
              onClick={() => redirect("saveConversation")}
            >
              Salvar conversa na conta
            </button>
          </>
        )}

        <EmergencyContacts />

        <p className="chat-page__privacy">
          Toda resposta mostra de onde veio a informação. Se não houver fonte
          confiável, o Aurora diz que não sabe.
        </p>

        <p className="chat-page__privacy">
          Esta conversa existe apenas enquanto a página está aberta. Ao sair, o
          histórico desta sessão é descartado.
        </p>
      </aside>
      {riskScreen && (
        <RiskScreen
          kind={riskScreen.status}
          priorityNumbers={priorityNumbers(riskScreen.signals)}
          onReturn={handleReturnToConversation}
          onQuickExit={() => redirect("quickExit")}
        />
      )}
    </div>
  );
}
