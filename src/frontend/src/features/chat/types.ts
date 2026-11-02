import type {
  ContentOffer,
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
  offer?: ContentOffer;
  sources?: SourceReference[];
  demo?: boolean;
}
