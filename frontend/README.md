# Frontend — Reasoning Engine Web Client

Next.js 15 (App Router) + React 19 client for streaming chat, structured reasoning, auth screens, and the dashboard shell.

Deep design notes: [ARCHITECTURE.md](ARCHITECTURE.md) · Full-stack ops: [../README.md](../README.md)

---

## Contents

1. [Prerequisites](#prerequisites)
2. [Local setup](#local-setup)
3. [Environment variables](#environment-variables)
4. [Scripts](#scripts)
5. [Talking to the API](#talking-to-the-api)
6. [Docker (development)](#docker-development)
7. [Staging & production](#staging--production)
8. [Project structure](#project-structure)
9. [Quality gates](#quality-gates)

---

## Prerequisites

| Tool | Version |
|------|---------|
| Node.js | 20+ |
| npm | Comes with Node (lockfile: `package-lock.json`) |
| Running backend | http://localhost:8000 (or Docker `api`) |

---

## Local setup

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Open http://localhost:3000.

Recommended `.env.local` for local API on port 8000:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_CLIENT_API_URL=/api
```

With `NEXT_PUBLIC_CLIENT_API_URL=/api`, the browser calls same-origin `/api/...` and Next.js rewrites to the backend (`next.config.ts`). That avoids CORS friction during development.

---

## Environment variables

### Local — `frontend/.env.example` → `.env.local`

| Variable | Role |
|----------|------|
| `NEXT_PUBLIC_API_URL` | Absolute API URL (docs / fallback) |
| `NEXT_PUBLIC_CLIENT_API_URL` | Browser base path (`/api` recommended) |
| `API_URL` | Server-only rewrite target (e.g. `http://api:8000/api` in Docker) |
| `USE_NEXT_REWRITES` | Force rewrites; Docker **dev** Compose sets `true` |
| `NEXT_PUBLIC_SITE_URL` | Canonical site URL for metadata |

### Production — `frontend/.env.production.example`

| Variable | When applied | Role |
|----------|--------------|------|
| `NEXT_PUBLIC_CLIENT_API_URL` | **Build time** | Usually `/api` behind nginx |
| `NEXT_PUBLIC_API_URL` | **Build time** | Public API URL if not relative |
| `NEXT_PUBLIC_SITE_URL` | **Build time** | Canonical origin |
| `API_URL` | Runtime | Internal `http://api:8000/api` |
| `USE_NEXT_REWRITES` | Runtime | `false` when nginx owns `/api` |

> Changing any `NEXT_PUBLIC_*` value requires rebuilding the frontend image / running `npm run build` again.

---

## Scripts

```bash
npm run dev          # next dev
npm run build        # production build (standalone output)
npm run start        # serve production build
npm run lint         # ESLint
npm run format       # Prettier write
npm run format:check
npm run typecheck    # tsc --noEmit
```

---

## Talking to the API

| Chat mode | Frontend path | Backend |
|-----------|---------------|---------|
| Standard (streaming) | `useSendMessage` → SSE client | `POST /api/v1/chat/stream` |
| Reasoning | `useSendMessage` → JSON | `POST /api/chat` |

Conversation history is persisted in the browser via Zustand `persist` (localStorage). Backend auth is still a placeholder; auth UI stores tokens client-side for future wiring.

Health for operators / Docker:

- Frontend: `GET /health`
- Backend (proxied): `GET /api/health`

---

## Docker (development)

From the **repository root**:

```bash
docker compose up --build frontend
# typically with api + db:
docker compose up --build db api frontend
```

Dev image: `Dockerfile.dev`. Compose sets:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_CLIENT_API_URL=/api
USE_NEXT_REWRITES=true
```

Source mount: `./frontend/src` → `/app/src` for hot reload.

---

## Staging & production

Production and staging use the **same** root file `docker-compose.prod.yml`:

| Service | Role |
|---------|------|
| `frontend` | Multi-stage `Dockerfile` → Next.js **standalone** on `:3000` (internal) |
| `nginx` | Public HTTP; proxies `/` → frontend, `/api/` → api |
| `api` / `db` | Backend stack |

### Build args (important)

Compose passes build args into the frontend image:

- `NEXT_PUBLIC_CLIENT_API_URL`
- `NEXT_PUBLIC_API_URL`
- `NEXT_PUBLIC_SITE_URL`

Example staging values in root `.env`:

```env
NEXT_PUBLIC_CLIENT_API_URL=/api
NEXT_PUBLIC_API_URL=https://staging.example.com/api
NEXT_PUBLIC_SITE_URL=https://staging.example.com
NGINX_SERVER_NAME=staging.example.com
CORS_ORIGINS=["https://staging.example.com"]
```

Production example:

```env
NEXT_PUBLIC_CLIENT_API_URL=/api
NEXT_PUBLIC_API_URL=https://app.example.com/api
NEXT_PUBLIC_SITE_URL=https://app.example.com
NGINX_SERVER_NAME=app.example.com
CORS_ORIGINS=["https://app.example.com"]
```

Bring-up (from repo root):

```bash
docker compose -f docker-compose.prod.yml --env-file .env up --build -d
```

Runtime inside the frontend container:

```env
API_URL=http://api:8000/api
USE_NEXT_REWRITES=false
NODE_ENV=production
```

### Nginx behavior

Defined under `nginx/` and `Dockerfile.nginx`:

| Path | Behavior |
|------|----------|
| `/api/` | Proxy to FastAPI; buffering off (SSE) |
| `/_next/static/` | Long-cache immutable assets |
| `/` | Next.js; HTML not cached |
| `/health` | Frontend health probe |

Manual image build:

```bash
docker build -t youruser/anti-sycophancy-frontend:0.1.0 \
  --build-arg NEXT_PUBLIC_CLIENT_API_URL=/api \
  --build-arg NEXT_PUBLIC_API_URL=https://app.example.com/api \
  --build-arg NEXT_PUBLIC_SITE_URL=https://app.example.com \
  ./frontend
```

Create the Docker Hub repository first; then `docker login` and `docker push`. The tag must exist locally before push.

### TLS

Compose publishes HTTP on port 80. Terminate TLS with Cloudflare, a host reverse proxy, or an ingress in front of nginx. Set `NEXT_PUBLIC_SITE_URL` to the HTTPS origin.

---

## Project structure

```
frontend/
├── src/
│   ├── app/                 # Routes only
│   ├── features/            # chat, auth, dashboard, landing, …
│   ├── components/          # ui, layout, feedback, motion
│   ├── services/api/        # Domain API functions
│   ├── lib/api/             # Axios, SSE, tokens, retry
│   ├── stores/              # Zustand
│   ├── hooks/
│   ├── providers/           # Theme + React Query
│   ├── config/
│   ├── types/
│   ├── utils/
│   └── styles/
├── nginx/
├── Dockerfile
├── Dockerfile.dev
├── Dockerfile.nginx
├── .env.example
└── .env.production.example
```

Import rule: features export via `index.ts`; shared layers never import features. Full dependency graph: [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Quality gates

```bash
npm run typecheck
npm run lint
npm run build
```

CI should fail the pipeline if any of these fail. Recommended future tests (Vitest / Playwright) are outlined in ARCHITECTURE.md.
