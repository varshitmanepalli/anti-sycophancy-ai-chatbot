import { STORAGE_KEYS } from "@/config";

import type { AuthTokens } from "./types";

const memoryStore: { tokens: AuthTokens | null } = { tokens: null };

function isBrowser(): boolean {
  return typeof window !== "undefined";
}

/** Client-side auth token storage (localStorage with in-memory fallback). */
export const authTokenStore = {
  get(): AuthTokens | null {
    if (!isBrowser()) return memoryStore.tokens;

    try {
      const raw = localStorage.getItem(STORAGE_KEYS.auth);
      if (!raw) return null;
      return JSON.parse(raw) as AuthTokens;
    } catch {
      return null;
    }
  },

  set(tokens: AuthTokens): void {
    if (!isBrowser()) {
      memoryStore.tokens = tokens;
      return;
    }
    localStorage.setItem(STORAGE_KEYS.auth, JSON.stringify(tokens));
  },

  getAccessToken(): string | null {
    return this.get()?.accessToken ?? null;
  },

  getRefreshToken(): string | null {
    return this.get()?.refreshToken ?? null;
  },

  updateAccessToken(accessToken: string, expiresAt?: number): void {
    const current = this.get();
    if (!current) {
      this.set({ accessToken, refreshToken: "" });
      return;
    }
    this.set({ ...current, accessToken, expiresAt });
  },

  clear(): void {
    memoryStore.tokens = null;
    if (!isBrowser()) return;
    localStorage.removeItem(STORAGE_KEYS.auth);
  },

  isExpired(bufferMs = 60_000): boolean {
    const tokens = this.get();
    if (!tokens?.expiresAt) return false;
    return Date.now() >= tokens.expiresAt - bufferMs;
  },
};
