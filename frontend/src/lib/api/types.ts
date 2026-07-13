import type { AxiosRequestConfig, InternalAxiosRequestConfig } from "axios";

/** Options for automatic request retries. */
export interface RetryOptions {
  /** Max retry attempts after the initial request (default: 2). */
  retries?: number;
  /** Base delay in ms — doubled each attempt with jitter (default: 1000). */
  retryDelayMs?: number;
  /** HTTP status codes that should trigger a retry. */
  retryOn?: number[];
}

/** Extended Axios request config used by the API layer. */
export interface ApiRequestConfig extends AxiosRequestConfig {
  /** Skip attaching the Authorization header. */
  skipAuth?: boolean;
  /** Skip automatic token refresh on 401. */
  skipRefresh?: boolean;
  /** Per-request retry overrides. Set `retries: 0` to disable. */
  retry?: RetryOptions | false;
  /** @internal — marks a retried request after refresh. */
  _retryAfterRefresh?: boolean;
  /** @internal — current retry attempt count. */
  _retryCount?: number;
}

export type ApiInternalConfig = InternalAxiosRequestConfig & ApiRequestConfig;

/** Standard auth token pair stored client-side. */
export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresAt?: number;
}

/** Placeholder refresh response — wire to your auth endpoint. */
export interface RefreshTokenResponse {
  access_token: string;
  refresh_token?: string;
  expires_in?: number;
}

/** Typed successful API result. */
export interface ApiResult<T> {
  data: T;
  status: number;
  headers: Record<string, string>;
}

/** SSE stream handler callbacks. */
export interface SseStreamOptions<TEvent> {
  url: string;
  method?: "GET" | "POST";
  body?: unknown;
  signal?: AbortSignal;
  headers?: Record<string, string>;
  onEvent: (event: TEvent) => void;
  /** Parse a single SSE `data:` line. Defaults to JSON.parse. */
  parseEvent?: (line: string) => TEvent | null;
  /** Called when the stream ends normally. */
  onComplete?: () => void;
  /** Called on connection open. */
  onOpen?: () => void;
}

export interface SseReaderOptions<TEvent> extends Omit<SseStreamOptions<TEvent>, "url"> {
  response: Response;
}
