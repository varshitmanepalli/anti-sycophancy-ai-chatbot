/** Chat domain types mirroring backend Pydantic schemas. */

export type MessageRole = "user" | "assistant" | "system";

export type ChatMode = "standard" | "reasoning";

/** Lifecycle phase for an in-flight streamed assistant response. */
export type StreamPhase =
  | "connecting"
  | "streaming"
  | "reconnecting"
  | "completed"
  | "aborted"
  | "error";

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  createdAt: string;
  isStreaming?: boolean;
  streamPhase?: StreamPhase;
  error?: string | null;
  /** Set when the user stops generation before completion. */
  wasAborted?: boolean;
}

/** Tracks the active stream for a conversation (used by UI chrome). */
export interface ActiveStream {
  conversationId: string;
  messageId: string;
  phase: StreamPhase;
  attempt: number;
  maxAttempts: number;
}

export interface ReasoningStep {
  label: string;
  content: string;
}

export interface ReasoningItem {
  text: string;
  confidence: number;
  source?: string | null;
}

export interface StructuredReasoning {
  facts: ReasoningItem[];
  assumptions: ReasoningItem[];
  evidence: ReasoningItem[];
  counterarguments: ReasoningItem[];
  confidence_score: number;
  alternative_explanations: ReasoningItem[];
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  stream?: boolean;
}

export interface ChatResponse {
  conversation_id: string;
  message: string;
  model?: string | null;
}

export interface ChatStreamEvent {
  conversation_id: string;
  token: string;
  done: boolean;
}

export interface ChatPipelineRequest {
  user_id?: string;
  conversation_id?: string;
  message: string;
}

export interface ChatPipelineResponse {
  response: string;
  confidence: number;
  category?: string | null;
  reasoning_steps: ReasoningStep[];
  structured_reasoning?: StructuredReasoning | null;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: string;
  updatedAt: string;
  mode: ChatMode;
  pinned?: boolean;
  pinnedAt?: string | null;
  structuredReasoning?: StructuredReasoning | null;
}

export type ConversationFilter = "all" | "pinned" | "standard" | "reasoning";
