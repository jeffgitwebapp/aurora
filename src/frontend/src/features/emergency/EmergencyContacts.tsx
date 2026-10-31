import type { TriageSignal } from "../chat/api/chatApi";

const emergencyContacts = [
  { label: "Polícia Militar", number: "190" },
  { label: "Central de Atendimento à Mulher", number: "180" },
  { label: "SAMU", number: "192" },
  { label: "CVV · Centro de Valorização da Vida", number: "188" },
] as const;

interface EmergencyContactsProps {
  compact?: boolean;
  variant?: "default" | "risk";
  signals?: TriageSignal[];
}

export function EmergencyContacts({
  compact = false,
  variant = "default",
  signals = [],
}: EmergencyContactsProps) {
  const priorityNumbers = new Set<string>();
  if (variant === "risk") {
    if (
      signals.some(
        (signal) =>
          signal === "ongoing_assault" ||
          signal === "death_threat" ||
          signal === "weapon_present",
      )
    ) {
      priorityNumbers.add("190");
    }
    if (signals.includes("suicidal_ideation")) {
      priorityNumbers.add("188");
    }
  }
  const contacts = emergencyContacts.map((contact) => ({
    ...contact,
    priority: priorityNumbers.has(contact.number),
  }));
  return (
    <section
      id={
        compact
          ? "welcome-emergency-contacts"
          : variant === "risk"
            ? "risk-emergency-contacts"
            : "emergency-contacts"
      }
      className={`emergency-card${compact ? " emergency-card--compact" : ""}${variant === "risk" ? " emergency-card--risk" : ""}`}
      aria-labelledby={
        compact
          ? "welcome-emergency-title"
          : variant === "risk"
            ? "risk-emergency-title"
            : "emergency-title"
      }
      tabIndex={-1}
    >
      {!compact && <p className="emergency-card__eyebrow">Ajuda por telefone</p>}
      <h2
        className="emergency-card__title"
        id={
          compact
            ? "welcome-emergency-title"
            : variant === "risk"
              ? "risk-emergency-title"
              : "emergency-title"
        }
        tabIndex={-1}
      >
        {variant === "risk" ? "Canais de apoio" : "Em perigo agora?"}
      </h2>
      {variant === "risk" && (
        <>
          <p className="emergency-card__hint">
            Os canais abaixo são opções. Escolha se e quando deseja ligar.
          </p>
          <p className="emergency-card__hint">
            190: polícia; 192: urgência médica; 180: orientação para mulheres;
            188: apoio emocional.
          </p>
        </>
      )}
      <ul className="emergency-card__list">
        {contacts.map(({ label, number, priority }) => (
          <li key={number}>
            <a
              className={priority ? "emergency-card__link--priority" : undefined}
              href={`tel:${number}`}
              aria-label={`Ligar para ${label}, ${number}${priority ? ", canal destacado" : ""}`}
            >
              <span>
                {label}
                {priority && (
                  <strong className="emergency-card__priority">Prioritário</strong>
                )}
              </span>
              <strong>{number}</strong>
            </a>
          </li>
        ))}
      </ul>
    </section>
  );
}
