import { useState, type FormEvent } from "react";

interface MessageComposerProps {
  onSendMessage: (message: string) => Promise<void> | void;
  disabled?: boolean;
  initialText?: string;
}

export function MessageComposer({
  onSendMessage,
  disabled = false,
  initialText = "",
}: MessageComposerProps) {
  const [text, setText] = useState(initialText);

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
      <label htmlFor="message-input" className="visually-hidden">
        Sua mensagem
      </label>
      <div className="message-composer__input-group">
        <textarea
          id="message-input"
          className="message-composer__input"
          rows={2}
          placeholder="Escreva aqui…"
          value={text}
          onChange={(e) => setText(e.target.value)}
          disabled={disabled}
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
