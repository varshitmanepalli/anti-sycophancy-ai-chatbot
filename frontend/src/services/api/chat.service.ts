import type { ChatPipelineRequest, ChatPipelineResponse, ChatRequest, ChatResponse } from "@/types";

import { api } from "./client";

/** Send a message via the standard chat endpoint. */
export async function sendChatMessage(payload: ChatRequest): Promise<ChatResponse> {
  return api.post<ChatResponse>("/v1/chat/", payload);
}

/** Send a message through the full reasoning pipeline. */
export async function sendPipelineMessage(
  payload: ChatPipelineRequest,
): Promise<ChatPipelineResponse> {
  return api.post<ChatPipelineResponse>("/chat", payload);
}

/** Stream chat tokens via Server-Sent Events with reconnect support. */
export {
  streamChatMessage,
  streamChatWithRetry,
  StreamChatError,
  type StreamPhase as ServiceStreamPhase,
  type StreamErrorCode,
} from "./stream-chat.service";
