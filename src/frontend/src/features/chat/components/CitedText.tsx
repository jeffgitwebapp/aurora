import type { SourceReference } from "../api/chatApi";

interface CitedTextProps {
  text: string;
  sources: SourceReference[];
  anchorPrefix: string;
}

const CITATION = /\[(\d+)\]/g;

export function sourceAnchorId(anchorPrefix: string, index: number): string {
  return `${anchorPrefix}-source-${index}`;
}

/** Texto da resposta com cada marcador [n] ligado à fonte n da lista "Fontes". */
export function CitedText({ text, sources, anchorPrefix }: CitedTextProps) {
  const parts: React.ReactNode[] = [];
  let lastIndex = 0;

  for (const match of text.matchAll(CITATION)) {
    const position = match.index ?? 0;
    const number = Number(match[1]);
    const source = sources[number - 1];
    parts.push(text.slice(lastIndex, position));
    if (source) {
      parts.push(
        <a
          key={`${position}-${number}`}
          className="message-citation"
          href={`#${sourceAnchorId(anchorPrefix, number)}`}
          aria-label={`Fonte ${number}: ${source.title}`}
        >
          [{number}]
        </a>,
      );
    } else {
      parts.push(match[0]);
    }
    lastIndex = position + match[0].length;
  }
  parts.push(text.slice(lastIndex));

  return <>{parts}</>;
}
