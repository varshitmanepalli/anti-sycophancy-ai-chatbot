# Anti-Sycophancy AI Chatbot

A production-ready reasoning engine that uses open-source Hugging Face models to deliver honest, critical responses instead of sycophantic agreement. The backend exposes a multi-stage reasoning pipeline, specialized analysis agents, and tooling for SFT dataset generation and benchmark evaluation. The frontend is a Next.js chat and dashboard client with streaming, structured reasoning UI, and local conversation persistence.

| Document | Purpose |
|----------|---------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Full-stack structure, request flows, environments |
| [backend/README.md](backend/README.md) | Backend-only setup, migrations, API, tests |
| [backend/ARCHITECTURE.md](backend/ARCHITECTURE.md) | Backend layers, DI, LLM adapters, schema |
| [frontend/README.md](frontend/README.md) | Frontend-only setup, env vars, builds |
| [frontend/ARCHITECTURE.md](frontend/ARCHITECTURE.md) | Feature modules, stores, streaming, nginx |

---

## Table of contents

1. [Tech stack](#tech-stack)
2. [Features](#features)
3. [Repository structure](#repository-structure)
4. [Prerequisites](#prerequisites)
5. [Local setup (detailed)](#local-setup-detailed)
6. [Database setup (detailed)](#database-setup-detailed)
7. [LLM / inference options](#llm--inference-options)
8. [Staging deployment](#staging-deployment)
9. [Production deployment](#production-deployment)
10. [Environment variables reference](#environment-variables-reference)
11. [Verification checklist](#verification-checklist)
12. [Training & evaluation](#training--evaluation)
13. [Development & quality gates](#development--quality-gates)
14. [API overview](#api-overview)
15. [Troubleshooting](#troubleshooting)
16. [License](#license)

---

## Tech stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.12, FastAPI, SQLAlchemy (async), Alembic, Pydantic Settings |
| Inference | vLLM (OpenAI-compatible server), Transformers (dev/CPU fallback) |
| Database | PostgreSQL 16 |
| Frontend | Next.js 15, React 19, TypeScript, Tailwind CSS, shadcn/ui |
| State | Zustand, TanStack Query |
| Infra | Docker, Docker Compose, Nginx (production) |

---

## Features

### Reasoning pipeline

The chat pipeline (`POST /api/chat`) runs staged analysis before response generation:

1. Input classification  
2. Claim extraction  
3. Assumption detection  
4. Logical fallacy detection  
5. Prompt construction  
6. LLM inference  
7. Confidence scoring  
8. Reasoning extraction  

### Analysis agents

| Module | Endpoint | Purpose |
|--------|----------|---------|
| Classification | `POST /api/v1/classify` | Categorize user input |
| Claims | `POST /api/v1/claims/extract` | Extract factual claims |
| Assumptions | `POST /api/v1/assumptions/detect` | Surface hidden assumptions |
| Fallacies | `POST /api/v1/fallacies/detect` | Detect logical fallacies |
| Debate | `POST /api/v1/debate/run` | Support → Opponent → Fact Checker → Judge |
| Confidence | `POST /api/v1/confidence/score` | Score evidence, reasoning, and uncertainty |
| Memory | `POST /api/v1/memory/extract`, `/store` | Extract and persist long-term user facts |
| Contradictions | `POST /api/v1/contradictions/check`, `/check-and-store` | Detect memory contradictions |

### Chat modes (frontend)

| Mode | API endpoint | Behavior |
|------|-------------|----------|
| **Chat** | `POST /api/v1/chat/stream` | Streaming SSE with anti-sycophancy persona |
| **Reasoning** | `POST /api/chat` | Full pipeline with confidence and reasoning panel |

---

## Repository structure

```
anti-sycophancy-ai-chatbot/
├── backend/                     # FastAPI API + training/eval CLI
│   ├── src/app/                 # Application package (import root: src/)
│   ├── alembic/                 # Database migrations
│   ├── scripts/                 # SFT generation, eval, DB export
│   ├── tests/                   # Unit & integration tests
│   ├── data/                    # Sample conversations, benchmarks, reports
│   ├── Dockerfile
│   ├── ARCHITECTURE.md
│   └── README.md
├── frontend/                    # Next.js 15 App Router client
│   ├── src/app/                 # Routes only
│   ├── src/features/            # Vertical feature modules
│   ├── nginx/                   # Production reverse proxy templates
│   ├── Dockerfile               # Production standalone image
│   ├── Dockerfile.dev           # Dev image with hot reload
│   ├── Dockerfile.nginx
│   ├── ARCHITECTURE.md
│   └── README.md
├── docker-compose.yml           # Local / development stack
├── docker-compose.prod.yml      # Staging & production stack (nginx)
├── .env.example                 # Root env template (API + infra)
├── ARCHITECTURE.md              # Full-stack architecture
└── README.md                    # This file
```

For layer-by-layer design (dependency rules, request flows, known gaps), see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Prerequisites

### Required for all local workflows

| Tool | Version | Notes |
|------|---------|-------|
| Git | any recent | Clone the repository |
| Docker Desktop / Docker Engine | 24+ | Includes Compose v2 (`docker compose`) |
| Docker Compose | v2 | Bundled with Docker Desktop |

### Required for hybrid local development (API/frontend outside Docker)

| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.12+ | Backend virtualenv |
| Node.js | 20+ | Frontend (`npm` / `package-lock.json`) |
| PostgreSQL | 16 | Or use Compose `db` service only |

### Optional (GPU inference)

| Tool | Notes |
|------|-------|
| NVIDIA GPU + drivers | Required for the Compose `vllm` service |
| NVIDIA Container Toolkit | Required for Docker GPU passthrough |
| WSL2 + GPU adapters | On Windows: `nvidia-smi` must work in Windows **and** WSL |

> **Important:** Without a GPU, do **not** start the `vllm` service. The stack still runs with `db` + `api` + `frontend`; configure an external OpenAI-compatible endpoint or `transformers` / CPU fallback for inference. See [LLM / inference options](#llm--inference-options).

---

## Local setup (detailed)

There are three supported local workflows. Pick one.

| Workflow | When to use | Command summary |
|----------|-------------|-----------------|
| **A. Full Docker (dev)** | Fastest path; mirrors team env | `docker compose up --build db api frontend` |
| **B. Hybrid** | Day-to-day coding with hot reload | Compose `db` (+ optional vLLM); run API + frontend on host |
| **C. Full host** | No Docker for app code; DB still recommended in Docker | Postgres + `uvicorn` + `npm run dev` |

---

### Workflow A — Full Docker development stack

#### 1. Clone and enter the repo

```bash
git clone <your-fork-or-remote-url>
cd anti-sycophancy-ai-chatbot
```

#### 2. Create environment files

```bash
cp .env.example .env
cp frontend/.env.example frontend/.env.local
```

Edit `.env` if you change Postgres credentials, model name, or CORS. For Compose on the Docker network, the **api** service already injects `DATABASE_URL` pointing at host `db` (see `docker-compose.yml`); your root `.env` is still used when running tools on the host.

#### 3. Start services (recommended without vLLM if no GPU)

```bash
docker compose up --build db api frontend
```

| Service | Container role | Host URL |
|---------|----------------|----------|
| `db` | PostgreSQL 16 | `localhost:5432` |
| `api` | FastAPI (source mount `./backend/src`) | http://localhost:8000 |
| `frontend` | Next.js via `Dockerfile.dev` | http://localhost:3000 |

With GPU and NVIDIA Container Toolkit working:

```bash
docker compose up --build
# or explicitly:
docker compose up --build db vllm api frontend
```

| Extra service | Host URL |
|---------------|----------|
| `vllm` | http://localhost:8001/v1 |

#### 4. Apply database migrations

The API image includes Alembic. After `db` is healthy:

```bash
docker compose exec api alembic upgrade head
```

Or from the host (with venv and `DATABASE_URL` pointing at `localhost`):

```bash
cd backend
alembic upgrade head
```

#### 5. Open the apps

| Surface | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API OpenAPI docs | http://localhost:8000/api/docs |
| Health | http://localhost:8000/api/health |
| Ready | http://localhost:8000/api/ready |

In this mode the frontend sets `USE_NEXT_REWRITES=true` so the browser calls `/api`, and Next.js rewrites proxy to the API. Nginx is **not** used in development Compose.

#### 6. Stop / reset

```bash
docker compose down          # stop containers, keep volume
docker compose down -v       # stop and DELETE Postgres data volume (destructive)
```

---

### Workflow B — Hybrid (Compose database + host processes)

Best for editing Python and TypeScript with native IDE tooling.

#### 1. Start only PostgreSQL

```bash
docker compose up -d db
```

Wait until healthy:

```bash
docker compose ps
# db should show healthy
```

#### 2. Backend on the host

```bash
cd backend
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

pip install -e ".[dev]"
```

Ensure root or `backend` env has:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/chatbot
```

Migrate and run:

```bash
alembic upgrade head

# Linux / macOS
PYTHONPATH=src uvicorn app.main:app --reload --app-dir src --host 0.0.0.0 --port 8000

# Windows (PowerShell)
$env:PYTHONPATH="src"
uvicorn app.main:app --reload --app-dir src --host 0.0.0.0 --port 8000
```

#### 3. Frontend on the host

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Defaults in `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_CLIENT_API_URL=/api
```

Open http://localhost:3000. The Next.js rewrite proxies `/api/*` to `http://localhost:8000/api/*`.

---

### Workflow C — Full host (optional)

1. Install PostgreSQL 16 locally.  
2. Create role/database (see [Database setup](#database-setup-detailed)).  
3. Follow backend and frontend steps from Workflow B.  

Use this only if you cannot run Docker for the database.

---

## Database setup (detailed)

### What PostgreSQL is used for

| Concern | Status |
|---------|--------|
| Connection / pool | Configured via `DATABASE_URL` (async SQLAlchemy + asyncpg) |
| Schema | Alembic migrations under `backend/alembic/` |
| Memory APIs | Repositories for facts, opinions, goals, contradictions |
| Conversations / messages tables | Created by migration `001_memory_schema` |
| Live chat persistence | Frontend uses Zustand `localStorage`; backend chat still has an in-memory path — Postgres wiring for live chat is ongoing (see ARCHITECTURE known gaps) |

### Default development credentials

| Setting | Value |
|---------|-------|
| User | `postgres` |
| Password | `postgres` |
| Database | `chatbot` |
| Host (Docker service) | `db` |
| Host (from your machine) | `localhost` |
| Port | `5432` |
| App URL | `postgresql+asyncpg://postgres:postgres@localhost:5432/chatbot` |
| Inside Compose network | `postgresql+asyncpg://postgres:postgres@db:5432/chatbot` |

### Create database manually (host Postgres)

```sql
CREATE USER postgres WITH PASSWORD 'postgres';
CREATE DATABASE chatbot OWNER postgres;
```

Or with `psql`:

```bash
createdb -U postgres chatbot
```

### Run migrations

Always run from `backend/` so `alembic.ini` and `env.py` resolve correctly. `alembic/env.py` loads `DATABASE_URL` from application settings.

```bash
cd backend

# Apply all migrations
alembic upgrade head

# Show current revision
alembic current

# History
alembic history

# Create a new migration after ORM changes
alembic revision --autogenerate -m "describe_change"

# Roll back one revision
alembic downgrade -1
```

Inside the running API container:

```bash
docker compose exec api alembic upgrade head
```

### Tables created by `001_memory_schema`

Approximate schema (see migration file for full column set):

| Table | Purpose |
|-------|---------|
| `conversations` | Conversation metadata (`user_id`, title, timestamps) |
| `messages` | Message rows linked to conversations |
| `user_facts` | Long-term factual memory |
| `user_opinions` | Opinion memory |
| `user_goals` | Goal memory |
| `contradictions` | Detected memory contradictions |

### Backups (local / staging / production)

```bash
# Dump
docker compose exec -T db pg_dump -U postgres chatbot > backup_$(date +%Y%m%d).sql

# Restore (destructive to current DB content)
docker compose exec -T db psql -U postgres chatbot < backup_YYYYMMDD.sql
```

Production Compose uses the volume name defined in `docker-compose.prod.yml` (`pgdata`). Always back up before `docker compose down -v`.

### Connecting with GUI tools

Point GUI clients (DBeaver, pgAdmin, TablePlus) at:

- Host: `localhost`
- Port: `5432`
- Database: `chatbot`
- User / password: as in env  

When only prod Compose is up, Postgres is **not** published to the host by default (no `ports:` on `db` in `docker-compose.prod.yml`). Use `docker compose -f docker-compose.prod.yml exec db psql -U postgres -d chatbot` or temporarily add a port mapping for admin access.

---

## LLM / inference options

| Mode | Requirements | Configuration |
|------|--------------|---------------|
| **vLLM in Compose** | NVIDIA GPU + Container Toolkit | Start `vllm`; `VLLM_BASE_URL=http://vllm:8001/v1`, `LLM_BACKEND=vllm` |
| **External OpenAI-compatible API** | Reachable URL | Set `VLLM_BASE_URL` to that base (`…/v1`), leave Compose without `vllm` |
| **Transformers on host / API** | RAM/GPU or CPU | `LLM_BACKEND=transformers` / `MODEL_BACKEND=transformers`, `ALLOW_CPU_FALLBACK=true` |
| **No model yet** | — | API boots for docs/health; chat routes fail until a backend is reachable |

Default model id: `Qwen/Qwen3-14B` (large — prefer a smaller model or remote endpoint for laptops).

Example without local vLLM (external server):

```env
LLM_BACKEND=vllm
MODEL_BACKEND=vllm_server
VLLM_BASE_URL=https://your-inference-host/v1
MODEL_NAME=Qwen/Qwen3-14B
```

---

## Staging deployment

Staging should mirror production topology (nginx + standalone Next.js + API + Postgres) with non-production secrets, smaller models if needed, and a distinct hostname.

### Goals

- Same Compose file as production: `docker-compose.prod.yml`
- Separate `.env` / secrets from production
- Optional public URL such as `https://staging.example.com`
- JSON logs on the API (`LOG_FORMAT=json`)
- Migrations applied before traffic switch

### 1. Prepare secrets and env

On the staging host (or CI runner):

```bash
cp .env.example .env
cp frontend/.env.production.example frontend/.env.production
```

Minimum staging `.env` values:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<strong-staging-password>
POSTGRES_DB=chatbot

LLM_BACKEND=vllm
MODEL_NAME=Qwen/Qwen3-14B
VLLM_BASE_URL=http://vllm:8001/v1
# Or point at a shared staging inference cluster:
# VLLM_BASE_URL=https://llm-staging.internal/v1

CORS_ORIGINS=["https://staging.example.com"]

NEXT_PUBLIC_CLIENT_API_URL=/api
NEXT_PUBLIC_API_URL=https://staging.example.com/api
NEXT_PUBLIC_SITE_URL=https://staging.example.com

NGINX_HTTP_PORT=80
NGINX_SERVER_NAME=staging.example.com
```

> `POSTGRES_PASSWORD` is **required** by `docker-compose.prod.yml` (`${POSTGRES_PASSWORD:?…}`). Compose will refuse to start without it.

### 2. Build and start the staging stack

```bash
docker compose -f docker-compose.prod.yml --env-file .env up --build -d
```

Services:

| Service | Role | Exposure |
|---------|------|----------|
| `db` | PostgreSQL + volume `pgdata` | Internal only |
| `api` | FastAPI | Internal `:8000`, health on `/health` |
| `frontend` | Next.js standalone | Internal `:3000` |
| `nginx` | Reverse proxy | Host `${NGINX_HTTP_PORT:-80}:80` |

Note: production Compose does **not** include the `vllm` service. Attach an external LLM or add a vLLM service/profile for staging GPU hosts.

### 3. Run migrations on staging

```bash
docker compose -f docker-compose.prod.yml exec api alembic upgrade head
```

### 4. TLS / reverse proxy in front of nginx (recommended)

`docker-compose.prod.yml` exposes HTTP on port 80. For HTTPS staging:

- Put Cloudflare, Traefik, Caddy, or host nginx/TLS in front of port 80, **or**
- Extend Compose with a certbot/Caddy sidecar (not shipped by default).

Set `NEXT_PUBLIC_SITE_URL` and `CORS_ORIGINS` to the HTTPS origin.

### 5. Staging smoke tests

```bash
curl -fsS http://localhost/health
curl -fsS http://localhost/api/health
curl -fsS http://localhost/api/ready
```

Open `https://staging.example.com` (or `http://localhost` if testing locally with the prod compose file).

### 6. Staging update process

```bash
git pull
docker compose -f docker-compose.prod.yml --env-file .env up --build -d
docker compose -f docker-compose.prod.yml exec api alembic upgrade head
docker compose -f docker-compose.prod.yml logs -f --tail=200
```

### Staging vs production differences (recommended policy)

| Concern | Staging | Production |
|---------|---------|------------|
| `POSTGRES_PASSWORD` | Strong, unique | Strong, unique, vault-managed |
| `DEBUG` | Often `false` (prod compose sets API `DEBUG=false`) | Always `false` |
| `CORS_ORIGINS` | Staging origin only | Production origin(s) only |
| Model size | Smaller / shared cluster | Full production model |
| Data | Synthetic / anonymized | Real; backup schedule |
| Auth | Still placeholder (`AUTH_ENABLED=false`) | Same until JWT/OAuth lands — lock network |

---

## Production deployment

### Architecture (production Compose)

```
Internet
   │
   ▼
┌─────────────┐     /api/*      ┌──────────────┐
│   nginx:80  │ ───────────────►│  api:8000    │──► PostgreSQL
│             │                 │  (FastAPI)   │──► LLM (VLLM_BASE_URL)
│             │     /*          └──────────────┘
│             │ ───────────────►┌──────────────┐
└─────────────┘                 │ frontend:3000│
                                │ (Next.js)    │
                                └──────────────┘
```

Nginx (`frontend/Dockerfile.nginx` + `frontend/nginx/`):

- `/api/` → FastAPI (buffering off for SSE, long timeouts)
- `/_next/static/` → long-lived immutable cache
- `/` → Next.js standalone (HTML not cached)

Frontend build args bake `NEXT_PUBLIC_*` into the client bundle. Runtime `API_URL=http://api:8000/api` stays on the Docker network; `USE_NEXT_REWRITES=false` so nginx owns `/api`.

### 1. Harden configuration

Production `.env` checklist:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<vault-managed-secret>
POSTGRES_DB=chatbot

DATABASE_URL=postgresql+asyncpg://postgres:<secret>@db:5432/chatbot
# (Compose builds DATABASE_URL for the api service automatically)

LLM_BACKEND=vllm
MODEL_NAME=Qwen/Qwen3-14B
VLLM_BASE_URL=https://llm.internal/v1

CORS_ORIGINS=["https://app.example.com"]
AUTH_ENABLED=false
API_KEY=<rotate-if-enabling-auth>

NEXT_PUBLIC_CLIENT_API_URL=/api
NEXT_PUBLIC_API_URL=https://app.example.com/api
NEXT_PUBLIC_SITE_URL=https://app.example.com

NGINX_HTTP_PORT=80
NGINX_SERVER_NAME=app.example.com
```

Never commit real `.env` files. Use a secrets manager or CI variables.

### 2. Deploy

```bash
docker compose -f docker-compose.prod.yml --env-file .env up --build -d
docker compose -f docker-compose.prod.yml exec api alembic upgrade head
```

### 3. Health and readiness

| Check | Command / URL |
|-------|----------------|
| Nginx / frontend health | `GET /health` (Next.js route via nginx) |
| API liveness | `GET /api/health` |
| API readiness | `GET /api/ready` |
| Compose status | `docker compose -f docker-compose.prod.yml ps` |

Compose healthchecks already probe API, frontend, and nginx.

### 4. Rolling update

```bash
docker compose -f docker-compose.prod.yml --env-file .env pull   # if using registry images
docker compose -f docker-compose.prod.yml --env-file .env up --build -d
docker compose -f docker-compose.prod.yml exec api alembic upgrade head
```

Prefer migrate **before** or immediately after new API containers start; avoid long periods where new code expects new columns that are missing.

### 5. Publishing images to Docker Hub / a registry (optional)

Compose builds from Dockerfiles by default. To push:

```bash
# Build with correct repository names (fix typos like "aycophancy")
docker build -t <dockerhub-user>/anti-sycophancy-api:0.1.0 ./backend
docker build -t <dockerhub-user>/anti-sycophancy-frontend:0.1.0 \
  --build-arg NEXT_PUBLIC_CLIENT_API_URL=/api \
  --build-arg NEXT_PUBLIC_API_URL=https://app.example.com/api \
  --build-arg NEXT_PUBLIC_SITE_URL=https://app.example.com \
  ./frontend

docker login
docker push <dockerhub-user>/anti-sycophancy-api:0.1.0
docker push <dockerhub-user>/anti-sycophancy-frontend:0.1.0
```

Create empty repositories on Docker Hub first; `docker push` only uploads images that already exist **locally** under that name:tag.

### 6. Production operations

| Task | Approach |
|------|----------|
| Logs | `docker compose -f docker-compose.prod.yml logs -f api nginx` |
| DB shell | `docker compose -f docker-compose.prod.yml exec db psql -U postgres -d chatbot` |
| Backup | `pg_dump` on a schedule; store off-box |
| Restore | Stop writers → restore dump → `alembic upgrade head` if needed |
| Scale | Single-node Compose is the shipped path; for multi-node use Swarm/K8s with shared DB and sticky sessions for SSE if needed |

---

## Environment variables reference

### Root / backend (see `.env.example`)

| Variable | Typical local | Purpose |
|----------|---------------|---------|
| `APP_NAME` | Anti-Sycophancy Chatbot | Service display name |
| `DEBUG` | `true` local / `false` prod | Verbose behavior |
| `DATABASE_URL` | asyncpg URL | SQLAlchemy async DB |
| `LLM_BACKEND` | `vllm` | Legacy alias for backend choice |
| `MODEL_NAME` | `Qwen/Qwen3-14B` | HF model id |
| `MODEL_BACKEND` | `auto` | `auto`, `vllm_server`, `vllm_local`, `transformers` |
| `VLLM_BASE_URL` | `http://localhost:8001/v1` | OpenAI-compatible base |
| `ALLOW_CPU_FALLBACK` | `true` | Permit CPU when no GPU |
| `AUTH_ENABLED` | `false` | Auth placeholder |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed browser origins |
| `LOG_LEVEL` / `LOG_FORMAT` | `INFO` / `text` or `json` | Logging |
| `POSTGRES_PASSWORD` | required in prod Compose | DB password |

### Frontend local (see `frontend/.env.example` → `.env.local`)

| Variable | Purpose |
|----------|---------|
| `NEXT_PUBLIC_API_URL` | Documented/direct API URL |
| `NEXT_PUBLIC_CLIENT_API_URL` | Browser base (`/api` with rewrites) |
| `API_URL` | Server-only backend URL (Docker) |
| `USE_NEXT_REWRITES` | `true` in dev Compose; `false` behind nginx |

### Frontend production (see `frontend/.env.production.example`)

| Variable | Purpose |
|----------|---------|
| `NEXT_PUBLIC_SITE_URL` | Canonical public URL |
| `NEXT_PUBLIC_*` | Inlined at **build** time — rebuild image when these change |
| `API_URL` | Internal `http://api:8000/api` |
| `USE_NEXT_REWRITES` | `false` when nginx terminates `/api` |

Training tooling uses the `TRAINING_` prefix (`backend/src/app/config/training.py`).

---

## Verification checklist

After any local, staging, or production bring-up:

- [ ] `GET /api/health` returns OK  
- [ ] `GET /api/ready` returns OK (DB reachable)  
- [ ] `alembic current` shows `001_memory_schema` (or later head)  
- [ ] Frontend loads at the expected URL  
- [ ] Browser network tab: chat calls go to `/api/...` (or configured base)  
- [ ] Standard chat: SSE stream receives tokens (requires working LLM)  
- [ ] Reasoning mode: JSON response + reasoning panel (requires working LLM)  
- [ ] Staging/prod: nginx `/health` and `/api/health` both succeed  

---

## Training & evaluation

All commands run from `backend/` with `PYTHONPATH=src`.

### Generate SFT dataset from conversations

```bash
# Linux / macOS
PYTHONPATH=src python scripts/generate_sft_dataset.py \
  --input data/sample_conversations.json \
  --output-dir data/sft

# Windows (PowerShell)
$env:PYTHONPATH="src"
python scripts/generate_sft_dataset.py `
  --input data/sample_conversations.json `
  --output-dir data/sft
```

Output: `train.jsonl`, `val.jsonl`, `dataset_info.json` (Alpaca format for QLoRA/TRL).

### Export conversations from PostgreSQL

```bash
PYTHONPATH=src python scripts/export_sft_from_db.py \
  --database-url postgresql+asyncpg://postgres:postgres@localhost:5432/chatbot \
  --output-dir data/sft
```

### Run benchmark evaluation

```bash
PYTHONPATH=src python scripts/run_eval.py \
  --benchmark data/benchmarks/anti_sycophancy_benchmark.json \
  --output-dir data/eval_reports
```

Output: `report.json`, `report.md`, `report.html`.

---

## Development & quality gates

### Backend

```bash
cd backend
PYTHONPATH=src python -m pytest tests/ -q
ruff check src/
mypy src/app
```

### Frontend

```bash
cd frontend
npm run typecheck
npm run lint
npm run build
```

---

## API overview

Base URL: `http://localhost:8000/api` (dev) or `https://<host>/api` (prod via nginx).

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness |
| GET | `/ready` | Readiness |
| POST | `/chat` | Full reasoning pipeline |
| POST | `/v1/chat/` | Non-streaming chat |
| POST | `/v1/chat/stream` | Streaming chat (SSE) |
| POST | `/v1/classify` | Classification |
| POST | `/v1/claims/extract` | Claims |
| POST | `/v1/assumptions/detect` | Assumptions |
| POST | `/v1/fallacies/detect` | Fallacies |
| POST | `/v1/debate/run` | Debate |
| POST | `/v1/confidence/score` | Confidence |
| POST | `/v1/memory/extract` | Memory extract |
| POST | `/v1/memory/store` | Memory store |
| POST | `/v1/contradictions/check` | Contradictions |
| POST | `/v1/contradictions/check-and-store` | Check + store |

Interactive docs: http://localhost:8000/api/docs

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `unknown docker command: "compose db"` | Missing `up` subcommand | Use `docker compose up …` |
| vLLM: `no adapters were found` / nvidia-container-cli | No GPU in Docker/WSL | Skip `vllm`; use external URL or transformers |
| `tag does not exist` on `docker push` | Image not built/tagged locally | `docker build -t user/repo:tag …` then push |
| Frontend Offline / API proxy `ECONNREFUSED` | API not reachable from Next rewrite target | Ensure API listens on `8000`; in Compose, rewrites may need `API_URL=http://api:8000/api` |
| Alembic cannot connect | Wrong `DATABASE_URL` host | Use `localhost` from host, `db` from containers |
| Prod Compose fails on start | Missing `POSTGRES_PASSWORD` | Set in `.env` and pass `--env-file .env` |
| SSE stalls behind proxy | Buffering enabled | Use shipped nginx template (`proxy_buffering off`) |

---

## License

MIT
