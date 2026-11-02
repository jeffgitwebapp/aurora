import { createContext, useContext, useEffect, useRef, useState, type ReactNode } from "react";

import { QUICK_EXIT_EVENT } from "../redirectsManagement/targets";
import { logout, type AccountSession } from "./sessionApi";

interface SessionContextValue {
  session: AccountSession | null;
  setSession: (session: AccountSession | null) => void;
  /** Encerra no servidor sem esperar a rede e limpa o estado local. */
  endSession: () => void;
}

const SessionContext = createContext<SessionContextValue | null>(null);

/** Sessão da área logada só na memória da página: recarregar ou sair a encerra. */
export function SessionProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<AccountSession | null>(null);
  const sessionRef = useRef<AccountSession | null>(null);
  sessionRef.current = session;

  const endSession = () => {
    if (sessionRef.current) {
      logout(sessionRef.current.token);
    }
    setSession(null);
  };

  useEffect(() => {
    window.addEventListener(QUICK_EXIT_EVENT, endSession);
    return () => window.removeEventListener(QUICK_EXIT_EVENT, endSession);
  }, []);

  return (
    <SessionContext.Provider value={{ session, setSession, endSession }}>
      {children}
    </SessionContext.Provider>
  );
}

export function useSession(): SessionContextValue {
  const value = useContext(SessionContext);
  if (!value) {
    throw new Error("useSession precisa de SessionProvider.");
  }
  return value;
}

/** Contrato das seções exibidas em “Minha conta”, compostas pelo app. */
export interface AccountSectionProps {
  token: string;
  onSessionExpired: (message: string) => void;
  /** Pede para a página esconder as outras seções (ex.: leitura de um módulo). */
  onFocusChange: (isFocused: boolean) => void;
}
