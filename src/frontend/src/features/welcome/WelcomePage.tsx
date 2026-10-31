import { useRef, useState, type FormEvent } from "react";

import { EmergencyContacts } from "../emergency/EmergencyContacts";

interface WelcomePageProps {
  onOpenConversation: (initialMessage: string, sendImmediately?: boolean) => void;
  onQuickExit: () => void;
}

const suggestedMessages = [
  "Quero entender o que estou sentindo",
  "Tenho dúvidas sobre meus direitos",
  "Onde encontrar apoio",
];

export function WelcomePage({ onOpenConversation, onQuickExit }: WelcomePageProps) {
  const [draft, setDraft] = useState("");
  const [isPrivacyOpen, setIsPrivacyOpen] = useState(false);
  const privacyButtonRef = useRef<HTMLButtonElement>(null);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const message = draft.trim();
    if (message) {
      onOpenConversation(message, true);
    }
  };

  return (
    <div className="welcome-page">
      <header className="welcome-header">
        <a className="welcome-header__brand" href="/" aria-label="Aurora, início">
          Aurora
        </a>
        <nav className="welcome-header__actions" aria-label="Ações de segurança">
          <a className="welcome-header__emergency" href="tel:190">
            Emergência
          </a>
          <button
            className="welcome-header__exit"
            type="button"
            onClick={onQuickExit}
          >
            Sair
          </button>
        </nav>
      </header>

      <section className="welcome-hero" aria-labelledby="welcome-title">
        <div className="welcome-hero__content">
          <p className="welcome-hero__eyebrow">Um espaço para se informar</p>
          <h1 className="welcome-hero__title" id="welcome-title">
            Fale com a Aurora
          </h1>
          <p className="welcome-hero__description">
            Você pode começar com suas próprias palavras.
          </p>
        </div>
        <div className="welcome-hero__art" aria-hidden="true">
          <span />
          <span />
        </div>
      </section>

      <main className="welcome-page__main">
        <div className="welcome-page__content">
          <form className="welcome-composer" onSubmit={handleSubmit}>
            <label className="visually-hidden" htmlFor="welcome-message">
              Escreva sua mensagem
            </label>
            <textarea
              id="welcome-message"
              className="welcome-composer__input"
              rows={3}
              placeholder="Escreva o que quiser…"
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
            />
            <div className="welcome-composer__footer">
              <span>
                A conversa fica na memória enquanto esta página está aberta.
              </span>
              <button
                type="submit"
                className="welcome-composer__submit"
                aria-label="Enviar"
                disabled={!draft.trim()}
              >
                <span aria-hidden="true">→</span>
              </button>
            </div>
          </form>

          <div className="welcome-suggestions" aria-label="Sugestões para começar">
            <p className="welcome-suggestions__label">Se preferir, comece por aqui</p>
            <div className="welcome-suggestions__list">
              {suggestedMessages.map((message) => (
                <button
                  key={message}
                  type="button"
                  className="welcome-suggestions__button"
                  onClick={() => onOpenConversation(message, true)}
                >
                  {message}
                </button>
              ))}
            </div>
          </div>
        </div>
      </main>

      <footer className="welcome-footer">
        <EmergencyContacts compact />
        <div className="welcome-footer__links">
          <span>Tecla Esc fecha a página.</span>
          <button
            ref={privacyButtonRef}
            type="button"
            className="welcome-footer__link"
            aria-expanded={isPrivacyOpen}
            aria-controls="privacy-notice"
            onClick={() => setIsPrivacyOpen(true)}
          >
            Privacidade
          </button>
          <a className="welcome-footer__link" href="#welcome-emergency-contacts">
            Contatos úteis
          </a>
        </div>
      </footer>

      <section
        id="privacy-notice"
        className="privacy-panel"
        aria-labelledby="privacy-notice-title"
        hidden={!isPrivacyOpen}
      >
        <h2 id="privacy-notice-title">Privacidade da conversa</h2>
        <p>
          Esta conversa fica na memória enquanto esta página está aberta. Ao
          usar a Saída Rápida ou encerrar a página, o Aurora descarta o conteúdo
          da sessão que mantém. Isso não apaga possíveis registros do navegador,
          dispositivo, rede ou terceiros.
        </p>
        <button
          type="button"
          className="privacy-panel__close"
          onClick={() => {
            setIsPrivacyOpen(false);
            privacyButtonRef.current?.focus();
          }}
        >
          Fechar
        </button>
      </section>
    </div>
  );
}
