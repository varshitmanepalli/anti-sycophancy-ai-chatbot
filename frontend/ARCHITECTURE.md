# Frontend Architecture

This document describes the architecture of the **Reasoning Engine** web client — a Next.js 15 application built with React 19, TypeScript, Tailwind CSS, shadcn/ui, Zustand, TanStack Query, and Framer Motion. The frontend provides streaming chat, structured reasoning visualization, conversation history, authentication screens, and a responsive dashboard shell optimized for both desktop and mobile.

The guiding goal is **maintainability at SaaS scale**: new features should be added as self-contained vertical slices without polluting shared layers, and all backend communication should flow through a typed, retry-aware API layer.

---

## Design principles

**Feature-first vertical slices.** Domain logic, components, hooks, and validators for a capability (chat, auth, dashboard, etc.) live together under `src/features/<name>/`. The App Router in `src/app/` only declares routes and composes feature exports — it does not contain business rules, API calls, or form validation.

**Thin routing layer.** Every page file should be readable in a few lines: import a layout or feature entry component, pass route params, done. Loading states, error boundaries, and not-found pages delegate to shared primitives in `components/feedback/`.

**Unidirectional dependencies.** Features may import from shared layers (`components/`, `hooks/`, `stores/`, `services/`, `config/`, `utils/`, `types/`). Shared layers must never import from `features/` or `app/`. This prevents circular coupling and keeps shared code truly reusable.

**Colocation until proven shared.** If a hook or component is used by only one feature, it stays inside that feature. Promote to a shared folder only when a second consumer appears.

**Explicit public APIs.** Each feature exports through `index.ts`. Other parts of the app import `@/features/chat`, not `@/features/chat/components/chat-input`. This allows internal refactors without breaking consumers.

**No raw fetch in UI.** Components and hooks call `@/services` (domain API functions). Services sit on top of `@/lib/api` (Axios client, interceptors, SSE helpers). This two-tier split keeps transport concerns (auth headers, retry, error normalization, streaming) separate from endpoint-specific payloads.

---

## Dependency graph

The diagram below shows allowed import direction. Arrows point from dependent to dependency.

```
app/  ──────────────────►  features/  ──►  services/api/
  │                            │              │
  │                            ▼              ▼
  └──►  components/  ◄──  stores/       lib/api/
  │         │              hooks/
  │         ▼                │
  providers/                 ▼
  styles/                 config/
                            utils/
                            types/
```

The `lib/` folder is intentionally minimal: it holds third-party shims (`lib/utils.ts` re-exports `cn` for shadcn) and cross-cutting utilities such as `lib/motion.ts` (Framer Motion presets) and `lib/api/` (HTTP transport).

---

