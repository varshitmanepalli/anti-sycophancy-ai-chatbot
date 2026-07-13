import { authTokenStore } from "./auth-token-store";
import { ApiRequestError } from "./errors";
import type { SseReaderOptions, SseStreamOptions } from "./types";

export type StreamErrorCode = "aborted" | "network" | "server" | "offline" | "parse" | "timeout";

/** Typed error for SSE stream failures. */
export class StreamError extends Error {
  readonly code: StreamErrorCode;
  readonly retryable: boolean;
  readonly status?: number;

  constructor(message: string, code: StreamErrorCode, retryable = false, status?: number) {
    super(message);
    this.name = "StreamError";
    this.code = code;
    this.retryable = retryable;
    this.status = status;
  }
}

function defaultParseEvent<T>(line: string): T | null {
  if (!line.startsWith("data: ")) return null;
  try {
    return JSON.parse(line.slice(6)) as T;
  } catch {
    return null;
  }
}

function buildAuthHeaders(extra?: Record<string, string>): Record<string, string> {
  const headers: Record<string, string> = {
    Accept: "text/event-stream",
    ...extra,
  };

  const token = authTokenStore.getAccessToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  return headers;
}

/** Read SSE events from an open Response body. */
export async function readSseStream<TEvent>(
  options: SseReaderOptions<TEvent>,
): Promise<void> {
  const { response, signal, onEvent, onComplete, parseEvent = defaultParseEvent } = options;
  const reader = response.body?.getReader();

  if (!reader) {
    throw new StreamError("No response body", "server", true);
  }

  const decoder = new TextDecoder();
  let buffer = "";

  try {
    while (true) {
      if (signal?.aborted) {
        throw new StreamError("Stream aborted", "aborted");
      }

      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";

      for (const rawLine of lines) {
        const line = rawLine.trim();
        if (!line) continue;
        const event = parseEvent(line);
        if (event !== null) onEvent(event);
      }
    }
  } finally {
    reader.releaseLock();
  }

  onComplete?.();
}

/** Open an SSE connection via fetch (supports POST + auth headers). */
export async function openSseStream<TEvent>(
  baseUrl: string,
  options: SseStreamOptions<TEvent>,
): Promise<void> {
  const {
    url,
    method = "POST",
    body,
    signal,
    headers,
    onEvent,
    onComplete,
    onOpen,
    parseEvent,
  } = options;

  if (typeof navigator !== "undefined" && !navigator.onLine) {
    throw new StreamError("You appear to be offline", "offline", true);
  }

  const response = await fetch(`${baseUrl.replace(/\/$/, "")}${url}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...buildAuthHeaders(headers),
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
    signal,
  });

  if (!response.ok) {
    const text = await response.text().catch(() => "");
    const retryable = response.status >= 500 || response.status === 429;
    throw new StreamError(
      text || `Stream failed (${response.status})`,
      "server",
      retryable,
      response.status,
    );
  }

  onOpen?.();

  await readSseStream({
    response,
    signal,
    onEvent,
    onComplete,
    parseEvent,
  });
}

/** Map a StreamError to an ApiRequestError for unified handling. */
export function streamErrorToApiError(error: StreamError): ApiRequestError {
  return new ApiRequestError(error.message, {
    status: error.status,
    code: error.code === "offline" || error.code === "network" ? "NETWORK" : "SERVER",
    isRetryable: error.retryable,
  });
}
