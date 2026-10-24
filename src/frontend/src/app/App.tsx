import { useEffect, useState } from "react";

import { ChatPage } from "../features/chat/ChatPage";
import { WelcomePage } from "../features/welcome/WelcomePage";

function isConversationPath() {
  return window.location.pathname === "/conversa";
}

export function App() {
  const [isConversationOpen, setIsConversationOpen] = useState(isConversationPath);
  const [initialMessage, setInitialMessage] = useState("");
  const [sendInitialMessage, setSendInitialMessage] = useState(false);

  useEffect(() => {
    const handlePopState = () => {
      setIsConversationOpen(isConversationPath());
      setInitialMessage("");
      setSendInitialMessage(false);
    };

    const handleQuickExit = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        window.location.replace("about:blank");
      }
    };

    window.addEventListener("popstate", handlePopState);
    window.addEventListener("keydown", handleQuickExit);
    return () => {
      window.removeEventListener("popstate", handlePopState);
      window.removeEventListener("keydown", handleQuickExit);
    };
  }, []);

  const openConversation = (message: string, sendImmediately = false) => {
    window.history.pushState(null, "", "/conversa");
    setInitialMessage(message);
    setSendInitialMessage(sendImmediately);
    setIsConversationOpen(true);
  };

  const handleQuickExit = () => {
    window.location.replace("about:blank");
  };

  useEffect(() => {
    document.title = isConversationOpen ? "Notas" : "Aurora — protótipo local";
    document.body.classList.toggle("conversation-mode", isConversationOpen);

    return () => document.body.classList.remove("conversation-mode");
  }, [isConversationOpen]);

  if (!isConversationOpen) {
    return (
      <WelcomePage
        onOpenConversation={openConversation}
        onQuickExit={handleQuickExit}
      />
    );
  }

  return (
    <div className="app app--conversation">
      <header className="conversation-header">
        <a className="conversation-header__brand" href="/">
          Notas
        </a>
        <nav className="conversation-header__actions" aria-label="Ações de segurança">
          <a className="conversation-header__emergency" href="tel:190">
            Emergência
          </a>
          <button
            className="conversation-header__exit"
            type="button"
            onClick={handleQuickExit}
          >
            Saída rápida <span aria-hidden="true">(Esc)</span>
          </button>
        </nav>
      </header>
      <main className="app__main">
        <ChatPage
          initialMessage={initialMessage}
          sendInitialMessage={sendInitialMessage}
        />
      </main>
    </div>
  );
}