## Application structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router (routes only)
│   ├── features/               # Vertical feature modules
│   ├── components/             # Shared UI (ui, layout, feedback, motion)
│   ├── services/               # Domain API functions (no React)
│   ├── lib/                    # HTTP transport, motion presets, shims
│   ├── stores/                 # Zustand global client state
│   ├── hooks/                  # Cross-feature React hooks
│   ├── providers/              # Theme, React Query, app composition
│   ├── config/                 # env, constants, query keys
│   ├── types/                  # Shared TypeScript types
│   ├── styles/                 # globals.css, design tokens
│   └── utils/                  # Pure helpers (cn, format, id)
├── public/                     # Static assets (robots.txt, …)
├── nginx/                      # Production reverse proxy config
├── Dockerfile                  # Multi-stage standalone production image
├── Dockerfile.dev              # Development image with hot reload
├── Dockerfile.nginx            # Nginx proxy image
├── next.config.ts              # Standalone output, images, caching headers
├── .env.example                # Local development variables
└── .env.production.example     # Production build/runtime variables
```

---

## App Router (`src/app/`)

The App Router defines URL structure, root metadata, and route-level loading/error boundaries. Business logic never lives here.

**Root layout** (`app/layout.tsx`) loads Geist fonts, global CSS, and wraps the tree in `<AppProviders>` (theme + TanStack Query).

**Public routes:**

| Route | Page | Feature source |
|-------|------|----------------|
| `/` | Landing / marketing | `features/landing` |
| `/login`, `/signup` | Authentication | `features/auth` |
| `/forgot-password`, `/reset-password`, `/verify-otp` | Password / OTP flows | `features/auth` |

**Dashboard route group** (`app/(dashboard)/`):

The `(dashboard)` group applies `DashboardShell` via `layout.tsx` — sidebar, header, mobile bottom nav, offline banner, and page transitions. All routes inside share this chrome.

| Route | Purpose |
|-------|---------|
| `/chat` | New chat session |
| `/c/[id]` | Conversation by ID |
| `/profile` | User profile editor |
| `/settings` | App preferences (theme, chat mode, notifications) |

**Infrastructure routes:**

| Route | Purpose |
|-------|---------|
| `/health` | JSON health check for Docker and load balancers |
| `loading.tsx`, `error.tsx`, `not-found.tsx` | Root and `(dashboard)/` boundaries using `components/feedback/` |

Pages import feature components and pass route parameters. For example, `c/[id]/page.tsx` renders `<ChatWindow conversationId={id} />` from `@/features/chat`.

---

## Feature modules (`src/features/`)

Each feature is a mini-application with its own components, hooks, validators, and barrel export.

### `features/chat`

The core product experience: message list, input composer, streaming indicators, reasoning panel, mode toggle (standard vs reasoning), and message actions (copy, edit, delete, regenerate, retry).

Key pieces:

- **`ChatWindow`** — orchestrates conversation resolution, empty state, message list, reasoning panel, and input
- **`useSendMessage`** — central hook for send, stream, regenerate, retry, abort, reconnect; coordinates `useConversationStore`, `useStreamingStore`, and `useReasoningPanelStore`
- **`stream-chat.service.ts`** — SSE with exponential backoff, offline detection, abort, non-streaming fallback
- **`components/lazy/`** — code-split `LazyMarkdownRenderer` and `LazyReasoningPanel` to reduce initial bundle size

### `features/conversation-history`

Sidebar conversation list with search, pin, rename, delete, date grouping, and infinite scroll via `IntersectionObserver`.

### `features/dashboard`

Application shell: `DashboardShell`, `DashboardHeader`, `DashboardSidebar`, `MobileBottomNav`, profile and settings views. Reads auth profile from `useAuthStore` and health status via TanStack Query.

### `features/auth`

Login, signup, forgot password, reset password, and OTP verification forms with Zod validation. Auth layout with branding and theme toggle. Backend endpoints are placeholders; UI and client token storage are production-shaped.

### `features/feedback` (message feedback)

Thumbs up/down and report-issue flow on assistant messages. Uses `useFeedbackStore` for local persistence and `feedback.service.ts` for optional server sync (graceful fallback if route missing).

### `features/markdown`

Shared markdown renderer: GFM, KaTeX math, syntax highlighting (highlight.js), Mermaid diagrams (dynamic import), and copy-code buttons. Used by chat message bubbles via lazy-loaded chunk.

### `features/landing`

Marketing homepage sections with animated content for unauthenticated visitors.

**Import rule:** Always use barrel exports:

```typescript
import { ChatWindow, ModeToggle } from "@/features/chat";
import { DashboardShell } from "@/features/dashboard";
```

---

## Shared components (`src/components/`)

### `components/ui/`

shadcn/ui primitives: Button, Input, Textarea, Card, Sheet, Avatar, Badge, Skeleton, ScrollArea, Tooltip, DropdownMenu, etc. These are domain-agnostic — no API calls, no feature-specific copy.

`OptimizedImage` wraps `next/image` with lazy loading, responsive `sizes`, and AVIF/WebP formats configured in `next.config.ts`.

### `components/layout/`

Cross-feature shell elements: Logo, SidebarToggle, ThemeToggle.

### `components/feedback/`

**Application UX states** — not to be confused with `features/feedback` (message ratings).

| Component | Role |
|-----------|------|
| `ShimmerSkeleton`, `SkeletonText`, page skeletons | Loading placeholders with shimmer animation |
| `EmptyStateView`, `ErrorStateView`, `ErrorPage` | Empty, inline error, and full-page error (404, offline) |
| `RetryButton`, `LoadingSpinner`, `OfflineBanner` | Retry actions, spinners, network status |
| `AsyncState` | Wrapper switching between loading / error / empty / content |

Route-level `loading.tsx` and `error.tsx` files compose these primitives.

### `components/motion/`

Framer Motion wrappers for consistent animation: `PageTransition`, `StaggerList`, `MotionButton`, `MotionCard`, `AnimatedSheet`, `Collapse`, `SidebarNavItem`. Animation tokens live in `lib/motion.ts` with reduced-motion respect via `useReducedMotion`.

---

## API layer

### Transport tier (`src/lib/api/`)

| Module | Responsibility |
|--------|----------------|
| `create-client.ts` | Axios instance factory with base URL and timeout |
| `client.ts` | Shared `apiClient`, typed `api.get/post/…` helpers |
| `interceptors.ts` | Auth header injection, 401 refresh queue, error normalization, retry |
| `auth-token-store.ts` | In-memory access/refresh token storage (non-React) |
| `refresh-token.ts` | Token refresh handler (`POST /v1/auth/refresh` placeholder) |
| `retry.ts` | Exponential backoff for retryable HTTP status codes |
| `errors.ts` | `ApiRequestError` with `isRetryable` flag |
| `streaming.ts` | `openSseStream`, `readSseStream`, `StreamError` with offline detection |

All Axios requests go through interceptors. SSE streaming uses `fetch` with auth headers because Axios does not natively support SSE consumption in the browser.

### Domain tier (`src/services/api/`)

| Service | Endpoints |
|---------|-----------|
| `chat.service.ts` | `POST /v1/chat/`, `POST /chat` (pipeline), streaming helpers |
| `stream-chat.service.ts` | Retry-aware SSE wrapper with phase callbacks |
| `health.service.ts` | `GET /health`, `GET /ready` |
| `auth.service.ts` | Login/logout placeholders |
| `feedback.service.ts` | `POST /v1/feedback/` with local fallback |

React Query hooks in features call these services. Query keys are centralized in `config/query-keys.ts`.

**Environment wiring** (`config/env.ts`):

- `clientApiUrl` — browser-facing base (`/api` in production so nginx same-origin proxy works)
- `apiUrl` — server-side / direct backend URL
- `siteUrl`, `enableAnalytics` — metadata and optional integrations

Never read `process.env` outside `config/env.ts`.

---

## Client state (Zustand)

Global state is split by concern so each store stays small and persist boundaries are clear.

| Store | File | Responsibility | Persisted |
|-------|------|----------------|-----------|
| `useAuthStore` | `auth-store.ts` | User session, profile, login/logout; syncs with `authTokenStore` | Yes (`authSession`) |
| `useSettingsStore` | `settings-store.ts` | Stream responses, confidence badges, email notifications | Yes (`settings`) |
| `useThemeStore` | `theme-store.ts` | light / dark / system; synced via `ThemeStoreSync` + next-themes | Mirrored from next-themes |
| `useConversationStore` | `conversation-store.ts` | Conversations, messages, structured reasoning, CRUD | Yes (`conversation`); migrates legacy `chat` key |
| `useChatStore` | `chat-store.ts` | UI only: `chatMode`, sidebar open | Partial (`chatMode` only) |
| `useReasoningPanelStore` | `reasoning-panel-store.ts` | Panel expanded per conversation, steps, last confidence | Yes (expand state) |
| `useStreamingStore` | `streaming-store.ts` | Active stream handle, stream phase mutations on messages | No (ephemeral) |
| `useFeedbackStore` | `feedback-store.ts` | Per-message helpful/unhelpful/report | Yes |

`useUserStore` in `user-store.ts` is a **deprecated facade** combining auth profile and settings for backward compatibility during migration. New code should use `useAuthStore` and `useSettingsStore` directly.

Shared store types (`AuthUser`, `UserProfile`, `UserSettings`, `ThemePreference`) live in `stores/types.ts`.

---

## Streaming architecture

Standard chat mode follows this sequence:

1. User submits message → `useSendMessage.mutation` appends user message to `useConversationStore`
2. Assistant placeholder message created with `isStreaming: true`, `streamPhase: 'connecting'`
3. `streamChatWithRetry` opens SSE to `POST /api/v1/chat/stream` with shared `AbortController` (cancel works across hook instances)
4. On each token: `updateMessage` appends content; `useStreamingStore` updates phase
5. On complete: streaming flags cleared; structured reasoning cleared (standard mode)
6. On error: `setMessageError` with formatted message; `StreamStatusBar` and inline retry in message bubble
7. On abort: `setMessageAborted`; user can regenerate
8. On reconnect: `window.online` listener triggers retry when phase was error

Reasoning mode bypasses SSE and calls `POST /api/chat` for a complete JSON payload including `structured_reasoning`, then updates conversation and reasoning panel stores.

---

## Providers and configuration

**`providers/app-providers.tsx`** composes:

- `ThemeProvider` — next-themes with class strategy; includes `ThemeStoreSync` to mirror preference into Zustand
- `QueryProvider` — TanStack Query with default `retry: 1` for queries

**`config/constants.ts`** holds app name, route map, localStorage keys, chat modes, and API retry defaults.

**`config/query-keys.ts`** factory for health, conversations, and future server-backed queries.

---

## Production build and deployment

### Next.js configuration (`next.config.ts`)

Production optimizations enabled:

- **`output: 'standalone'`** — minimal Node server artifact for Docker
- **`compress: true`**, **`poweredByHeader: false`**
- **`removeConsole`** in production (except `warn` / `error`)
- **`optimizePackageImports`** for lucide-react, Radix, framer-motion
- **Image formats** AVIF + WebP with remote patterns for avatars
- **Cache-Control headers** on `/_next/static` and public assets
- **Rewrites** — enabled for local/dev (`USE_NEXT_REWRITES` / non-prod); disabled by default behind nginx in production

### Environment matrix

| Environment | Entry | `/api` routing | Image |
|-------------|-------|----------------|-------|
| Local `npm run dev` | `:3000` | Next rewrite → `localhost:8000` | Host Node |
| Local Compose (`Dockerfile.dev`) | `:3000` | Next rewrite (`USE_NEXT_REWRITES=true`) | Dev image + src mount |
| Staging | nginx `:80` | nginx → `api:8000` | Standalone prod image |
| Production | nginx (+ TLS) | nginx → `api:8000` | Standalone prod image |

`NEXT_PUBLIC_*` values are **build-time**. Staging and production must rebuild when site URL or public API base changes.

### Docker

| File | Purpose |
|------|---------|
| `Dockerfile` | Multi-stage: deps → build → non-root standalone runner with health check |
| `Dockerfile.dev` | Development with volume-friendly layout |
| `Dockerfile.nginx` | Nginx 1.27 alpine with gzip and proxy cache zone |

Build args pass `NEXT_PUBLIC_*` variables at image build time. Runtime `API_URL` stays internal to the container network (`http://api:8000/api`).

