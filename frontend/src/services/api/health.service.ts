import type { HealthResponse } from "@/types";

import { api } from "./client";

/** Liveness probe. */
export async function checkHealth(): Promise<HealthResponse> {
  return api.get<HealthResponse>("/health", { retry: { retries: 1 } });
}

/** Readiness probe. */
export async function checkReady(): Promise<HealthResponse> {
  return api.get<HealthResponse>("/ready", { retry: { retries: 1 } });
}
