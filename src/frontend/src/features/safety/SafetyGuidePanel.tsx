import { useCallback, useEffect, useRef, useState } from "react";

import { useRedirects } from "../../shared/redirectsManagement/RedirectsProvider";
import { AccountForm } from "../../shared/session/AccountForm";
import { useSession } from "../../shared/session/SessionProvider";
import { SafetyGuide } from "./SafetyGuide";

/** Guia aberto dentro da conversa: a conversa continua preservada ao fundo. */
export function SafetyGuidePanel() {
  const { session, setSession: onSessionChange } = useSession();
  const { redirect } = useRedirects();
  const onBack = () => redirect("closePanel");
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
