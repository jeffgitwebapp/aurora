import type { KnowledgeStatus, SourceReference } from "./api/chatApi";

export type MessageRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: MessageRole;
  text: string;
  knowledgeStatus?: KnowledgeStatus;
  sources?: SourceReference[];
  demo?: boolean;
}
