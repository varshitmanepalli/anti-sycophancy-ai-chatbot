/**
 * Shared TypeScript types mirroring backend Pydantic schemas.
 */

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  conversation_id?: string;
  message: string;
}

export interface Message {
  role: "user" | "assistant" | "system";
  content: string;
}

export interface Conversation {
  id: string;
  messages: Message[];
}
