import { useEffect, useRef, useState } from "react";

import {
  fetchQuestions,
  QuestionnaireApiError,
  submitAnswers,
  type HelpType,
  type Question,
  type QuestionnaireResult,
} from "./api/questionnaireApi";

const HELP_TYPE_LABELS: Record<HelpType, string> = {
  report: "Denúncia",
  legal: "Orientação jurídica",
  psychological: "Apoio psicológico",
  peer: "Apoio entre pares",
};

interface QuestionnairePanelProps {
  onStop: () => void;
  onEmergency: () => void;
  onOpenReferral: () => void;
}

type LoadState =
  | { kind: "loading" }
  | { kind: "error"; message: string }
  | { kind: "ready"; questions: Question[] };

export function QuestionnairePanel({
  onStop,
  onEmergency,
  onOpenReferral,
}: QuestionnairePanelProps) {
  const [loadState, setLoadState] = useState<LoadState>({ kind: "loading" });
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<QuestionnaireResult | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);
  const headingRef = useRef<HTMLHeadingElement | null>(null);
  const abortController = useRef<AbortController | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    setLoadState({ kind: "loading" });
    fetchQuestions(controller.signal)
      .then((questions) => setLoadState({ kind: "ready", questions }))
      .catch((err: unknown) => {
        if (!controller.signal.aborted) {
          setLoadState({
            kind: "error",
            message:
              err instanceof QuestionnaireApiError
                ? err.message
                : "Ocorreu um erro inesperado ao carregar o questionário.",
          });
        }
      });
    return () => {
      controller.abort();
      abortController.current?.abort();
    };
  }, [reloadKey]);

  useEffect(() => {
    headingRef.current?.focus();
  }, [step, result, loadState.kind]);

  const questions = loadState.kind === "ready" ? loadState.questions : [];
  const question = questions[step];
  const isLastStep = step === questions.length - 1;

  const handleSubmit = async () => {
    abortController.current?.abort();
    const controller = new AbortController();
    abortController.current = controller;
    setIsSubmitting(true);
    setSubmitError(null);
    try {
      setResult(await submitAnswers(answers, controller.signal));
    } catch (err: unknown) {
      if (!controller.signal.aborted) {
        setSubmitError(
          err instanceof QuestionnaireApiError
            ? err.message
            : "Ocorreu um erro inesperado ao calcular o resultado.",
        );
      }
    } finally {
      if (abortController.current === controller) {
        setIsSubmitting(false);
      }
    }
  };

  const emergencyButton = (
    <button type="button" className="questionnaire__emergency" onClick={onEmergency}>
      Estou em perigo agora
    </button>
  );

  return (
    <section className="questionnaire" aria-labelledby="questionnaire-title">
      <div className="questionnaire__top">
        <button type="button" className="referral__back" onClick={onStop}>
          {result ? "← Voltar à conversa" : "Parar questionário"}
        </button>
        {emergencyButton}
      </div>

      {loadState.kind === "loading" && (
        <p className="questionnaire__status" role="status">
          Carregando o questionário…
        </p>
      )}

      {loadState.kind === "error" && (
        <div className="referral__alert" role="alert">
          <p>{loadState.message}</p>
          <button
            type="button"
            className="referral__action"
            onClick={() => setReloadKey((key) => key + 1)}
          >
            Tentar novamente
          </button>
        </div>
      )}

      {question && !result && (
        <>
          <p className="questionnaire__progress">
            Passo {step + 1} de {questions.length}
          </p>
          <fieldset className="questionnaire__fieldset">
            <legend>
              <h1
                id="questionnaire-title"
                className="questionnaire__title"
                tabIndex={-1}
                ref={headingRef}
              >
                {question.title}
              </h1>
            </legend>
            {question.options.map((option) => (
              <label key={option.id} className="questionnaire__option">
                <input
                  type="radio"
                  name={question.id}
                  value={option.id}
                  checked={answers[question.id] === option.id}
                  onChange={() =>
                    setAnswers((prev) => ({ ...prev, [question.id]: option.id }))
                  }
                />
                <span>{option.label}</span>
              </label>
            ))}
          </fieldset>

          {submitError && (
            <p className="referral__error" role="alert">
              {submitError}
            </p>
          )}

          <div className="questionnaire__nav">
            {step > 0 && (
              <button
                type="button"
                className="referral__action"
                onClick={() => setStep((current) => current - 1)}
              >
                Voltar
              </button>
            )}
            <button
              type="button"
              className="referral__submit"
              disabled={!answers[question.id] || isSubmitting}
              onClick={() =>
                isLastStep ? void handleSubmit() : setStep((current) => current + 1)
              }
            >
              {isLastStep ? (isSubmitting ? "Calculando..." : "Ver resultado") : "Continuar"}
            </button>
          </div>

          <p className="questionnaire__note" role="note">
            Demonstração: as perguntas 1 e 2 são provisórias e não fazem parte de um
            instrumento aprovado. Você pode parar quando quiser; nada é guardado.
          </p>
        </>
      )}

      {result && (
        <div className="questionnaire__result" aria-live="polite">
          <h1
            id="questionnaire-title"
            className="questionnaire__title"
            tabIndex={-1}
            ref={headingRef}
          >
            Resultado de demonstração
          </h1>
          <p className="questionnaire__band">Faixa de demonstração {result.band}</p>
          <p className="questionnaire__disclaimer">
            Esta faixa é fictícia e foi calculada só para testar a tela. Ela não indica
            padrão de violência, risco nem diagnóstico.
          </p>
          <p>
            Tipo de ajuda escolhido:{" "}
            <strong>
              {result.helpType ? HELP_TYPE_LABELS[result.helpType] : "Prefiro não responder"}
            </strong>
          </p>
          <div className="questionnaire__nav">
            <button type="button" className="referral__submit" onClick={onOpenReferral}>
              Onde buscar ajuda
            </button>
            <button type="button" className="referral__action" onClick={onStop}>
              Conversar com a Aurora
            </button>
          </div>
          <p className="questionnaire__note">As respostas não ficam salvas.</p>
        </div>
      )}
    </section>
  );
}
