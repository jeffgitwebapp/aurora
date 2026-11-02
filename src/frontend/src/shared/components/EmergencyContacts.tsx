export const emergencyContacts = [
  { label: "Polícia Militar", number: "190" },
  { label: "Central de Atendimento à Mulher", number: "180" },
  { label: "SAMU", number: "192" },
  { label: "CVV · Centro de Valorização da Vida", number: "188" },
] as const;

export type EmergencyNumber = (typeof emergencyContacts)[number]["number"];

interface EmergencyContactsProps {
  compact?: boolean;
  variant?: "default" | "risk";
  /** Números a destacar; quem chama decide, este componente não conhece a triagem. */
  priorityNumbers?: readonly EmergencyNumber[];
}

export function EmergencyContacts({
  compact = false,
  variant = "default",
  priorityNumbers = [],
}: EmergencyContactsProps) {
  const contacts = emergencyContacts.map((contact) => ({
    ...contact,
    priority: priorityNumbers.includes(contact.number),
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
      {!compact && variant !== "risk" && (
        <p className="emergency-card__eyebrow">Ajuda por telefone</p>
      )}
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
      <ul className="emergency-card__list">
        {contacts.map(({ label, number, priority }) => (
          <li key={number}>
            <a
              className={priority ? "emergency-card__link--priority" : undefined}
              href={`tel:${number}`}
              aria-label={`Ligar para ${label}, ${number}${priority ? ", canal destacado" : ""}`}
            >
              {variant === "risk" && <strong>{number}</strong>}
              <span>
                {label}
                {priority && (
                  <strong className="emergency-card__priority">Prioritário</strong>
                )}
              </span>
              {variant !== "risk" && <strong>{number}</strong>}
            </a>
          </li>
        ))}
      </ul>
    </section>
  );
}
