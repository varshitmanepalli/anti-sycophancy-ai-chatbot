import type { AxiosError } from "axios";

import type { ApiErrorBody } from "@/types";

export type ApiErrorCode =
  | "NETWORK"
  | "TIMEOUT"
  | "ABORTED"
  | "UNAUTHORIZED"
  | "FORBIDDEN"
  | "NOT_FOUND"
  | "VALIDATION"
  | "SERVER"
  | "UNKNOWN";

/** Structured API error with status, code, and optional field details. */
export class ApiRequestError extends Error {
  readonly status?: number;
  readonly code: ApiErrorCode;
  readonly details?: unknown;
  readonly isRetryable: boolean;

  constructor(
    message: string,
    options: {
      status?: number;
      code?: ApiErrorCode;
      details?: unknown;
      isRetryable?: boolean;
    } = {},
  ) {
    super(message);
    this.name = "ApiRequestError";
    this.status = options.status;
    this.code = options.code ?? inferCode(options.status);
    this.details = options.details;
    this.isRetryable = options.isRetryable ?? isRetryableStatus(options.status);
  }
}

function inferCode(status?: number): ApiErrorCode {
  if (!status) return "NETWORK";
  if (status === 401) return "UNAUTHORIZED";
  if (status === 403) return "FORBIDDEN";
  if (status === 404) return "NOT_FOUND";
  if (status === 422 || status === 400) return "VALIDATION";
  if (status >= 500) return "SERVER";
  return "UNKNOWN";
}

function isRetryableStatus(status?: number): boolean {
  if (!status) return true;
  return status >= 500 || status === 429 || status === 408;
}

/** Extract a human-readable message from an Axios error body. */
export function parseApiErrorMessage(error: AxiosError<ApiErrorBody>): string {
  const detail = error.response?.data?.detail;

  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail.length > 0) {
    return detail.map((item) => item.msg).join(", ");
  }
  if (error.response?.data?.message) return error.response.data.message;
  if (error.code === "ECONNABORTED") return "Request timed out";
  if (error.code === "ERR_CANCELED") return "Request was cancelled";
  return error.message || "An unexpected error occurred";
}

/** Convert any thrown value into an ApiRequestError. */
export function toApiRequestError(error: unknown): ApiRequestError {
  if (error instanceof ApiRequestError) return error;

  if (isAxiosError(error)) {
    const status = error.response?.status;
    return new ApiRequestError(parseApiErrorMessage(error), {
      status,
      details: error.response?.data,
      isRetryable: isRetryableStatus(status),
    });
  }

  if (error instanceof DOMException && error.name === "AbortError") {
    return new ApiRequestError("Request was cancelled", { code: "ABORTED" });
  }

  const message = error instanceof Error ? error.message : "An unexpected error occurred";
  return new ApiRequestError(message);
}

function isAxiosError(error: unknown): error is AxiosError<ApiErrorBody> {
  return (
    typeof error === "object" &&
    error !== null &&
    "isAxiosError" in error &&
    (error as AxiosError).isAxiosError === true
  );
}
