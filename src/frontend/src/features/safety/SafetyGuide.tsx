import { useCallback, useEffect, useState, type FormEvent } from "react";

import { emergencyContacts } from "../../shared/components/EmergencyContacts";
import type { AccountSectionProps } from "../../shared/session/SessionProvider";
import { AccountApiError, SessionExpiredError } from "../../shared/session/sessionApi";
import {
  getSafetyGuide,
  SafetyGuideApiError,
  type SafetyGuideContent,
} from "./api/safetyGuideApi";
import {
  getSafetyPlan,
  saveSafetyPlan,
  type SafetyPlan,
  type TrustedContact,
} from "./api/safetyPlanApi";

type SafetyGuideProps = Pick<AccountSectionProps, "token" | "onSessionExpired">;

const MAX_CONTACTS = 5;
const MAX_NOTES = 4000;
const PHONE_PATTERN = /^[0-9+()\- ]{8,20}$/;

function validate(contacts: TrustedContact[], notes: string): string | null {
  for (const contact of contacts) {
    if (!contact.name.trim()) {
      return "Cada contato precisa de um nome ou apelido.";
    }
    const digits = contact.phone.replace(/\D/g, "").length;
    if (!PHONE_PATTERN.test(contact.phone.trim()) || digits < 8) {
      return `Informe um telefone válido para ${contact.name.trim()}.`;
    }
  }
  return notes.length > MAX_NOTES ? "As anotações podem ter até 4.000 caracteres." : null;
}

