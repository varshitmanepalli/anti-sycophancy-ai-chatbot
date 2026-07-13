import { authTokenStore } from "@/lib/api";
import type { AuthTokens } from "@/lib/api";

import { api } from "./client";

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  expires_in?: number;
  token_type?: string;
}

/** Authenticate and persist tokens — wire when backend auth is ready. */
export async function login(payload: LoginRequest): Promise<AuthTokens> {
  const data = await api.post<LoginResponse, LoginRequest>("/v1/auth/login", payload, {
    skipAuth: true,
    skipRefresh: true,
  });

  const tokens: AuthTokens = {
    accessToken: data.access_token,
    refreshToken: data.refresh_token,
    expiresAt: data.expires_in ? Date.now() + data.expires_in * 1000 : undefined,
  };

  authTokenStore.set(tokens);
  return tokens;
}

/** Clear stored tokens (client-side logout). */
export function logout(): void {
  authTokenStore.clear();
}

/** Returns true when an access token is present. */
export function isAuthenticated(): boolean {
  return Boolean(authTokenStore.getAccessToken());
}
