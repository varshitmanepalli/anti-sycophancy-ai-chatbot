import { ROUTES } from "@/config";

import { authTokenStore } from "./auth-token-store";
import type { RefreshTokenResponse } from "./types";

type RefreshHandler = () => Promise<string | null>;

let refreshHandler: RefreshHandler = defaultRefreshHandler;

let isRefreshing = false;
let refreshQueue: Array<(token: string | null) => void> = [];

function flushRefreshQueue(token: string | null) {
  refreshQueue.forEach((callback) => callback(token));
  refreshQueue = [];
}

/**
 * Placeholder refresh implementation — replace the endpoint URL and response
 * mapping when your auth backend is ready.
 */
async function defaultRefreshHandler(): Promise<string | null> {
  const refreshToken = authTokenStore.getRefreshToken();
  if (!refreshToken) return null;

  const baseUrl =
    process.env.NEXT_PUBLIC_CLIENT_API_URL ??
    process.env.NEXT_PUBLIC_API_URL ??
    "/api";

  try {
    const response = await fetch(`${baseUrl}/v1/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) return null;

    const data = (await response.json()) as RefreshTokenResponse;
    const expiresAt = data.expires_in
      ? Date.now() + data.expires_in * 1000
      : undefined;

    authTokenStore.set({
      accessToken: data.access_token,
      refreshToken: data.refresh_token ?? refreshToken,
      expiresAt,
    });

    return data.access_token;
  } catch {
    return null;
  }
}

/** Override the refresh handler (e.g. in tests or when wiring real auth). */
export function setRefreshHandler(handler: RefreshHandler): void {
  refreshHandler = handler;
}

/** Reset to the default placeholder handler. */
export function resetRefreshHandler(): void {
  refreshHandler = defaultRefreshHandler;
}

/**
 * Refresh the access token, deduplicating concurrent calls.
 * Returns the new access token or null if refresh failed.
 */
export async function refreshAccessToken(): Promise<string | null> {
  if (isRefreshing) {
    return new Promise((resolve) => {
      refreshQueue.push(resolve);
    });
  }

  isRefreshing = true;

  try {
    const token = await refreshHandler();
    flushRefreshQueue(token);

    if (!token) {
      authTokenStore.clear();
      redirectToLogin();
    }

    return token;
  } catch {
    flushRefreshQueue(null);
    authTokenStore.clear();
    redirectToLogin();
    return null;
  } finally {
    isRefreshing = false;
  }
}

function redirectToLogin(): void {
  if (typeof window === "undefined") return;
  const path = window.location.pathname;
  if (path.startsWith("/login") || path.startsWith("/signup")) return;
  window.location.href = ROUTES.auth.login;
}
