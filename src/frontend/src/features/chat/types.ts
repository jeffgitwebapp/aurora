import type {
  KnowledgeStatus,
  OutOfScopeCategory,
  SourceReference,
} from "./api/chatApi";

export type MessageRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: MessageRole;
  text: string;
  knowledgeStatus?: KnowledgeStatus;
  outOfScopeCategory?: OutOfScopeCategory;
  sources?: SourceReference[];
  demo?: boolean;
}
