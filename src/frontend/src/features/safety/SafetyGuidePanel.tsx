import { useCallback, useEffect, useRef, useState } from "react";

import { AccountForm } from "../account/AccountForm";
import type { AccountSession } from "../account/api/accountApi";
import { SafetyGuide } from "./SafetyGuide";

interface SafetyGuidePanelProps {
  session: AccountSession | null;
  onSessionChange: (session: AccountSession | null) => void;
  onBack: () => void;
}

/** Guia aberto dentro da conversa: a conversa continua preservada ao fundo. */
export function SafetyGuidePanel({ session, onSessionChange, onBack }: SafetyGuidePanelProps) {
  const [notice, setNotice] = useState<string | null>(null);
  const titleRef = useRef<HTMLHeadingElement | null>(null);

  useEffect(() => {
    titleRef.current?.focus();
  }, [session]);

  const handleSessionExpired = useCallback(
    (message: string) => {
      onSessionChange(null);
      setNotice(message);
    },
    [onSessionChange],
  );

  return (
    <section className="questionnaire save-conversation" aria-labelledby="account-title">
      <button type="button" className="referral__back" onClick={onBack}>
        ← Voltar à conversa
      </button>
      {session ? (
        <>
          <h1 id="account-title" className="account__title" tabIndex={-1} ref={titleRef}>
            Guia de segurança
          </h1>
          <SafetyGuide token={session.token} onSessionExpired={handleSessionExpired} />
        </>
      ) : (
        <div className="save-conversation__form">
          <AccountForm
            title="Entre para abrir o guia de segurança"
            notice={notice}
            onAuthenticated={(created) => {
              setNotice(null);
              onSessionChange(created);
            }}
          />
          <p className="account__hint">
            O guia fica na área logada. A conversa continua aberta enquanto você entra.
          </p>
        </div>
      )}
    </section>
  );
}
