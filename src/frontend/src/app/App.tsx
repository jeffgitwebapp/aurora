import { useEffect, useMemo, useRef, type ComponentType } from "react";

import { AccountPage, type AccountSection } from "../features/account/AccountPage";
import { SaveConversationPanel } from "../features/account/SaveConversationPanel";
import { ChatPage } from "../features/chat/ChatPage";
import { JournalArea } from "../features/journal/JournalArea";
import { LearningArea } from "../features/learning/LearningArea";
import { QuestionnairePanel } from "../features/questionnaire/QuestionnairePanel";
import { getRandomRecipe, RecipesPage, type Recipe } from "../features/recipes/RecipesPage";
import { ReferralPanel } from "../features/referral/ReferralPanel";
import { SafetyGuide } from "../features/safety/SafetyGuide";
import { SafetyGuidePanel } from "../features/safety/SafetyGuidePanel";
import { WelcomePage } from "../features/welcome/WelcomePage";
import {
  RedirectsProvider,
  useRedirects,
} from "../shared/redirectsManagement/RedirectsProvider";
import type { PanelTarget } from "../shared/redirectsManagement/targets";
import { SessionProvider } from "../shared/session/SessionProvider";
import { TranscriptProvider } from "../shared/transcript/TranscriptProvider";

/**
 * Raiz de composição: único lugar que conhece todas as features e liga cada
 * destino do redirectsManagement ao componente que o atende.
 */
const CONVERSATION_PANELS: Record<PanelTarget, ComponentType> = {
  referral: ReferralPanel,
  questionnaire: QuestionnairePanel,
  saveConversation: SaveConversationPanel,
  safetyGuide: SafetyGuidePanel,
};

const ACCOUNT_SECTIONS: readonly AccountSection[] = [
  { title: "Módulos", Component: LearningArea },
  { title: "Diário", Component: JournalArea },
  { title: "Guia de segurança", Component: SafetyGuide },
];

const PAGE_TITLES = {
  welcome: "Aurora — protótipo local",
  conversation: "Notas",
  account: "Conta — Aurora",
  recipes: "Receitas",
} as const;

export function App() {
  return (
    <SessionProvider>
      <TranscriptProvider>
        <RedirectsProvider panels={CONVERSATION_PANELS}>
          <CurrentPage />
        </RedirectsProvider>
      </TranscriptProvider>
    </SessionProvider>
  );
}

function CurrentPage() {
  const { page, quickExitCount, redirect } = useRedirects();
  const lastRecipe = useRef<Recipe | null>(null);
  // Cada Saída Rápida mostra uma receita diferente da anterior.
  const recipe = useMemo(() => getRandomRecipe(lastRecipe.current?.id), [quickExitCount]);
  lastRecipe.current = recipe;

  useEffect(() => {
    document.title = PAGE_TITLES[page];
    document.body.classList.toggle("conversation-mode", page === "conversation");
    return () => document.body.classList.remove("conversation-mode");
  }, [page]);

  if (page === "recipes") {
    return <RecipesPage recipe={recipe} />;
  }
  if (page === "account") {
    return <AccountPage sections={ACCOUNT_SECTIONS} />;
  }
  if (page === "welcome") {
    return <WelcomePage />;
  }

  return (
    <div className="app app--conversation">
      <header className="conversation-header">
        <a className="conversation-header__brand" href="/">
          Aurora
        </a>
        <nav className="conversation-header__actions" aria-label="Ações de segurança">
          <a className="conversation-header__emergency" href="tel:190">
            Emergência
          </a>
          <button
            className="conversation-header__exit"
            type="button"
            onClick={() => redirect("quickExit")}
          >
            Saída rápida <span aria-hidden="true">(Esc)</span>
          </button>
        </nav>
      </header>
      <main className="app__main">
        <ChatPage />
      </main>
    </div>
  );
}
