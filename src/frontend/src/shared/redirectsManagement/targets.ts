/**
 * Destinos conhecidos da aplicação. As features pedem um destino pelo nome e
 * não precisam conhecer a feature que o atende.
 */

export type PageTarget = "welcome" | "conversation" | "account" | "recipes";

/** Painéis abertos dentro da conversa, sem perder as mensagens. */
export type PanelTarget = "referral" | "questionnaire" | "saveConversation" | "safetyGuide";

/** Ações de navegação que não são uma página nem um painel. */
export type ActionTarget = "emergencyContacts" | "quickExit" | "closePanel";

export type RedirectTarget = PageTarget | PanelTarget | ActionTarget;

export const PAGE_PATHS: Record<PageTarget, string> = {
  welcome: "/",
  conversation: "/conversa",
  account: "/conta",
  recipes: "/receitas",
};

export const PANEL_TARGETS: readonly PanelTarget[] = [
  "referral",
  "questionnaire",
  "saveConversation",
  "safetyGuide",
];

/** Âncora dos contatos úteis na lateral da conversa. */
export const EMERGENCY_CONTACTS_ANCHOR = { section: "emergency-contacts", title: "emergency-title" };

/** Evento disparado na Saída Rápida para que cada parte descarte o próprio estado. */
export const QUICK_EXIT_EVENT = "aurora:quick-exit";

export function pageFromPath(pathname: string): PageTarget {
  const entry = Object.entries(PAGE_PATHS).find(([, path]) => path === pathname);
  return (entry?.[0] as PageTarget | undefined) ?? "welcome";
}
