import { useLayoutEffect, useRef, useState } from "react";

import type { ChatMessage } from "../types";
import { CitedText } from "./CitedText";
import { SourcesModal } from "./SourcesModal";

interface MessageListProps {
  messages: ChatMessage[];
  isLoading?: boolean;
  onAskLaw: () => void;
  onOpenContacts: () => void;
  onOpenSafetyGuide: () => void;
  onQuickExit: () => void;
}

function sourcesButtonId(messageId: string): string {
  return `${messageId}-sources-button`;
}

export function MessageList({
  messages,
  isLoading = false,
  onAskLaw,
  onOpenContacts,
  onOpenSafetyGuide,
  onQuickExit,
}: MessageListProps) {
  const containerRef = useRef<HTMLElement | null>(null);
  const [openSources, setOpenSources] = useState<{
    messageId: string;
    highlighted: number | null;
  } | null>(null);
  const sourcesMessage = openSources
    ? messages.find((message) => message.id === openSources.messageId)
    : undefined;

  const handleCloseSources = () => {
    const messageId = openSources?.messageId;
    setOpenSources(null);
    if (messageId) {
      window.requestAnimationFrame(() => {
        document.getElementById(sourcesButtonId(messageId))?.focus();
      });
    }
  };

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
            const isOutOfScope = message.outOfScopeCategory !== undefined;
            const titleId = `${message.id}-title`;
            return (
              <li
                key={message.id}
                className={`message-item message-item--${message.role}${isOutOfScope ? " message-item--limit" : ""}`}
                aria-labelledby={isOutOfScope ? titleId : undefined}
              >
                <span className="message-item__sender">
                  {isUser ? "Você" : "Aurora"}
                </span>
                {isOutOfScope && (
                  <h2 className="message-item__limit-title" id={titleId}>
                    Fora do que eu posso fazer
                  </h2>
                )}
                <p className="message-item__text">
                  {message.sources && message.sources.length > 0 ? (
                    <CitedText
                      text={message.text}
                      sources={message.sources}
                      onOpenSource={(number) =>
                        setOpenSources({ messageId: message.id, highlighted: number })
                      }
                    />
                  ) : (
                    message.text
                  )}
                </p>
                {isOutOfScope && (
                  <>
                    <div className="message-item__actions">
                      <button
                        type="button"
                        className="message-item__action"
                        onClick={onAskLaw}
                        disabled={isLoading}
                      >
                        O que a lei diz
                      </button>
                      <button
                        type="button"
                        className="message-item__action"
                        onClick={onOpenContacts}
                      >
                        Defensoria Pública ou CRAM
                      </button>
                    </div>
                    <p className="message-item__note">
                      No protótipo, este botão leva aos contatos gerais desta
                      tela. Opções de Defensoria Pública e CRAM entram com o
                      encaminhamento por cidade.
                    </p>
                    <p className="message-item__autonomy">
                      O Aurora informa sobre a lei, mas não diz o que você deve
                      fazer. A decisão é sempre sua.
                    </p>
                  </>
                )}
                {message.offer === "safety_guide" && (
                  <div className="message-item__actions">
                    <button
                      type="button"
                      className="message-item__action"
                      onClick={onOpenSafetyGuide}
                    >
                      Abrir guia de segurança
                    </button>
                  </div>
                )}
                {message.sources && message.sources.length > 0 && (
                  <button
                    type="button"
                    id={sourcesButtonId(message.id)}
                    className="message-sources__link"
                    aria-haspopup="dialog"
                    onClick={() =>
                      setOpenSources({ messageId: message.id, highlighted: null })
                    }
                  >
                    Fontes ({message.sources.length})
                  </button>
                )}
                {message.demo && (
                  <p className="message-item__demo" role="note">
                    {message.offer
                      ? "Demonstração: o convite é acionado por uma frase de teste."
                      : isOutOfScope
                        ? "Demonstração: o limite é acionado por frases de teste e não identifica pedidos reais."
                        : message.knowledgeStatus === "found"
                          ? "Resposta baseada nas fontes indicadas. É informação geral e não substitui orientação sobre o seu caso."
                          : "Demonstração: a base de fontes do protótipo ainda está em revisão e pode não cobrir esta pergunta."}
                  </p>
                )}
              </li>
            );
          })}
          {isLoading && (
            <li
              className="message-item message-item--assistant message-item--typing"
              role="status"
              aria-label="Lendo com atenção"
            >
              <span className="message-item__sender">Aurora</span>
              <span className="message-item__typing-text">Lendo com atenção…</span>
              <span className="message-item__typing-dots" aria-hidden="true">
                <span />
                <span />
                <span />
              </span>
            </li>
          )}
        </ol>
      )}
      {sourcesMessage?.sources && sourcesMessage.sources.length > 0 && (
        <SourcesModal
          sources={sourcesMessage.sources}
          highlighted={openSources?.highlighted ?? null}
          onClose={handleCloseSources}
          onQuickExit={onQuickExit}
        />
      )}
    </section>
  );
}
