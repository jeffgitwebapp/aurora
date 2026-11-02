import { useEffect, useRef } from "react";

import { EmergencyContacts, type EmergencyNumber } from "./EmergencyContacts";

interface RiskScreenProps {
  kind: "acute" | "indeterminate";
  priorityNumbers?: readonly EmergencyNumber[];
  onReturn: () => void;
  onQuickExit: () => void;
}

/** Modal de risco sobre a tela atual; é a única exceção à regra de não usar modais. */
export function RiskScreen({
  kind,
  priorityNumbers = [],
  onReturn,
  onQuickExit,
}: RiskScreenProps) {
  const dialogRef = useRef<HTMLDialogElement | null>(null);
  const isAcute = kind === "acute";

  useEffect(() => {
    const dialog = dialogRef.current;
    if (dialog && !dialog.open) {
      dialog.showModal();
      dialog.focus();
    }
  }, []);

  return (
    <dialog
      ref={dialogRef}
      className="risk-screen risk-screen--modal"
      aria-labelledby="risk-screen-title"
      aria-modal="true"
      tabIndex={-1}
      onCancel={(event) => event.preventDefault()}
    >
      <div className="risk-screen__content">
        <p className="risk-screen__eyebrow">{isAcute ? "Ajuda agora" : "Resultado incerto"}</p>
        <h1 id="risk-screen-title">
          {isAcute
            ? "Você pode estar em perigo agora."
            : "Não foi possível avaliar esta mensagem."}
        </h1>
        <p className="risk-screen__intro">
          {isAcute
            ? "Se puder, ligue para um destes números. As ligações são gratuitas e funcionam mesmo sem internet."
            : "Isso não significa que não exista risco. Se precisar, você pode escolher um dos canais de apoio abaixo. Nenhuma resposta informativa foi gerada."}
        </p>
        <EmergencyContacts variant="risk" priorityNumbers={isAcute ? priorityNumbers : []} />
        <p className="risk-screen__note">
          O Aurora não liga para ninguém por você. Você decide se e quando ligar.
        </p>
        <p className="risk-screen__demo" role="note">
          Demonstração: a triagem usa frases de teste e não avalia situações reais.
        </p>
      </div>
      <div className="risk-screen__actions">
        <button className="risk-screen__return" type="button" onClick={onReturn}>
          Voltar à conversa
        </button>
        <button className="risk-screen__quick-exit" type="button" onClick={onQuickExit}>
          Saída rápida (Esc)
        </button>
      </div>
    </dialog>
  );
}
