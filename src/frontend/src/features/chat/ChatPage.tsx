import { useState } from "react";

import { sendMessage, ChatApiError } from "./api/chatApi";
import { MessageComposer } from "./components/MessageComposer";
import { MessageList } from "./components/MessageList";
import type { ChatMessage } from "./types";

export function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

  return (
    <div className="chat-page">
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

      <MessageComposer onSendMessage={handleSendMessage} disabled={isLoading} />
    </div>
  );
}

