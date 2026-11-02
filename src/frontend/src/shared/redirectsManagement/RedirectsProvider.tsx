import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ComponentType,
  type ReactNode,
} from "react";

import {
  EMERGENCY_CONTACTS_ANCHOR,
  PAGE_PATHS,
  PANEL_TARGETS,
  QUICK_EXIT_EVENT,
  pageFromPath,
  type PageTarget,
  type PanelTarget,
  type RedirectTarget,
} from "./targets";

export interface ConversationEntry {
  message: string;
  sendImmediately: boolean;
}

interface RedirectOptions {
  /** Ao abrir a conversa: texto inicial e se deve ser enviado na hora. */
  message?: string;
  sendImmediately?: boolean;
}

interface RedirectsContextValue {
  page: PageTarget;
  panel: PanelTarget | null;
  entry: ConversationEntry;
  /** Aumenta a cada Saída Rápida, para a página neutra trocar de conteúdo. */
  quickExitCount: number;
  redirect: (target: RedirectTarget, options?: RedirectOptions) => void;
  panels: Partial<Record<PanelTarget, ComponentType>>;
}

const RedirectsContext = createContext<RedirectsContextValue | null>(null);

const EMPTY_ENTRY: ConversationEntry = { message: "", sendImmediately: false };

interface RedirectsProviderProps {
  /** Componente de cada painel, registrado pela composição do app. */
  panels: Partial<Record<PanelTarget, ComponentType>>;
  children: ReactNode;
}

function focusConversation() {
  window.requestAnimationFrame(() => {
    document.querySelector<HTMLElement>(".chat-page__conversation")?.focus();
  });
}

export function RedirectsProvider({ panels, children }: RedirectsProviderProps) {
  const [page, setPage] = useState<PageTarget>(() => pageFromPath(window.location.pathname));
  const [panel, setPanel] = useState<PanelTarget | null>(null);
  const [entry, setEntry] = useState<ConversationEntry>(EMPTY_ENTRY);
  const [quickExitCount, setQuickExitCount] = useState(0);

  const goToPage = useCallback((target: PageTarget) => {
    window.history.replaceState(null, "", PAGE_PATHS[target]);
    setPanel(null);
    setPage(target);
  }, []);

  const redirect = useCallback(
    (target: RedirectTarget, options: RedirectOptions = {}) => {
      if (target === "quickExit") {
        // Não depende da rede: troca a tela antes de qualquer outra coisa.
        window.dispatchEvent(new Event(QUICK_EXIT_EVENT));
        setEntry(EMPTY_ENTRY);
        setQuickExitCount((count) => count + 1);
        goToPage("recipes");
        return;
      }
      if (target === "closePanel") {
        setPanel(null);
        focusConversation();
        return;
      }
      if (target === "emergencyContacts") {
        setPanel(null);
        window.requestAnimationFrame(() => {
          document
            .getElementById(EMERGENCY_CONTACTS_ANCHOR.section)
            ?.scrollIntoView({ behavior: "smooth", block: "start" });
          document
            .getElementById(EMERGENCY_CONTACTS_ANCHOR.title)
            ?.focus({ preventScroll: true });
        });
        return;
      }
      if ((PANEL_TARGETS as readonly string[]).includes(target)) {
        if (page !== "conversation") {
          window.history.replaceState(null, "", PAGE_PATHS.conversation);
          setPage("conversation");
        }
        setPanel(target as PanelTarget);
        return;
      }
      if (target === "conversation") {
        setEntry({
          message: options.message ?? "",
          sendImmediately: options.sendImmediately ?? false,
        });
      }
      goToPage(target as PageTarget);
    },
    [goToPage, page],
  );

  useEffect(() => {
    const handlePopState = () => {
      setPanel(null);
      setEntry(EMPTY_ENTRY);
      setPage(pageFromPath(window.location.pathname));
    };
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        redirect("quickExit");
      }
    };
    window.addEventListener("popstate", handlePopState);
    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("popstate", handlePopState);
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [redirect]);

  const value = useMemo(
    () => ({ page, panel, entry, quickExitCount, redirect, panels }),
    [page, panel, entry, quickExitCount, redirect, panels],
  );

  return <RedirectsContext.Provider value={value}>{children}</RedirectsContext.Provider>;
}

export function useRedirects(): RedirectsContextValue {
  const value = useContext(RedirectsContext);
  if (!value) {
    throw new Error("useRedirects precisa de RedirectsProvider.");
  }
  return value;
}

/** Renderiza o painel ativo registrado para a conversa, se houver. */
export function PanelOutlet() {
  const { panel, panels } = useRedirects();
  const Panel = panel ? panels[panel] : undefined;
  return Panel ? <Panel /> : null;
}
