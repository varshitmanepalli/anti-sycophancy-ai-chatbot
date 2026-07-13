import type { AxiosError, AxiosInstance } from "axios";

import { API_RETRY_ATTEMPTS, API_RETRY_DELAY_MS, API_RETRY_STATUS_CODES } from "@/config";

import type { ApiInternalConfig, RetryOptions } from "./types";

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function backoffDelay(attempt: number, baseMs: number): number {
  const jitter = Math.random() * 200;
  return baseMs * 2 ** attempt + jitter;
}

function resolveRetryOptions(config: ApiInternalConfig): Required<RetryOptions> {
  const overrides = config.retry === false ? { retries: 0 } : (config.retry ?? {});
  return {
    retries: overrides.retries ?? API_RETRY_ATTEMPTS,
    retryDelayMs: overrides.retryDelayMs ?? API_RETRY_DELAY_MS,
    retryOn: overrides.retryOn ?? [...API_RETRY_STATUS_CODES],
  };
}

function shouldRetry(error: AxiosError, config: ApiInternalConfig): boolean {
  const { retries, retryOn } = resolveRetryOptions(config);
  const attempt = config._retryCount ?? 0;

  if (attempt >= retries) return false;
  if (error.code === "ERR_CANCELED") return false;

  const status = error.response?.status;
  if (status && retryOn.includes(status)) return true;

  return !error.response && error.code !== "ECONNABORTED";
}

/** Retry a failed request with exponential backoff. */
export async function retryRequest(
  client: AxiosInstance,
  error: AxiosError,
): Promise<unknown> {
  const config = error.config as ApiInternalConfig | undefined;
  if (!config || !shouldRetry(error, config)) {
    throw error;
  }

  const { retryDelayMs } = resolveRetryOptions(config);
  const attempt = (config._retryCount ?? 0) + 1;
  config._retryCount = attempt;

  await sleep(backoffDelay(attempt - 1, retryDelayMs));
  return client.request(config);
}

/** Returns true when the error is eligible for automatic retry. */
export function isRetryableAxiosError(error: AxiosError): boolean {
  const config = error.config as ApiInternalConfig | undefined;
  if (!config) return false;
  return shouldRetry(error, config);
}
