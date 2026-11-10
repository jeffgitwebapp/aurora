import type { SourceReference } from "../api/chatApi";

interface CitedTextProps {
  text: string;
  sources: SourceReference[];
  onOpenSource: (index: number) => void;
}

const CITATION = /\[(\d+)\]/g;

/** Texto da resposta com cada marcador [n] abrindo a fonte n no modal de fontes. */
export function CitedText({ text, sources, onOpenSource }: CitedTextProps) {
  const parts: React.ReactNode[] = [];
  let lastIndex = 0;

  for (const match of text.matchAll(CITATION)) {
    const position = match.index ?? 0;
    const number = Number(match[1]);
    const source = sources[number - 1];
    parts.push(text.slice(lastIndex, position));
    if (source) {
      parts.push(
        <button
          key={`${position}-${number}`}
          type="button"
          className="message-citation"
          aria-label={`Fonte ${number}: ${source.title}`}
          onClick={() => onOpenSource(number)}
        >
          [{number}]
        </button>,
      );
    } else {
      parts.push(match[0]);
    }
    lastIndex = position + match[0].length;
  }
  parts.push(text.slice(lastIndex));

  return <>{parts}</>;
}
