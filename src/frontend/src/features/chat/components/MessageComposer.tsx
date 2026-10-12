import { useState, type FormEvent } from "react";

interface MessageComposerProps {
  onSendMessage: (message: string) => Promise<void> | void;
  disabled?: boolean;
}

export function MessageComposer({ onSendMessage, disabled = false }: MessageComposerProps) {
  const [text, setText] = useState("");

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = text.trim();
    if (!trimmed || disabled) {
      return;
    }

    setText("");
    await onSendMessage(trimmed);
  };

  const isSubmitDisabled = disabled || text.trim() === "";

  return (
    <form className="message-composer" onSubmit={handleSubmit}>
      <label htmlFor="message-input" className="message-composer__label">
        Sua mensagem
      </label>
      <div className="message-composer__input-group">
        <input
          id="message-input"
          type="text"
          className="message-composer__input"
          placeholder="Digite sua mensagem..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          disabled={disabled}
          autoComplete="off"
        />
        <button
          type="submit"
          className="message-composer__button"
          disabled={isSubmitDisabled}
        >
          {disabled ? "Enviando..." : "Enviar"}
        </button>
      </div>
    </form>
  );
}

