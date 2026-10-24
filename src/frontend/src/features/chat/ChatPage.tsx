import { useEffect, useRef, useState } from "react";

import { sendMessage, ChatApiError } from "./api/chatApi";
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
  const initialMessageSent = useRef(false);

  const handleSendMessage = async (text: string) => {
    setError(null);

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      text,
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const replyText = await sendMessage(text);
      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        text: replyText,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: unknown) {
      if (err instanceof ChatApiError) {
        setError(err.message);
      } else {
        setError("Ocorreu um erro inesperado ao se comunicar com o servidor.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (sendInitialMessage && initialMessage && !initialMessageSent.current) {
      initialMessageSent.current = true;
      void handleSendMessage(initialMessage);
    }
  }, [initialMessage, sendInitialMessage]);

  return (
    <div className="chat-page">
      <section className="chat-page__conversation" aria-label="Conversa">
        {error && (
          <div className="chat-page__alert" role="alert">
            <p className="chat-page__alert-text">{error}</p>
            <button
              type="button"
              className="chat-page__alert-dismiss"
              onClick={() => setError(null)}
            >
              Fechar
            </button>
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
        <section className="emergency-card" aria-labelledby="emergency-title">
          <p className="emergency-card__eyebrow">Ajuda por telefone</p>
          <h2 className="emergency-card__title" id="emergency-title">
            Em perigo agora?
          </h2>
          <ul className="emergency-card__list">
            <li>
              <a href="tel:190">
                <span>Polícia Militar</span>
                <strong>190</strong>
              </a>
            </li>
            <li>
              <a href="tel:180">
                <span>Central de Atendimento à Mulher</span>
                <strong>180</strong>
              </a>
            </li>
            <li>
              <a href="tel:192">
                <span>SAMU</span>
                <strong>192</strong>
              </a>
            </li>
            <li>
              <a href="tel:188">
                <span>CVV</span>
                <strong>188</strong>
              </a>
            </li>
          </ul>
        </section>

        <p className="chat-page__privacy">
          Esta conversa existe apenas enquanto a página está aberta. Ao sair, o
          histórico desta sessão é descartado.
        </p>
      </aside>
    </div>
  );
}
