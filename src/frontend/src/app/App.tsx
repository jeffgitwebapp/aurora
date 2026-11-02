import { useEffect, useRef, useState } from "react";

import { AccountPage } from "../features/account/AccountPage";
import { logout, type AccountSession } from "../features/account/api/accountApi";
import { ChatPage } from "../features/chat/ChatPage";
import {
  getRandomRecipe,
  RecipesPage,
  type Recipe,
} from "../features/recipes/RecipesPage";
import { WelcomePage } from "../features/welcome/WelcomePage";

function isConversationPath() {
  return window.location.pathname === "/conversa";
}

function isAccountPath() {
  return window.location.pathname === "/conta";
}

function isRecipesPath() {
  return window.location.pathname === "/receitas";
}

export function App() {
  const [isConversationOpen, setIsConversationOpen] = useState(isConversationPath);
  const [isRecipesPage, setIsRecipesPage] = useState(isRecipesPath);
  const [isAccountPage, setIsAccountPage] = useState(isAccountPath);
  // Sessão da área logada só na memória da página: recarregar ou sair a encerra.
  const [accountSession, setAccountSession] = useState<AccountSession | null>(null);
  const accountSessionRef = useRef<AccountSession | null>(null);
  accountSessionRef.current = accountSession;
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(() =>
    isRecipesPath() ? getRandomRecipe() : null,
  );
  const [initialMessage, setInitialMessage] = useState("");
  const [sendInitialMessage, setSendInitialMessage] = useState(false);

  useEffect(() => {
    const handlePopState = () => {
      setIsConversationOpen(isConversationPath());
      setIsAccountPage(isAccountPath());
      const shouldShowRecipes = isRecipesPath();
      setIsRecipesPage(shouldShowRecipes);
      if (shouldShowRecipes) {
        setSelectedRecipe((previous) => getRandomRecipe(previous?.id));
      }
      setInitialMessage("");
      setSendInitialMessage(false);
    };

    const handleQuickExit = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        window.dispatchEvent(new Event("aurora:quick-exit"));
        endAccountSession();
        setIsAccountPage(false);
        window.history.replaceState(null, "", "/receitas");
        setSelectedRecipe((previous) => getRandomRecipe(previous?.id));
        setInitialMessage("");
        setSendInitialMessage(false);
        setIsConversationOpen(false);
        setIsRecipesPage(true);
      }
    };

    const endAccountSession = () => {
      if (accountSessionRef.current) {
        logout(accountSessionRef.current.token);
      }
      setAccountSession(null);
    };

    window.addEventListener("popstate", handlePopState);
    window.addEventListener("keydown", handleQuickExit);
    return () => {
      window.removeEventListener("popstate", handlePopState);
      window.removeEventListener("keydown", handleQuickExit);
    };
  }, []);

  const openConversation = (message: string, sendImmediately = false) => {
    window.history.replaceState(null, "", "/conversa");
    setInitialMessage(message);
    setSendInitialMessage(sendImmediately);
    setIsAccountPage(false);
    setIsConversationOpen(true);
  };

  const openAccount = () => {
    window.history.replaceState(null, "", "/conta");
    setIsConversationOpen(false);
    setIsAccountPage(true);
  };

  const openWelcome = () => {
    window.history.replaceState(null, "", "/");
    setIsAccountPage(false);
  };

  const handleQuickExit = () => {
    window.dispatchEvent(new Event("aurora:quick-exit"));
    if (accountSession) {
      logout(accountSession.token);
    }
    setAccountSession(null);
    setIsAccountPage(false);
    window.history.replaceState(null, "", "/receitas");
    setSelectedRecipe((previous) => getRandomRecipe(previous?.id));
    setInitialMessage("");
    setSendInitialMessage(false);
    setIsConversationOpen(false);
    setIsRecipesPage(true);
  };

  useEffect(() => {
    document.title = isRecipesPage
      ? "Receitas"
      : isConversationOpen
        ? "Notas"
        : isAccountPage
          ? "Conta — Aurora"
          : "Aurora — protótipo local";
    document.body.classList.toggle("conversation-mode", isConversationOpen);

    return () => document.body.classList.remove("conversation-mode");
  }, [isConversationOpen, isRecipesPage, isAccountPage]);

  if (isRecipesPage) {
    return selectedRecipe ? <RecipesPage recipe={selectedRecipe} /> : null;
  }

  if (isAccountPage && !isConversationOpen) {
    return (
      <AccountPage
        session={accountSession}
        onSessionChange={setAccountSession}
        onOpenConversation={() => openConversation("")}
        onBack={openWelcome}
        onQuickExit={handleQuickExit}
      />
    );
  }

  if (!isConversationOpen) {
    return (
      <WelcomePage
        onOpenConversation={openConversation}
        onOpenAccount={openAccount}
        isLoggedIn={accountSession !== null}
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
          accountSession={accountSession}
          onAccountSessionChange={setAccountSession}
          onOpenAccount={openAccount}
          onQuickExit={handleQuickExit}
        />
      </main>
    </div>
  );
}