export function SafetyGuide({ token, onSessionExpired }: SafetyGuideProps) {
  const [guide, setGuide] = useState<SafetyGuideContent | null>(null);
  const [plan, setPlan] = useState<SafetyPlan | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [editing, setEditing] = useState<{ contacts: TrustedContact[]; notes: string } | null>(
    null,
  );
  const [formError, setFormError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoadError(null);
    try {
      const [content, savedPlan] = await Promise.all([getSafetyGuide(), getSafetyPlan(token)]);
      setGuide(content);
      setPlan(savedPlan);
    } catch (err: unknown) {
      if (err instanceof SessionExpiredError) {
        onSessionExpired(err.message);
        return;
      }
      setLoadError(
        err instanceof SafetyGuideApiError || err instanceof AccountApiError
          ? err.message
          : "Não foi possível carregar o guia.",
      );
    }
  }, [token, onSessionExpired]);

  useEffect(() => {
    void load();
  }, [load]);

  const startEditing = () => {
    setNotice(null);
    setFormError(null);
    setEditing({
      contacts: plan?.contacts.map((contact) => ({ ...contact })) ?? [],
      notes: plan?.notes ?? "",
    });
  };

  const updateContact = (index: number, field: keyof TrustedContact, value: string) => {
    if (!editing) {
      return;
    }
    const contacts = editing.contacts.map((contact, position) =>
      position === index ? { ...contact, [field]: value } : contact,
    );
    setEditing({ ...editing, contacts });
  };

  const handleSave = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!editing) {
      return;
    }
    const contacts = editing.contacts.filter(
      (contact) => contact.name.trim() || contact.phone.trim(),
    );
    const validationError = validate(contacts, editing.notes);
    if (validationError) {
      setFormError(validationError);
      return;
    }
    setIsSaving(true);
    setFormError(null);
    try {
      setPlan(await saveSafetyPlan(token, contacts, editing.notes));
      setEditing(null);
      setNotice("Plano salvo.");
    } catch (err: unknown) {
      if (err instanceof SessionExpiredError) {
        onSessionExpired(err.message);
        return;
      }
      setFormError(
        `${err instanceof AccountApiError ? err.message : "Não foi possível salvar."} Nada foi salvo.`,
      );
    } finally {
      setIsSaving(false);
    }
  };

  if (loadError) {
    return (
      <div className="referral__alert" role="alert">
        <p>{loadError}</p>
        <button type="button" className="referral__action" onClick={load}>
          Tentar novamente
        </button>
      </div>
    );
  }

  if (!guide || !plan) {
    return <p className="account__hint">Carregando o guia…</p>;
  }

  return (
    <div className="safety-guide">
      <p className="account__warning">
        Este guia é opcional e informativo. Ele não presume que você deva sair de casa ou do
        relacionamento e não substitui atendimento especializado. Você decide o que usar.
      </p>

      {guide.sections.map((section) => (
        <section key={section.title} className="safety-guide__section">
          <h3>{section.title}</h3>
          {section.paragraphs.map((paragraph, index) => (
            <p key={index}>{paragraph}</p>
          ))}
        </section>
      ))}

      <section className="safety-guide__section">
        <h3>Canais de apoio</h3>
        <ul className="safety-guide__channels">
          {emergencyContacts.map((contact) => (
            <li key={contact.number}>
              <a
                href={`tel:${contact.number}`}
                aria-label={`Ligar para ${contact.label}, ${contact.number}`}
              >
                {contact.label} · <strong>{contact.number}</strong>
              </a>
            </li>
          ))}
        </ul>
      </section>

      <section className="safety-guide__section" aria-labelledby="safety-plan-title">
        <h3 id="safety-plan-title">Meu plano</h3>
        {notice && (
          <p className="account__notice" role="status">
            {notice}
          </p>
        )}

        {editing ? (
          <form className="account__form" onSubmit={handleSave} noValidate>
            <p className="account__warning">
              Antes de salvar: contatos e anotações ficam cifrados com uma chave derivada da
              sua senha, na memória do servidor de demonstração, e somem quando ele reinicia.
              Não use dados reais. O Aurora nunca envia nada a esses contatos.
            </p>
            <fieldset className="safety-guide__contacts">
              <legend>Contatos de confiança (até {MAX_CONTACTS})</legend>
              {editing.contacts.map((contact, index) => (
                <div key={index} className="safety-guide__contact-row">
                  <label htmlFor={`contact-name-${index}`}>Nome ou apelido</label>
                  <input
                    id={`contact-name-${index}`}
                    className="referral__input"
                    maxLength={60}
                    value={contact.name}
                    onChange={(event) => updateContact(index, "name", event.target.value)}
                  />
                  <label htmlFor={`contact-phone-${index}`}>Telefone</label>
                  <input
                    id={`contact-phone-${index}`}
                    className="referral__input"
                    type="tel"
                    inputMode="tel"
                    maxLength={20}
                    value={contact.phone}
                    onChange={(event) => updateContact(index, "phone", event.target.value)}
                  />
                  <button
                    type="button"
                    className="referral__action safety-guide__remove"
                    onClick={() =>
                      setEditing({
                        ...editing,
                        contacts: editing.contacts.filter((_, position) => position !== index),
                      })
                    }
                  >
                    Remover contato
                  </button>
                </div>
              ))}
              {editing.contacts.length < MAX_CONTACTS && (
                <button
                  type="button"
                  className="referral__action safety-guide__remove"
                  onClick={() =>
                    setEditing({
                      ...editing,
                      contacts: [...editing.contacts, { name: "", phone: "" }],
                    })
                  }
                >
                  Adicionar contato
                </button>
              )}
            </fieldset>

            <label htmlFor="safety-notes">Anotações pessoais</label>
            <textarea
              id="safety-notes"
              className="referral__input journal__textarea"
              rows={5}
              maxLength={MAX_NOTES}
              value={editing.notes}
              onChange={(event) => setEditing({ ...editing, notes: event.target.value })}
            />

            {formError && (
              <p className="referral__error" role="alert">
                {formError}
              </p>
            )}
            <div className="account__actions">
              <button type="submit" className="referral__submit" disabled={isSaving}>
                {isSaving ? "Salvando..." : "Salvar plano"}
              </button>
              <button
                type="button"
                className="referral__action"
                onClick={() => {
                  setEditing(null);
                  setNotice("Nada foi salvo.");
                }}
              >
                Sair sem salvar
              </button>
            </div>
          </form>
        ) : (
          <>
            {plan.contacts.length === 0 && !plan.notes ? (
              <p className="account__hint">
                Nenhum contato ou anotação. Se quiser, você pode guardar pessoas de confiança e
                anotações.
              </p>
            ) : (
              <>
                {plan.contacts.length > 0 && (
                  <ul className="safety-guide__channels">
                    {plan.contacts.map((contact, index) => (
                      <li key={index}>
                        <a
                          href={`tel:${contact.phone.replace(/[^0-9+]/g, "")}`}
                          aria-label={`Ligar para ${contact.name}, ${contact.phone}`}
                        >
                          {contact.name} · <strong>{contact.phone}</strong>
                        </a>
                      </li>
                    ))}
                  </ul>
                )}
                {plan.notes && <p className="journal__description">{plan.notes}</p>}
              </>
            )}
            <div className="account__actions">
              <button type="button" className="referral__action" onClick={startEditing}>
                {plan.contacts.length === 0 && !plan.notes ? "Começar meu plano" : "Editar plano"}
              </button>
            </div>
            <p className="account__hint">
              Os telefones só são chamados se você tocar neles. O Aurora não envia mensagens.
            </p>
          </>
        )}
      </section>
    </div>
  );
}
