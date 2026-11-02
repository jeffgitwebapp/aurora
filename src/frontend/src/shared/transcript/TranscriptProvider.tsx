import { createContext, useContext, useState, type ReactNode } from "react";

export interface TranscriptMessage {
  role: "user" | "assistant";
  text: string;
}

interface TranscriptContextValue {
  messages: TranscriptMessage[];
  setMessages: (messages: TranscriptMessage[]) => void;
}

const TranscriptContext = createContext<TranscriptContextValue | null>(null);

/**
 * Cópia somente de papel e texto da conversa aberta, para features que precisam
 * lê-la (ex.: salvar na conta) sem depender da feature de conversa.
 */
export function TranscriptProvider({ children }: { children: ReactNode }) {
  const [messages, setMessages] = useState<TranscriptMessage[]>([]);
  return (
    <TranscriptContext.Provider value={{ messages, setMessages }}>
      {children}
    </TranscriptContext.Provider>
  );
}

export function useTranscript(): TranscriptContextValue {
  const value = useContext(TranscriptContext);
  if (!value) {
    throw new Error("useTranscript precisa de TranscriptProvider.");
  }
  return value;
}
