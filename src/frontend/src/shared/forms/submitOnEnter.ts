import type { KeyboardEvent } from "react";

/** Enter envia o formulário; Shift+Enter quebra linha; durante composição (acentos/IME) não envia. */
export function submitOnEnter(event: KeyboardEvent<HTMLTextAreaElement>): void {
  if (event.key !== "Enter" || event.shiftKey || event.nativeEvent.isComposing) {
    return;
  }
  event.preventDefault();
  event.currentTarget.form?.requestSubmit();
}
