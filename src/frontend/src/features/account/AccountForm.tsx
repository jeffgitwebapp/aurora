import { useEffect, useRef, useState, type FormEvent } from "react";

import {
  AccountApiError,
  login,
  registerAccount,
  type AccountSession,
} from "./api/accountApi";

const NICKNAME_PATTERN = /^[A-Za-z0-9._-]{3,30}$/;
const NICKNAME_RULE =
  "De 3 a 30 caracteres: letras, números, ponto, hífen ou sublinhado.";
const PASSWORD_RULE = "Pelo menos 10 caracteres, com letras e números.";

type Mode = "login" | "register";

interface AccountFormProps {
  onAuthenticated: (session: AccountSession) => void;
  /** Título exibido acima das opções; por padrão, o nome da opção escolhida. */
  title?: string;
  notice?: string | null;
}

function validateRegistration(nickname: string, password: string, confirmation: string) {
  if (!NICKNAME_PATTERN.test(nickname)) {
    return `Apelido inválido. ${NICKNAME_RULE}`;
  }
  if (password.length < 10 || !/[A-Za-z]/.test(password) || !/\d/.test(password)) {
    return `Senha fraca. ${PASSWORD_RULE}`;
  }
  if (password !== confirmation) {
    return "As senhas não são iguais.";
  }
  return null;
}

export function AccountForm({ onAuthenticated, title, notice = null }: AccountFormProps) {
  const [mode, setMode] = useState<Mode>("login");
  const [nickname, setNickname] = useState("");
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const titleRef = useRef<HTMLHeadingElement | null>(null);

  useEffect(() => {
    titleRef.current?.focus();
  }, [mode]);

  const switchMode = (next: Mode) => {
    setMode(next);
    setPassword("");
    setConfirmation("");
    setError(null);
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmedNickname = nickname.trim();
    if (mode === "register") {
      const validationError = validateRegistration(trimmedNickname, password, confirmation);
      if (validationError) {
        setError(validationError);
        return;
      }
    } else if (!trimmedNickname || !password) {
      setError("Informe o apelido e a senha.");
      return;
    }

    setIsSubmitting(true);
    setError(null);
    try {
      const created =
        mode === "register"
          ? await registerAccount(trimmedNickname, password)
          : await login(trimmedNickname, password);
      setPassword("");
      setConfirmation("");
      onAuthenticated(created);
    } catch (err: unknown) {
      setError(
        err instanceof AccountApiError ? err.message : "Ocorreu um erro inesperado.",
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <h1 id="account-title" className="account__title" tabIndex={-1} ref={titleRef}>
        {title ?? (mode === "login" ? "Entrar" : "Criar conta")}
      </h1>
      {notice && (
        <p className="account__notice" role="status">
          {notice}
        </p>
      )}
      <div className="account__tabs" role="group" aria-label="Escolha uma opção">
        <button
          type="button"
          className="account__tab"
          aria-pressed={mode === "login"}
          onClick={() => switchMode("login")}
        >
          Entrar
        </button>
        <button
          type="button"
          className="account__tab"
          aria-pressed={mode === "register"}
          onClick={() => switchMode("register")}
        >
          Criar conta
        </button>
      </div>

      <form className="account__form" onSubmit={handleSubmit} noValidate>
        <label htmlFor="account-nickname">Apelido</label>
        {mode === "register" && (
          <p className="account__hint" id="account-nickname-hint">
            {NICKNAME_RULE}
          </p>
        )}
        <input
          id="account-nickname"
          className="referral__input"
          autoComplete="username"
          value={nickname}
          maxLength={30}
          onChange={(event) => setNickname(event.target.value)}
          aria-describedby={mode === "register" ? "account-nickname-hint" : undefined}
        />

        <label htmlFor="account-password">Senha</label>
        {mode === "register" && (
          <p className="account__hint" id="account-password-hint">
            {PASSWORD_RULE}
          </p>
        )}
        <input
          id="account-password"
          className="referral__input"
          type={showPassword ? "text" : "password"}
          autoComplete={mode === "register" ? "new-password" : "current-password"}
          value={password}
          maxLength={128}
          onChange={(event) => setPassword(event.target.value)}
          aria-describedby={mode === "register" ? "account-password-hint" : undefined}
        />

        {mode === "register" && (
          <>
            <label htmlFor="account-confirmation">Confirmar senha</label>
            <input
              id="account-confirmation"
              className="referral__input"
              type={showPassword ? "text" : "password"}
              autoComplete="new-password"
              value={confirmation}
              maxLength={128}
              onChange={(event) => setConfirmation(event.target.value)}
            />
          </>
        )}

        <label className="account__toggle">
          <input
            type="checkbox"
            checked={showPassword}
            onChange={(event) => setShowPassword(event.target.checked)}
          />
          Mostrar senha
        </label>

        {mode === "register" ? (
          <p className="account__warning">
            Não use seu nome real nem uma senha que você usa em outro lugar. Não é preciso
            e-mail nem telefone.
          </p>
        ) : (
          <p className="account__hint">
            Sem e-mail, não é possível recuperar a senha. Guarde-a em lugar seguro.
          </p>
        )}

        {error && (
          <p className="referral__error" role="alert">
            {error}
          </p>
        )}

        <button type="submit" className="referral__submit" disabled={isSubmitting}>
          {isSubmitting ? "Aguarde..." : mode === "login" ? "Entrar" : "Criar conta"}
        </button>
      </form>
    </>
  );
}
