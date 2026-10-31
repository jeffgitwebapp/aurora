import { useEffect, useRef, useState } from "react";

import { EmergencyContacts } from "../emergency/EmergencyContacts";
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
  const nextMessageId = useRef(0);

  const handleSendMessage = async (text: string) => {
    setError(null);

    const userMessage: ChatMessage = {
      id: `message-${nextMessageId.current++}`,
      role: "user",
      text,
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const replyText = await sendMessage(text);
      const assistantMessage: ChatMessage = {
        id: `message-${nextMessageId.current++}`,
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
        <EmergencyContacts />

        <p className="chat-page__privacy">
          Esta conversa existe apenas enquanto a página está aberta. Ao sair, o
          histórico desta sessão é descartado.
        </p>
      </aside>
    </div>
  );
}
