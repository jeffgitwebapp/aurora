const emergencyContacts = [
  { label: "Polícia Militar", number: "190" },
  { label: "Central de Atendimento à Mulher", number: "180" },
  { label: "SAMU", number: "192" },
  { label: "CVV", number: "188" },
] as const;

interface EmergencyContactsProps {
  compact?: boolean;
}

export function EmergencyContacts({ compact = false }: EmergencyContactsProps) {
  return (
    <section
      id={compact ? "welcome-emergency-contacts" : "emergency-contacts"}
      className={`emergency-card${compact ? " emergency-card--compact" : ""}`}
      aria-labelledby={compact ? "welcome-emergency-title" : "emergency-title"}
      tabIndex={-1}
    >
      {!compact && <p className="emergency-card__eyebrow">Ajuda por telefone</p>}
      <h2
        className="emergency-card__title"
        id={compact ? "welcome-emergency-title" : "emergency-title"}
        tabIndex={-1}
      >
        Em perigo agora?
      </h2>
      <ul className="emergency-card__list">
        {emergencyContacts.map(({ label, number }) => (
          <li key={number}>
            <a href={`tel:${number}`} aria-label={`Ligar para ${label}, ${number}`}>
              <span>{label}</span>
              <strong>{number}</strong>
            </a>
          </li>
        ))}
      </ul>
    </section>
  );
}
