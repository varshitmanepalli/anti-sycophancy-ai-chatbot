/** Shared API error and response wrapper types. */

export interface ApiErrorBody {
  detail?: string | { msg: string; type?: string; loc?: (string | number)[] }[];
  message?: string;
}

export interface HealthResponse {
  status: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

/** Generic API envelope — use when the backend wraps payloads. */
export interface ApiEnvelope<T> {
  data: T;
  meta?: Record<string, unknown>;
}
