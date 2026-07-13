/** Application-wide constants (non-env). */

export const APP_NAME = "Reasoning Engine";
export const APP_DESCRIPTION =
  "The AI that tells you the truth — honest, critical reasoning over flattery.";

export const STORAGE_KEYS = {
  /** @deprecated Legacy combined chat store — migrated automatically. */
  chat: "reasoning-engine-chat",
  chatUi: "reasoning-engine-chat-ui",
  conversation: "reasoning-engine-conversations",
  theme: "reasoning-engine-theme",
  /** @deprecated Legacy combined user store — migrated automatically. */
  user: "reasoning-engine-user",
  settings: "reasoning-engine-settings",
  authSession: "reasoning-engine-auth-session",
  feedback: "reasoning-engine-feedback",
  auth: "reasoning-engine-auth",
  reasoningPanel: "reasoning-engine-reasoning-panel",
} as const;

export const ROUTES = {
  home: "/",
  chat: "/chat",
  conversation: (id: string) => `/c/${id}`,
  dashboard: {
    chat: "/chat",
    conversation: (id: string) => `/c/${id}`,
    profile: "/profile",
    settings: "/settings",
  },
  auth: {
    login: "/login",
    signup: "/signup",
    forgotPassword: "/forgot-password",
    resetPassword: "/reset-password",
    verifyOtp: "/verify-otp",
  },
} as const;

export const CHAT_MODES = ["standard", "reasoning"] as const;

export const API_TIMEOUT_MS = 120_000;

/** Default automatic retry settings for the API client. */
export const API_RETRY_ATTEMPTS = 2;
export const API_RETRY_DELAY_MS = 1_000;
export const API_RETRY_STATUS_CODES = [408, 429, 500, 502, 503, 504] as const;
