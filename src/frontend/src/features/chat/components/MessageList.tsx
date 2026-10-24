import { useLayoutEffect, useRef } from "react";

import type { ChatMessage } from "../types";

interface MessageListProps {
  messages: ChatMessage[];
  isLoading?: boolean;
}

export function MessageList({ messages, isLoading = false }: MessageListProps) {
  const containerRef = useRef<HTMLElement | null>(null);

  useLayoutEffect(() => {
    const container = containerRef.current;
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  }, [messages, isLoading]);

  return (
    <section
      ref={containerRef}
      className="message-list-container"
      aria-label="Histórico de mensagens"
    >
      {messages.length === 0 && !isLoading ? (
        <div className="message-list__empty">
          <p className="message-list__welcome">
            Conte com suas palavras o que está acontecendo. Não precisa usar os
            termos certos, e você pode parar quando quiser.
          </p>
          <p className="message-list__hint">
            Você decide o que compartilhar.
          </p>
        </div>
      ) : (
        <ol className="message-list" role="log" aria-live="polite">
          {messages.map((message) => {
            const isUser = message.role === "user";
            return (
              <li
                key={message.id}
                className={`message-item message-item--${message.role}`}
              >
                <span className="message-item__sender">
                  {isUser ? "Você" : "Aurora"}
                </span>
                <p className="message-item__text">{message.text}</p>
              </li>
            );
          })}
          {isLoading && (
            <li
              className="message-item message-item--assistant message-item--typing"
              role="status"
              aria-label="Aurora está digitando"
            >
              <span className="message-item__sender">Aurora</span>
              <span className="message-item__typing-dots" aria-hidden="true">
                <span />
                <span />
                <span />
              </span>
            </li>
          )}
        </ol>
      )}
    </section>
  );
}