### Nginx (`nginx/`)

Production/staging traffic enters nginx on port 80:

- **`/api/`** → FastAPI (no buffering for SSE, long read timeouts)
- **`/_next/static/`** → immutable 1-year cache
- **`/_next/image`** → 7-day cache for optimized images
- **`/`** → Next.js standalone (HTML not cached)
- **`/health`** → frontend health for Compose / load balancers

Security headers (X-Frame-Options, X-Content-Type-Options, Referrer-Policy) are set at the nginx layer.

### Staging vs production (frontend)

| | Staging | Production |
|--|---------|------------|
| Compose file | `docker-compose.prod.yml` | same |
| `NEXT_PUBLIC_SITE_URL` | `https://staging.example.com` | `https://app.example.com` |
| TLS | Optional terminator in front of `:80` | Required |
| Analytics | Usually off | Per product policy |

Commands (repository root):

```bash
docker compose -f docker-compose.prod.yml --env-file .env up --build -d
```

Operator runbooks: [../README.md](../README.md), [README.md](README.md).

---

## Code splitting and performance

Heavy dependencies are loaded on demand:

- **`LazyMarkdownRenderer`** — react-markdown, KaTeX, highlight.js (via dynamic import in `features/chat/components/lazy/`)
- **`LazyReasoningPanel`** — reasoning UI only when viewing a conversation in reasoning mode
- **Mermaid** — dynamic `import('mermaid')` inside `MarkdownMermaid` when a diagram block renders

