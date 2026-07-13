import {
  apiBaseUrl,
  openSseStream,
  StreamError,
  type StreamErrorCode,
} from "@/lib/api";
import type { ChatRequest, ChatStreamEvent } from "@/types";

import { sendChatMessage } from "./chat.service";

export type StreamPhase =
  | "connecting"
  | "streaming"
  | "reconnecting"
  | "completed"
  | "aborted"
  | "error";

export type { StreamErrorCode };

/** @deprecated Use StreamError from @/lib/api */
export class StreamChatError extends StreamError {
  constructor(message: string, code: StreamErrorCode, retryable = false, status?: number) {
    super(message, code, retryable, status);
    this.name = "StreamChatError";
  }
}

export interface StreamChatCallbacks {
  onToken: (token: string) => void;
  onComplete: (conversationId: string) => void;
  onPhaseChange?: (phase: StreamPhase, attempt?: number) => void;
}

export interface StreamChatOptions extends StreamChatCallbacks {
  payload: ChatRequest;
  signal?: AbortSignal;
  maxRetries?: number;
  baseRetryDelayMs?: number;
  fallbackToNonStreaming?: boolean;
}

const DEFAULT_MAX_RETRIES = 3;
const DEFAULT_BASE_RETRY_DELAY_MS = 1_000;

function isAbortError(error: unknown): boolean {
  if (error instanceof StreamError && error.code === "aborted") return true;
  if (error instanceof DOMException && error.name === "AbortError") return true;
  if (error instanceof Error && error.name === "AbortError") return true;
  return false;
}

function isRetryableError(error: unknown): boolean {
  if (isAbortError(error)) return false;
  if (error instanceof StreamError) return error.retryable;
  if (error instanceof TypeError) return true;
  return false;
}

function sleep(ms: number, signal?: AbortSignal): Promise<void> {
  return new Promise((resolve, reject) => {
    if (signal?.aborted) {
      reject(new StreamChatError("Stream aborted", "aborted"));
      return;
    }

    const timer = setTimeout(resolve, ms);

    const onAbort = () => {
      clearTimeout(timer);
      reject(new StreamChatError("Stream aborted", "aborted"));
    };

    signal?.addEventListener("abort", onAbort, { once: true });
  });
}

function backoffDelay(attempt: number, baseMs: number): number {
  const jitter = Math.random() * 200;
  return baseMs * 2 ** attempt + jitter;
}

async function streamOnce(
  payload: ChatRequest,
  callbacks: StreamChatCallbacks,
  signal?: AbortSignal,
): Promise<string> {
  let conversationId = payload.conversation_id ?? "";
  let accumulated = "";
  let receivedToken = false;

  await openSseStream<ChatStreamEvent>(apiBaseUrl, {
    url: "/v1/chat/stream",
    method: "POST",
    body: { ...payload, stream: true },
    signal,
    onOpen: () => callbacks.onPhaseChange?.("streaming"),
    onEvent: (event) => {
      conversationId = event.conversation_id;
      if (event.token) {
        receivedToken = true;
        accumulated += event.token;
        callbacks.onToken(event.token);
      }
      if (event.done) {
        callbacks.onComplete(conversationId);
        callbacks.onPhaseChange?.("completed");
      }
    },
  });

  if (receivedToken) {
    callbacks.onComplete(conversationId);
    callbacks.onPhaseChange?.("completed");
    return accumulated;
  }

  throw new StreamChatError("Stream ended unexpectedly", "network", true);
}

/**
 * Stream chat tokens with automatic reconnect, abort support, and optional
 * non-streaming fallback when retries are exhausted.
 */
export async function streamChatWithRetry(options: StreamChatOptions): Promise<string> {
  const {
    payload,
    onToken,
    onComplete,
    onPhaseChange,
    signal,
    maxRetries = DEFAULT_MAX_RETRIES,
    baseRetryDelayMs = DEFAULT_BASE_RETRY_DELAY_MS,
    fallbackToNonStreaming = true,
  } = options;

  let attempt = 0;
  let lastError: unknown;

  while (attempt <= maxRetries) {
    if (signal?.aborted) {
      onPhaseChange?.("aborted");
      throw new StreamChatError("Stream aborted", "aborted");
    }

    const phase: StreamPhase = attempt === 0 ? "connecting" : "reconnecting";
    onPhaseChange?.(phase, attempt);

    try {
      return await streamOnce(payload, { onToken, onComplete, onPhaseChange }, signal);
    } catch (error) {
      lastError = error;

      if (isAbortError(error)) {
        onPhaseChange?.("aborted");
        throw error instanceof StreamChatError
          ? error
          : new StreamChatError("Stream aborted", "aborted");
      }

      if (!isRetryableError(error) || attempt >= maxRetries) {
        break;
      }

      attempt += 1;
      onPhaseChange?.("reconnecting", attempt);
      await sleep(backoffDelay(attempt - 1, baseRetryDelayMs), signal);
    }
  }

  if (fallbackToNonStreaming && !signal?.aborted) {
    onPhaseChange?.("connecting", attempt);
    try {
      const response = await sendChatMessage(payload);
      onToken(response.message);
      onComplete(response.conversation_id);
      onPhaseChange?.("completed");
      return response.message;
    } catch (fallbackError) {
      lastError = fallbackError;
    }
  }

  onPhaseChange?.("error");
  if (lastError instanceof StreamChatError) throw lastError;

  const message =
    lastError instanceof Error ? lastError.message : "Failed to generate response";
  throw new StreamChatError(message, "network", false);
}

/** @deprecated Use streamChatWithRetry */
export async function streamChatMessage(
  payload: ChatRequest,
  onToken: (token: string) => void,
  onComplete: (conversationId: string) => void,
  signal?: AbortSignal,
): Promise<void> {
  await streamChatWithRetry({ payload, onToken, onComplete, signal, fallbackToNonStreaming: false });
}
