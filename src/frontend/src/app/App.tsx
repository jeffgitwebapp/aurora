import { useEffect, useState } from "react";

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

function isRecipesPath() {
  return window.location.pathname === "/receitas";
}

export function App() {
  const [isConversationOpen, setIsConversationOpen] = useState(isConversationPath);
  const [isRecipesPage, setIsRecipesPage] = useState(isRecipesPath);
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(() =>
    isRecipesPath() ? getRandomRecipe() : null,
  );
  const [initialMessage, setInitialMessage] = useState("");
  const [sendInitialMessage, setSendInitialMessage] = useState(false);

  useEffect(() => {
    const handlePopState = () => {
      setIsConversationOpen(isConversationPath());
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
        window.history.replaceState(null, "", "/receitas");
        setSelectedRecipe((previous) => getRandomRecipe(previous?.id));
        setInitialMessage("");
        setSendInitialMessage(false);
        setIsConversationOpen(false);
        setIsRecipesPage(true);
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
    window.history.replaceState(null, "", "/conversa");
    setInitialMessage(message);
    setSendInitialMessage(sendImmediately);
    setIsConversationOpen(true);
  };

  const handleQuickExit = () => {
    window.dispatchEvent(new Event("aurora:quick-exit"));
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
        : "Aurora — protótipo local";
    document.body.classList.toggle("conversation-mode", isConversationOpen);

    return () => document.body.classList.remove("conversation-mode");
  }, [isConversationOpen, isRecipesPage]);

  if (isRecipesPage) {
    return selectedRecipe ? <RecipesPage recipe={selectedRecipe} /> : null;
  }

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
          onQuickExit={handleQuickExit}
        />
      </main>
    </div>
  );
}