`optimizePackageImports` tree-shakes icon and Radix packages at build time. Chat route First Load JS is kept moderate by splitting markdown and reasoning chunks.

---

## Hooks (`src/hooks/`)

Cross-feature hooks with no domain coupling:

| Hook | Purpose |
|------|---------|
| `useMounted` | Hydration-safe rendering (theme toggle, settings) |
| `useMediaQuery` / `useIsMobile` | Responsive breakpoints (767px mobile) |
| `useOnlineStatus` | Browser online/offline for banner and stream recovery |
| `useSwipeEdge` | Edge swipe to open/close mobile sidebar |
| `useVisualViewportBottomInset` | Keyboard-aware padding on mobile chat input |

Feature-specific hooks remain in `features/*/hooks/`.

---

## Styling

**`styles/globals.css`** imports design tokens and Tailwind layers. **`styles/tokens.css`** defines CSS custom properties for light/dark themes consumed by shadcn variables.

Component styling uses Tailwind utility classes. Markdown content uses `features/markdown/styles/markdown.css` and `@tailwindcss/typography` prose classes.

Mobile utilities include safe-area padding (`pb-safe`, `pt-safe`), bottom nav offset (`pb-bottom-nav`), and touch-friendly button sizes (`iconTouch`).

---

## Testing strategy (recommended)

| Layer | Approach |
|-------|----------|
| `utils/`, validators | Unit tests (Vitest) |
| `services/api/` | Integration tests with MSW |
| `features/*/hooks/` | React Testing Library + MSW |
| `components/ui/` | Storybook or RTL snapshots |
| `app/` | E2E (Playwright) |

Current CI gate: `npm run typecheck`, `npm run lint`, `npm run build`.

---

## Related documentation

| Document | Contents |
|----------|----------|
| [Root README.md](../README.md) | Full local / staging / production + database runbook |
| [Frontend README.md](README.md) | Frontend setup, env matrix, Docker Hub notes |
| [Root ARCHITECTURE.md](../ARCHITECTURE.md) | Full-stack overview, environments, structure map |
| [Backend ARCHITECTURE.md](../backend/ARCHITECTURE.md) | API routes, pipeline, LLM adapters, DB schema |
| [Backend README.md](../backend/README.md) | Backend migrations and API bring-up |
