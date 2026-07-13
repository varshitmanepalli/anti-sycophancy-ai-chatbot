/**
 * Typed environment variables.
 * Single source of truth — never read process.env directly outside this file.
 */

function optionalBool(value: string | undefined, defaultValue = false): boolean {
  if (value === undefined) return defaultValue;
  return value === "true" || value === "1";
}

export const env = {
  /** Client-facing API base — use `/api` in production (nginx proxy). */
  clientApiUrl:
    process.env.NEXT_PUBLIC_CLIENT_API_URL ??
    process.env.NEXT_PUBLIC_API_URL ??
    "/api",

  /** Direct backend URL for server-side calls and dev rewrites. */
  apiUrl:
    process.env.API_URL ??
    process.env.NEXT_PUBLIC_API_URL ??
    "http://localhost:8000/api",

  /** Public site URL for metadata and absolute links. */
  siteUrl: process.env.NEXT_PUBLIC_SITE_URL ?? "",

  /** Enable analytics integrations when wired up. */
  enableAnalytics: optionalBool(process.env.NEXT_PUBLIC_ENABLE_ANALYTICS),

  nodeEnv: process.env.NODE_ENV ?? "development",
  isDev: process.env.NODE_ENV === "development",
  isProd: process.env.NODE_ENV === "production",
} as const;

export type Env = typeof env;
