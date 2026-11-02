import { useEffect, useRef, useState, type FormEvent } from "react";

import { useRedirects } from "../../shared/redirectsManagement/RedirectsProvider";
import {
  recommendServices,
  ReferralApiError,
  type RecommendationResult,
} from "./api/referralApi";
import {
  formatCityState,
  nearestCapital,
  parseCityState,
  type CityState,
} from "./location";

type LocationState = "locating" | "unmatched" | "unavailable" | "idle";

type SearchState =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "result"; result: RecommendationResult }
  | { kind: "error"; message: string; location: CityState };

const LOCATION_MESSAGES: Record<Exclude<LocationState, "idle">, string> = {
  locating: "Procurando a cidade pela localização do aparelho…",
  unmatched:
    "Não consegui identificar sua cidade pela localização. Se quiser, digite abaixo.",
  unavailable:
    "A localização do aparelho não está disponível. Se quiser, digite sua cidade abaixo.",
};

export function ReferralPanel() {
  const { redirect } = useRedirects();
  const onBack = () => redirect("closePanel");
  const onOpenContacts = () => redirect("emergencyContacts");
  const onQuickExit = () => redirect("quickExit");
  const [locationState, setLocationState] = useState<LocationState>("idle");
  const [suggestedCity, setSuggestedCity] = useState<CityState | null>(null);
  const [cityText, setCityText] = useState("");
  const [inputError, setInputError] = useState<string | null>(null);
  const [search, setSearch] = useState<SearchState>({ kind: "idle" });
  const inputRef = useRef<HTMLInputElement | null>(null);
  const titleRef = useRef<HTMLHeadingElement | null>(null);
  const confirmRef = useRef<HTMLDialogElement | null>(null);
  const abortController = useRef<AbortController | null>(null);

  useEffect(() => {
    titleRef.current?.focus();
    if (!("geolocation" in navigator)) {
      setLocationState("unavailable");
      return;
    }

    let active = true;
    setLocationState("locating");
    navigator.geolocation.getCurrentPosition(
      ({ coords }) => {
        if (!active) {
          return;
        }
        const capital = nearestCapital(coords.latitude, coords.longitude);
        setLocationState(capital ? "idle" : "unmatched");
        setSuggestedCity(capital);
      },
      () => {
        if (active) {
          setLocationState("unavailable");
        }
      },
      { enableHighAccuracy: false, maximumAge: 0, timeout: 10000 },
    );
    return () => {
      active = false;
      abortController.current?.abort();
    };
  }, []);

  useEffect(() => {
    const dialog = confirmRef.current;
    if (suggestedCity && dialog && !dialog.open) {
      dialog.showModal();
    }
  }, [suggestedCity]);

  const runSearch = async (location: CityState) => {
    abortController.current?.abort();
    const controller = new AbortController();
    abortController.current = controller;
    setSearch({ kind: "loading" });
    try {
      const result = await recommendServices(location.city, location.state, controller.signal);
      setSearch({ kind: "result", result });
    } catch (err: unknown) {
      if (controller.signal.aborted) {
        return;
      }
      setSearch({
        kind: "error",
        message:
          err instanceof ReferralApiError
            ? err.message
            : "Ocorreu um erro inesperado ao consultar os serviços.",
        location,
      });
    }
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const location = parseCityState(cityText);
    if (!location) {
      setInputError("Informe a cidade e a UF, por exemplo: Recife / PE.");
      return;
    }
    setInputError(null);
    void runSearch(location);
  };

  const handleUseSuggestedCity = () => {
    if (!suggestedCity) {
      return;
    }
    setCityText(formatCityState(suggestedCity));
    setSuggestedCity(null);
    void runSearch(suggestedCity);
  };

  const handleTypeAnotherCity = () => {
    setSuggestedCity(null);
    setSearch({ kind: "idle" });
    setCityText("");
    window.requestAnimationFrame(() => inputRef.current?.focus());
  };

  const result = search.kind === "result" ? search.result : null;
  const verifiedDates = result?.services
    .map((service) => service.lastVerifiedAt)
    .filter((date): date is string => date !== null);

  return (
    <section className="referral" aria-labelledby="referral-title">
      <button type="button" className="referral__back" onClick={onBack}>
        ← Voltar à conversa
      </button>

      <h1 className="referral__title" id="referral-title" tabIndex={-1} ref={titleRef}>
        {result ? `Onde buscar ajuda em ${result.city} / ${result.state}` : "Onde buscar ajuda"}
      </h1>

      {locationState !== "idle" && (
        <p className="referral__status" role="status">
          {LOCATION_MESSAGES[locationState]}
        </p>
      )}

      <form className="referral__form" onSubmit={handleSubmit} noValidate>
        <label htmlFor="referral-city" className="referral__label">
          Cidade / UF (opcional)
        </label>
        <p className="referral__hint" id="referral-city-hint">
          Se quiser, diga sua cidade. Só uso isso para indicar serviços perto de você.
        </p>
        <div className="referral__input-group">
          <input
            ref={inputRef}
            id="referral-city"
            className="referral__input"
            type="text"
            autoComplete="off"
            placeholder="Ex.: Recife / PE"
            value={cityText}
            onChange={(event) => setCityText(event.target.value)}
            aria-describedby={
              inputError ? "referral-city-hint referral-city-error" : "referral-city-hint"
            }
            aria-invalid={inputError ? true : undefined}
          />
          <button
            type="submit"
            className="referral__submit"
            disabled={cityText.trim() === "" || search.kind === "loading"}
          >
            {search.kind === "loading" ? "Buscando..." : "Buscar"}
          </button>
        </div>
        {inputError && (
          <p className="referral__error" id="referral-city-error" role="alert">
            {inputError}
          </p>
        )}
      </form>

      {search.kind === "error" && (
        <div className="referral__alert" role="alert">
          <p>{search.message}</p>
          <button
            type="button"
            className="referral__action"
            onClick={() => void runSearch(search.location)}
          >
            Tentar novamente
          </button>
        </div>
      )}

      {result?.status === "found" && (
        <div className="referral__results" aria-live="polite">
          <p className="referral__intro">
            Até 3 opções, do serviço público à sociedade civil. Você escolhe se, quando
            e qual procurar.
          </p>
          <ol className="referral__cards">
            {result.services.map((service) => (
              <li key={service.id} className="referral-card">
                <p className="referral-card__category">
                  {service.priority} · {service.category}
                </p>
                <h2 className="referral-card__name">{service.name}</h2>
                <dl className="referral-card__details">
                  <dt>O que faz</dt>
                  <dd>{service.description}</dd>
                  <dt>Contato</dt>
                  <dd>{service.contact ?? "Não incluído na demonstração"}</dd>
                  <dt>Horário</dt>
                  <dd>{service.hours ?? "Não incluído na demonstração"}</dd>
                  <dt>Custo</dt>
                  <dd>{service.cost ?? "Não incluído na demonstração"}</dd>
                </dl>
              </li>
            ))}
          </ol>
          <p className="referral__footnote" role="note">
            {verifiedDates && verifiedDates.length === result.services.length
              ? `Contatos conferidos em ${verifiedDates.sort()[0]}. Nada desta busca fica salvo.`
              : "Demonstração: serviços fictícios, sem contatos verificados. Nada desta busca fica salvo."}
          </p>
        </div>
      )}

      {result?.status === "no_verified_result" && (
        <div className="referral__empty" aria-live="polite">
          <p>
            Não consegui confirmar serviços perto de você nesta demonstração. Os canais
            nacionais continuam disponíveis.
          </p>
          <div className="referral__actions">
            <button type="button" className="referral__action" onClick={onOpenContacts}>
              Ver canais nacionais
            </button>
            <button type="button" className="referral__action" onClick={handleTypeAnotherCity}>
              Tentar outra cidade
            </button>
            <button type="button" className="referral__action" onClick={onBack}>
              Voltar à conversa
            </button>
          </div>
          <p className="referral__footnote">Nada desta busca fica salvo.</p>
        </div>
      )}

      {suggestedCity && (
        <dialog
          ref={confirmRef}
          className="referral-confirm"
          aria-labelledby="referral-confirm-title"
          aria-modal="true"
          onCancel={(event) => event.preventDefault()}
        >
          <h2 id="referral-confirm-title">Confirmar sua cidade</h2>
          <p>
            Encontramos: <strong>{formatCityState(suggestedCity)}</strong>. Usar esta cidade
            para buscar serviços?
          </p>
          <p className="referral-confirm__note">
            A localização do aparelho foi usada só para sugerir a cidade mais próxima e não
            sai deste aparelho. Apenas a cidade confirmada é usada na busca.
          </p>
          <div className="referral-confirm__actions">
            <button
              type="button"
              className="referral-confirm__primary"
              onClick={handleUseSuggestedCity}
            >
              Usar esta cidade
            </button>
            <button type="button" className="referral__action" onClick={handleTypeAnotherCity}>
              Digitar outra cidade
            </button>
            <button type="button" className="risk-screen__quick-exit" onClick={onQuickExit}>
              Saída rápida (Esc)
            </button>
          </div>
        </dialog>
      )}
    </section>
  );
}
