# Backend — Anti-Sycophancy Reasoning API

FastAPI service that powers chat, SSE streaming, the multi-stage reasoning pipeline, analysis agents, memory APIs, and offline SFT/evaluation tooling.

Deep design notes: [ARCHITECTURE.md](ARCHITECTURE.md) · Full-stack ops: [../README.md](../README.md)

---

## Contents

1. [Prerequisites](#prerequisites)
2. [Local setup](#local-setup)
3. [Database & migrations](#database--migrations)
4. [Running the API](#running-the-api)
5. [Docker](#docker)
6. [Staging & production](#staging--production)
7. [Configuration](#configuration)
8. [Testing & quality](#testing--quality)
9. [Training CLI](#training-cli)
10. [Package layout](#package-layout)

---

## Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.12+ |
| PostgreSQL | 16 (Docker `db` service recommended) |
| Docker | Optional but recommended for Postgres / deploy images |
| NVIDIA GPU | Optional; required only for local vLLM container |

---

## Local setup

### 1. Create a virtual environment

```bash
cd backend
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install -e ".[dev]"
```

### 2. Configure environment

Copy the repo root template and ensure the database URL points at your Postgres:

```bash
cp ../.env.example ../.env
```

Relevant defaults:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/chatbot
LLM_BACKEND=vllm
MODEL_NAME=Qwen/Qwen3-14B
VLLM_BASE_URL=http://localhost:8001/v1
CORS_ORIGINS=["http://localhost:3000"]
LOG_FORMAT=text
DEBUG=true
```

### 3. Start PostgreSQL

From the **repository root**:

```bash
docker compose up -d db
```

Wait until the container is healthy, then migrate (next section).

---

## Database & migrations

Migrations live in `alembic/`. `alembic/env.py` reads `DATABASE_URL` from `app.config.settings`.

```bash
cd backend

# Apply schema
alembic upgrade head

# Inspect
alembic current
alembic history

# After ORM changes
alembic revision --autogenerate -m "describe_change"

# Roll back one step
alembic downgrade -1
```

Inside Compose:

```bash
# Dev stack
docker compose exec api alembic upgrade head

# Staging / production stack
docker compose -f docker-compose.prod.yml exec api alembic upgrade head
```

### Schema overview (`001_memory_schema`)

| Table | Role |
|-------|------|
| `conversations` | Conversation metadata |
| `messages` | Per-conversation messages |
| `user_facts` / `user_opinions` / `user_goals` | Long-term memory |
| `contradictions` | Contradiction records |

Connection URL forms:

| Context | Host in `DATABASE_URL` |
|---------|-------------------------|
| API on host | `localhost` |
| API in Compose network | `db` |

Example:

```text
postgresql+asyncpg://postgres:postgres@localhost:5432/chatbot
postgresql+asyncpg://postgres:postgres@db:5432/chatbot
```

### Backup / restore

```bash
docker compose exec -T db pg_dump -U postgres chatbot > backup.sql
docker compose exec -T db psql -U postgres chatbot < backup.sql
```

---

## Running the API

```bash
cd backend

# Linux / macOS
PYTHONPATH=src uvicorn app.main:app --reload --app-dir src --host 0.0.0.0 --port 8000

# Windows PowerShell
$env:PYTHONPATH="src"
uvicorn app.main:app --reload --app-dir src --host 0.0.0.0 --port 8000
```

| URL | Purpose |
|-----|---------|
| http://localhost:8000/api/docs | OpenAPI UI |
| http://localhost:8000/api/health | Liveness |
| http://localhost:8000/api/ready | Readiness (includes dependency checks) |

Default API prefix: `/api` (`Settings.api_prefix`).

---

## Docker

### Development image (from root Compose)

```bash
docker compose up --build api
# or with DB + frontend
docker compose up --build db api frontend
```

`docker-compose.yml` mounts `./backend/src` into the container for live code reload with uvicorn when configured for reload, and sets:

- `DATABASE_URL=…@db:5432/chatbot`
- `VLLM_BASE_URL=http://vllm:8001/v1` (only useful if `vllm` is running)

### Production / staging image

Built by `docker-compose.prod.yml` from `backend/Dockerfile`:

- Python 3.12-slim
- Installs `requirements.txt`
- Copies `src/`, `alembic/`, `alembic.ini`
- Runs `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- Exposed only on the Docker network; nginx publishes HTTP

Manual build:

```bash
docker build -t youruser/anti-sycophancy-api:0.1.0 ./backend
```

---

## Staging & production

Use the root Compose production file (documented in [../README.md](../README.md)):

```bash
# From repository root
cp .env.example .env   # set POSTGRES_PASSWORD and CORS_ORIGINS

docker compose -f docker-compose.prod.yml --env-file .env up --build -d
docker compose -f docker-compose.prod.yml exec api alembic upgrade head
```

API container behavior in that file:

| Setting | Value |
|---------|-------|
| `DEBUG` | `false` |
| `LOG_FORMAT` | `json` |
| Ports | `expose: 8000` (not published to host) |
| Healthcheck | HTTP GET `http://127.0.0.1:8000/health` |
| Depends on | healthy `db` |

Point `VLLM_BASE_URL` at a reachable OpenAI-compatible inference service. The prod Compose file does not start vLLM itself.

### Staging vs production (backend)

| | Staging | Production |
|--|---------|------------|
| Secrets | Staging DB password | Vault / managed secret |
| CORS | Staging web origin | Production origin(s) |
| Model endpoint | Shared / cheaper model OK | Production SLA endpoint |
| Data | Non-prod | Backed up |

---

## Configuration

Settings: `src/app/config/settings.py` (env + `.env`). Training: `TRAINING_*` prefix in `config/training.py`.

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | Async SQLAlchemy URL |
| `MODEL_NAME` | Hugging Face / served model id |
| `MODEL_BACKEND` | `auto` \| `vllm_server` \| `vllm_local` \| `transformers` |
| `LLM_BACKEND` | Legacy alias (`vllm` / `transformers`) |
| `VLLM_BASE_URL` | OpenAI-compatible base ending in `/v1` |
| `AUTH_ENABLED` | Placeholder; `false` → anonymous user |
| `CORS_ORIGINS` | JSON list of allowed origins |
| `LOG_FORMAT` | `text` or `json` |
| `CLASSIFIER_MODE` | `rules` \| `llm` \| `hybrid` |

---

## Testing & quality

```bash
cd backend
PYTHONPATH=src python -m pytest tests/ -q
ruff check src/
mypy src/app
```

Tests mock LLMs (`AsyncMock`); GPU is not required for CI.

---

## Training CLI

```bash
cd backend
PYTHONPATH=src python scripts/generate_sft_dataset.py \
  --input data/sample_conversations.json \
  --output-dir data/sft

PYTHONPATH=src python scripts/export_sft_from_db.py \
  --database-url postgresql+asyncpg://postgres:postgres@localhost:5432/chatbot \
  --output-dir data/sft

PYTHONPATH=src python scripts/run_eval.py \
  --benchmark data/benchmarks/anti_sycophancy_benchmark.json \
  --output-dir data/eval_reports
```

---

## Package layout

```
backend/
├── src/app/
│   ├── api/           # HTTP routers, deps.py composition root
│   ├── services/      # Chat, pipeline, agents, memory, health
│   ├── domain/        # Dataclasses & ports
│   ├── models/        # ModelManager + adapters
│   ├── database/      # ORM + repositories
│   ├── prompts/       # PromptManager, prompts.yml
│   ├── memory/        # Context / stores
│   ├── training/      # Offline SFT + eval
│   ├── schemas/       # API DTOs
│   ├── config/
│   ├── logging/
│   └── core/
├── alembic/
├── scripts/
├── tests/
├── Dockerfile
└── pyproject.toml
```

Import root is `src/` (`from app.main import …`). See [ARCHITECTURE.md](ARCHITECTURE.md) for layer diagrams, full route catalog, and known gaps.
