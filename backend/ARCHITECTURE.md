# Backend Architecture

This document describes the architecture of the **Reasoning Engine** backend — a Python 3.12 **FastAPI** application that exposes chat, streaming, a multi-stage reasoning pipeline, specialized LLM analysis agents, long-term memory APIs, and offline training/evaluation tooling. The backend is designed around **clean architecture**: business rules live in the domain and service layers, HTTP and persistence are adapters, and LLM inference is swappable through a single `ModelManager` facade.

---

## Design principles

**Dependency rule.** Code in `domain/` never imports FastAPI, SQLAlchemy, Pydantic request models, or vLLM. Services orchestrate use cases and depend on domain types plus ports (protocols). The API layer translates HTTP to service calls and back to response schemas. This makes parsers and engines testable with mocked LLMs without standing up HTTP or GPU infrastructure.

**Ports and adapters.** `LLMProvider` in `domain/llm_interface.py` defines the inference port. `models/vllm_client.py`, `models/transformers_client.py`, and related adapters implement it. Memory persistence uses repository protocols in `domain/memory_interfaces.py` with SQLAlchemy implementations in `database/repositories/`.

**Single responsibility per package.** Parsers parse LLM JSON into domain objects. Engines orchestrate prompt render → generate → parse. Routers validate HTTP and call one service method. Prompt templates hold wording; `PromptManager` handles versioning and Jinja2 rendering.

**Configuration over code.** Model backend, database URL, classifier mode, token limits, CORS, auth flags, and log format are controlled by environment variables loaded through Pydantic `Settings` in `config/settings.py`. Training pipelines use a separate `TrainingSettings` with the `TRAINING_` env prefix.

**Dependency injection.** FastAPI `Depends()` in `api/deps.py` is the composition root for the HTTP layer: settings, database sessions, `ModelManager`, `PromptManager`, repositories, and every engine/service. Offline CLI scripts (`backend/scripts/`) accept injectable settings and registries instead of reading globals.

**Composition over inheritance.** `ChatPipeline`, `DebateEngine`, and `EvalPipeline` compose collaborators injected via constructors. They do not extend deep base classes.

---

## Layer diagram

```
┌──────────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                     │
│   api/router.py  api/deps.py  api/v1/*.py  api/chat.py     │
└──────────────────────────┬───────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────┐
│                    Service Layer                             │
│  chat_service  chat_pipeline  debate  classification  claims   │
│  assumptions  fallacies  confidence  memory  contradictions  │
│              (+ parser.py per LLM-backed feature)            │
└──────┬──────────┬──────────┬──────────┬──────────┬──────────┘
       │          │          │          │          │
       ▼          ▼          ▼          ▼          ▼
┌──────────┐ ┌────────┐ ┌────────┐ ┌──────────┐ ┌──────────┐
│ Prompts  │ │ Memory │ │ Models │ │ Database │ │ Training │
│ (Jinja2) │ │ context│ │ (LLM)  │ │ (Postgres│ │ SFT/eval │
└──────────┘ └────────┘ └────────┘ └──────────┘ └──────────┘
       │          │          │          │          │
       └──────────┴──────────┴──────────┴──────────┘
                           │
┌──────────────────────────▼───────────────────────────────────┐
│                     Domain Layer                             │
│  entities  debate  fallacies  confidence  memory  claims  …   │
│       (dataclass business types & abstract ports)              │
└──────────────────────────────────────────────────────────────┘

Cross-cutting: config/  logging/  utils/  core/  schemas/
```

---

## Package layout

```
backend/
├── src/app/
│   ├── main.py                 # FastAPI app factory, CORS, router mount
│   ├── api/                    # HTTP routers and dependency injection
│   ├── services/               # Application use cases
│   ├── domain/                 # Business types and ports
│   ├── models/                 # LLM inference adapters
│   ├── prompts/                # Jinja2 templates and PromptManager
│   ├── memory/                 # In-memory and Postgres conversation stores
│   ├── database/               # SQLAlchemy ORM, sessions, repositories
│   ├── schemas/                # Pydantic API DTOs
│   ├── training/               # SFT and benchmark evaluation (offline)
│   ├── config/                 # Settings (app + training)
│   ├── logging/                # Structured logging setup
│   └── core/                   # Lifespan, exceptions, middleware, security
├── alembic/                    # Database migrations
├── scripts/                    # CLI: SFT generation, eval, DB export
├── tests/                      # 235+ unit and integration tests
├── data/                       # Sample benchmarks, SFT output, reports
├── Dockerfile
└── pyproject.toml
```

The Python path root for imports is `backend/src` (`PYTHONPATH=src` or installed package `app`).

---

## API layer

### Router composition

`main.py` mounts `api_router` at the configured prefix (default **`/api`**).

`api/router.py` aggregates:

1. **`api/chat.py`** — `POST /chat` reasoning pipeline (no `/v1` prefix)
2. **`api/v1/router.py`** — all versioned routes under `/v1`
3. **`api/v1/health.py`** — also mounted at top level for backward-compatible `/health` and `/ready`

### Complete HTTP catalog

| Method | Path | Handler | Purpose |
|--------|------|---------|---------|
| `POST` | `/api/chat` | `ChatPipeline` | Full reasoning pipeline (JSON response) |
| `GET` | `/api/health` | `HealthService` | Liveness |
| `GET` | `/api/ready` | `HealthService` | Readiness |
| `POST` | `/api/v1/chat/` | `ChatService` | Standard chat (non-streaming) |
| `POST` | `/api/v1/chat/stream` | `ChatService` | SSE token streaming |
| `POST` | `/api/v1/classify` | `InputClassifier` | Input category classification |
| `POST` | `/api/v1/claims/extract` | `ClaimExtractor` | Factual claim extraction |
| `POST` | `/api/v1/assumptions/detect` | `AssumptionDetector` | Hidden assumption detection |
| `POST` | `/api/v1/fallacies/detect` | `LogicalFallacyDetector` | Logical fallacy detection |
| `POST` | `/api/v1/debate/run` | `DebateEngine` | Four-stage debate |
| `POST` | `/api/v1/confidence/score` | `ConfidenceEngine` | Multi-dimension confidence |
| `POST` | `/api/v1/memory/extract` | `MemoryExtractor` | Extract memory items from text |
| `POST` | `/api/v1/memory/store` | `MemoryStore` | Persist memory items |
| `POST` | `/api/v1/contradictions/check` | `MemoryContradictionChecker` | Check contradictions |
| `POST` | `/api/v1/contradictions/check-and-store` | Combined check + store | |

Routers are **thin**: validate request body with Pydantic, call injected service, map domain result to response schema. No business logic in routers.

### Dependency injection (`api/deps.py`)

`deps.py` is the composition root for HTTP requests. Typical dependencies:

| Dependency | Provides |
|------------|----------|
| `SettingsDep` | Application settings singleton |
| `DbSession` | Async SQLAlchemy session |
| `ModelManagerDep` | Active LLM backend |
| `PromptManagerDep` | Template registry and renderer |
| `MemoryRepositoryDep` | PostgreSQL memory CRUD |
| `ChatServiceDep` | Standard chat + streaming |
| `ChatPipelineDep` | Reasoning pipeline orchestrator |
| `DebateEngineDep`, `ConfidenceEngineDep`, … | Per-feature engines |

Engines receive `ModelManager`, `Settings`, and `PromptManager` through constructors wired here.

### Security (`core/security.py`)

Authentication is a **placeholder**. When `AUTH_ENABLED=false` (default), `get_current_user` returns an anonymous user and all routes remain open. Optional API key validation exists for future hardening. The frontend already implements token storage and refresh hooks anticipating `POST /v1/auth/refresh` — not yet implemented here.

### Cross-cutting HTTP concerns

- **`core/lifespan.py`** — startup/shutdown hooks (optional model warmup)
- **`core/exceptions.py`** — `AppError` hierarchy mapped to HTTP responses
- **`core/middleware/`** — request logging; rate limit settings exist but enforcement is not fully wired

---

## Service layer

### Standard chat (`services/chat_service.py`)

`ChatService` handles conversational messaging for **standard mode**:

1. Append user message via `InMemoryStore` (deduplicated append for idempotent retries)
2. Build trimmed context through `ContextManager` (token budget)
3. Format messages with `ConversationPrompt` (`prompts/anti_sycophancy.py`)
4. Call `ModelManager.generate()` or `generate_stream()` for SSE
5. Append assistant reply to store

Streaming emits async generator tuples `(conversation_id, token, done)` consumed by `api/v1/chat.py`, which formats SSE JSON lines and sets `Cache-Control: no-cache` and `X-Accel-Buffering: no` for nginx compatibility.

### Reasoning pipeline (`services/chat_pipeline/`)

`ChatPipeline` orchestrates staged analysis for **reasoning mode**. A mutable `PipelineContext` dataclass flows through each stage; every stage reads prior results and writes its own fields.

**Stages (in order):**

| Stage | Service | Status |
|-------|---------|--------|
| `load_context` | Memory / DB | **Stub** — returns empty history; TODO wire PostgreSQL |
| `classify_input` | `InputClassifier` | Implemented |
| `extract_claims` | `ClaimExtractor` | Implemented |
| `detect_assumptions` | `AssumptionDetector` | Implemented |
| `detect_fallacies` | `LogicalFallacyDetector` | Implemented |
| `build_prompt` | `ConversationPrompt` + `prompts.yml` | Implemented |
| `run_inference` | `ModelManager` | Implemented (requires loaded model) |
| `score_confidence` | `ConfidenceEngine` | Implemented |
| `extract_reasoning` | Pipeline internal | Builds `StructuredReasoning` from prior stages |
| `build_response` | Pipeline internal | Returns `ChatPipelineResponse` |

Each stage logs at DEBUG with the conversation ID. Failures in individual analyzers are handled according to engine implementation (most engines return empty structured results rather than failing the whole pipeline).

The response includes `structured_reasoning` consumed by the frontend reasoning panel: facts, assumptions, evidence, unknowns, and a confidence score.

### Feature module pattern

Every LLM-backed analyzer follows the same structure so new agents can be added predictably:

```
domain/{feature}.py              → dataclass result types
services/{feature}/
    engine.py | detector.py | extractor.py   → orchestrates LLM call
    parser.py                                → JSON → domain object
prompts/templates/{type}/v{N}.j2             → versioned Jinja2 template
prompts/templates/{type}/manifest.yaml       → metadata & variables
schemas/{feature}.py                         → Pydantic API DTOs
api/v1/{feature}.py                          → thin HTTP endpoint
tests/test_{feature}_*.py                    → parser, engine, API tests
```

| Module | Engine class | API endpoint |
|--------|-------------|--------------|
| Classification | `InputClassifier` | `POST /v1/classify` |
| Claims | `ClaimExtractor` | `POST /v1/claims/extract` |
| Assumptions | `AssumptionDetector` | `POST /v1/assumptions/detect` |
| Fallacies | `LogicalFallacyDetector` | `POST /v1/fallacies/detect` |
| Debate | `DebateEngine` | `POST /v1/debate/run` |
| Confidence | `ConfidenceEngine` | `POST /v1/confidence/score` |
| Memory | `MemoryExtractor`, `MemoryStore` | `POST /v1/memory/extract`, `/store` |
| Contradictions | `ContradictionDetector`, `MemoryContradictionChecker` | `POST /v1/contradictions/check`, `/check-and-store` |

### Debate engine (`services/debate/`)

`DebateEngine.run()` executes four sequential LLM stages sharing one `ModelManager`:

1. **Support Agent** (template v2) — arguments supporting the claim; parsed to structured JSON
2. **Opponent Agent** (template v2) — weaknesses and counter-arguments; parsed to structured JSON
3. **Fact Checker** (template v1) — plain-text report (not yet structured JSON)
4. **Judge** (template v4) — verdict with facts, assumptions, evidence, unknowns, conclusion; parsed via `JudgeVerdictParser`

Each stage receives prior outputs as Jinja2 template variables. This pattern — versioned prompts, strict parsers, shared model — is the template for adding new multi-step agents.

### Health (`services/health_service.py`)

Liveness and readiness checks for orchestrators and Docker health probes. Mounted at both `/api/health` and `/api/v1/health` for compatibility.

---

## Domain layer (`domain/`)

Domain types are plain **`@dataclass`** objects with optional `to_dict()` helpers. No FastAPI or SQLAlchemy imports.

| Module | Key types |
|--------|-----------|
| `entities.py` | `Conversation`, `Message`, `MessageRole` |
| `classification.py` | `InputCategory`, classification results |
| `claims.py` | `ClaimExtractionResult`, extracted claims |
| `assumptions.py` | `AssumptionDetectionResult` |
| `fallacies.py` | `FallacyType`, `DetectedFallacy`, `FallacyDetectionResult` |
| `confidence.py` | `DimensionScore`, `ConfidenceResult` |
| `debate.py` | `DebateStage`, `JudgeVerdict`, `DebateResult` |
| `memory.py` | `UserFact`, `UserOpinion`, `UserGoal`, `MemoryContradiction` |
| `memory_extraction.py` | `ExtractedMemoryItem`, `MemoryExtractionResult` |
| `support_agent.py`, `opponent_agent.py` | Structured debate agent outputs |
| `llm_interface.py` | `LLMProvider` protocol |
| `memory_interfaces.py` | Repository ports for memory persistence |
| `interfaces.py` | Port re-exports |

Keeping domain pure allows training scripts and tests to import business types without pulling in the web stack.

---

## LLM inference layer (`models/`)

`ModelManager` is a singleton that owns the active backend selected at startup from settings.

| Backend | Module | When used |
|---------|--------|-----------|
| `vllm_server` | `vllm_client.py` | Production: OpenAI-compatible HTTP to vLLM |
| `vllm_local` | `vllm_local.py` | In-process vLLM engine |
| `transformers` | `transformers_client.py` | Local Hugging Face inference |
| `auto` | `factory.py` | Chooses based on env and availability |

`base.py` defines `GenerationConfig` (temperature, max tokens, stop sequences) shared across backends. Swapping backends is a configuration change (`MODEL_BACKEND`, `LLM_BACKEND`, `VLLM_BASE_URL`) — services always call `ModelManager.generate()` or `generate_stream()`.

---

## Prompts (`prompts/`)

Prompt engineering is first-class and **editable without code changes** via the central file **`prompts/prompts.yml`**.

| Section in `prompts.yml` | Purpose |
|--------------------------|---------|
| `defaults.global` | Shared variables (`assistant_name`, `tone`, `reasoning_protocol`, …) |
| `defaults.{type}` | Per-agent default variables |
| `active_versions` | Which template version each agent uses (change here to roll forward/back) |
| `templates.{type}.{version}.content` | Full Jinja2 prompt text |

`PromptManager` loads template content from `prompts.yml` first; legacy `templates/{type}/v{N}.j2` + `manifest.yaml` files remain as fallback if the YAML section is empty.

Supporting modules:

- **`config_loader.py`** — parses `prompts.yml`, exposes defaults, active versions, template content
- **`manager.py`** — renders templates with Jinja2; supports `reload()` for dev
- **`registry.py`** — indexes template metadata from YAML or disk manifests
- **`variables.py`** — merges YAML defaults with call-time overrides
- **`anti_sycophancy.py`** — `ConversationPrompt` assembles system + history + user message

To fix a bad prompt in production: edit `prompts/prompts.yml`, restart the API (or call `PromptManager.reload()` in dev). No Python redeploy required for wording changes.

---

## Memory and persistence

### In-memory chat (`memory/`)

| Module | Role |
|--------|------|
| `conversation.py` | `InMemoryStore` — dev/test chat history |
| `context_manager.py` | Token-budget trimming for context windows |
| `postgres_store.py` | PostgreSQL-backed store adapter |

Standard chat currently uses `InMemoryStore`. Production persistence requires wiring repositories into `ChatService` and implementing `ChatPipeline.load_context`.

### Database (`database/`)

| Layer | Files |
|-------|-------|
| Session | `session.py` — async SQLAlchemy engine and session factory |
| ORM | `models/conversation.py`, `models/memory.py` |
| Repositories | `conversation_repository.py`, `memory_repository.py`, `user_fact_repository.py`, `user_opinion_repository.py`, `user_goal_repository.py`, `contradiction_repository.py`, `mappers.py` |

Alembic migrations live in `backend/alembic/`. Initial migration `001_memory_schema.py` creates:

- `conversations`, `messages`
- `user_facts`, `user_opinions`, `user_goals`
- `contradictions`

**Local setup:** start Postgres (`docker compose up -d db`), set `DATABASE_URL`, run `alembic upgrade head` from `backend/`.

**Staging / production:** run the same alembic command inside the `api` container after Compose brings `db` to healthy. Do not rely on auto-create from ORM metadata in deployed environments — migrations are the source of truth.

Conversation ORM models exist; full chat history integration into `ChatService` / `ChatPipeline.load_context` is ongoing.

---

## Schemas (`schemas/`)

Pydantic models validate HTTP request bodies and serialize responses. Each feature has a matching schema file. Where applicable, schemas expose `from_domain()` classmethods to map dataclass results to API DTOs.

Schemas are intentionally separate from domain dataclasses (business rules) and ORM models (persistence shape) to avoid leaking storage or transport concerns into the domain.

---

## Training and evaluation (offline)

The `training/` package supports **offline** workflows invoked by CLI scripts in `backend/scripts/` — not mounted as HTTP routes.

### SFT dataset generation

| Component | Role |
|-----------|------|
| `sft/converter.py` | `ConversationToSFTConverter` — one Alpaca row per assistant turn |
| `sft/pipeline.py` | Load conversations, convert, train/val split, write JSONL |
| `sft/io.py` | JSON/JSONL I/O, QLoRA `dataset_info.json` |

Scripts: `generate_sft_dataset.py`, `export_sft_from_db.py`

### Benchmark evaluation

| Component | Role |
|-----------|------|
| `eval/metrics/` | Six heuristic metrics: agreement rate, hallucination rate, evidence usage, logical consistency, bias detection, calibration (ECE/Brier) |
| `eval/registry.py` | `MetricRegistry` — register custom metrics (e.g. LLM-as-judge) |
| `eval/runner.py` | Per-case scoring and aggregation |
| `eval/pipeline.py` | End-to-end: load benchmark → run → write reports |
| `eval/report_writer.py` | JSON, Markdown, HTML output |

Script: `run_eval.py`. Configuration via `config/training.py` (`TRAINING_` env prefix).

---

## Request flow diagrams

### Standard chat (non-streaming)

```
ChatRequest
  → ChatService.process_message()
      1. InMemoryStore.append(user message)
      2. ContextManager.build_context()
      3. ConversationPrompt.to_chat_format()
      4. ModelManager.generate()
      5. InMemoryStore.append(assistant reply)
  → ChatResponse
```

### Standard chat (SSE streaming)

```
ChatRequest
  → ChatService.stream_message()
      → async generator of tokens
  → api/v1/chat.py formats SSE:
      data: {"conversation_id","token","done"}\n\n
```

### Reasoning pipeline

```
ChatPipelineRequest
  → ChatPipeline.run()
      → PipelineContext through all stages
  → ChatPipelineResponse
      (response text + structured_reasoning + confidence)
```

### Debate

```
DebateRequest
  → DebateEngine.run()
      Support → Opponent → Fact Checker → Judge
  → DebateResponse
```

---

## Configuration and logging

**`config/settings.py`** — application settings: LLM, database, CORS, classifier mode, feature flags, auth placeholder, logging level/format.

**`config/training.py`** — training-only settings with `TRAINING_` prefix (SFT split ratios, output directories, calibration bins).

**`logging/setup.py`** — `configure_logging()` and `get_logger()`. Production uses JSON structured logs; development uses human-readable text. All services and pipelines log through this module.

Key environment variables (see root [`.env.example`](../.env.example)):

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_NAME` | `Qwen/Qwen3-14B` | Hugging Face model ID |
| `MODEL_BACKEND` / `LLM_BACKEND` | `auto` | Inference backend selection |
| `VLLM_BASE_URL` | `http://localhost:8001/v1` | vLLM OpenAI-compatible endpoint |
| `DATABASE_URL` | PostgreSQL async URL | Database connection |
| `CLASSIFIER_MODE` | `rules` | `rules`, `llm`, or `hybrid` |
| `LOG_FORMAT` | `json` | `json` or `text` |
| `AUTH_ENABLED` | `false` | Auth placeholder flag |

---

## Testing

Tests live in `backend/tests/` (235+ cases). Coverage includes:

- JSON parsers (deterministic fixture inputs)
- Engines with `AsyncMock` model managers
- API routes via FastAPI test client
- Chat pipeline stage integration
- SFT conversion and eval metric math

```bash
cd backend
PYTHONPATH=src python -m pytest tests/ -q
```

Tests favor deterministic LLM responses over live inference so CI does not require GPU.

---

## Docker and deployment

### Container image (`backend/Dockerfile`)

- Base: `python:3.12-slim`
- Installs build deps for asyncpg (`libpq-dev`, `build-essential`)
- `PIP` installs `requirements.txt`
- Copies `src/`, `alembic/`, `alembic.ini`
- `PYTHONPATH=/app/src`
- CMD: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

### Local / development (`docker-compose.yml`)

| Aspect | Behavior |
|--------|----------|
| Service name | `api` |
| Volume | `./backend/src` → `/app/src` (edit code on host) |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@db:5432/chatbot` |
| `VLLM_BASE_URL` | `http://vllm:8001/v1` (only if `vllm` service is up) |
| Host port | `8000:8000` |
| Depends on | healthy `db` |

Migrate after DB is ready:

```bash
docker compose exec api alembic upgrade head
```

### Staging and production (`docker-compose.prod.yml`)

| Aspect | Behavior |
|--------|----------|
| Publish | Internal `expose: 8000` only — nginx fronts `/api/` |
| `DEBUG` | `false` |
| `LOG_FORMAT` | `json` |
| `DATABASE_URL` | Built from `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` |
| Healthcheck | urllib GET `http://127.0.0.1:8000/health` |
| LLM | Via `VLLM_BASE_URL` env (no vLLM service in this Compose file) |

Deploy pattern (repository root):

```bash
docker compose -f docker-compose.prod.yml --env-file .env up --build -d
docker compose -f docker-compose.prod.yml exec api alembic upgrade head
```

**Staging** uses the same Compose file with different secrets, `CORS_ORIGINS`, and public URLs. **Production** uses vault-managed `POSTGRES_PASSWORD`, HTTPS in front of nginx, and scheduled `pg_dump` backups.

### Database deployment concerns

| Topic | Detail |
|-------|--------|
| Engine | PostgreSQL 16 (`postgres:16-alpine` in Compose) |
| Migrations | Alembic; `env.py` loads URL from Settings |
| Initial revision | `001_memory_schema` — conversations, messages, memory tables |
| Chat path today | Live chat still leans on in-memory store; repositories exist for memory APIs |
| Backups | `pg_dump` against `db` service or managed Postgres |

Operational runbooks (local hybrid, staging TLS, registry push): [../README.md](../README.md) and [README.md](README.md).

---

## Known gaps

1. **`ChatPipeline.load_context`** — does not load conversation history from PostgreSQL.
2. **`ChatPipeline.run_inference` / `build_prompt`** — stubbed; full ModelManager integration pending.
3. **Chat persistence** — `ChatService` uses in-memory store; ORM/repositories exist but are not default.
4. **Authentication** — placeholder; no JWT/OAuth endpoints.
5. **Rate limiting** — settings present; middleware enforcement incomplete.
6. **Fact Checker** — debate stage returns plain text unlike JSON-parsed agents.
7. **Feedback API** — frontend calls `/v1/feedback/`; backend route not implemented.

---

## Related documentation

| Document | Contents |
|----------|----------|
| [Root README.md](../README.md) | Full local / staging / production + database runbook |
| [Backend README.md](README.md) | Backend setup, migrations, Docker commands |
| [Root ARCHITECTURE.md](../ARCHITECTURE.md) | Full-stack overview, environments diagram |
| [Frontend ARCHITECTURE.md](../frontend/ARCHITECTURE.md) | Client stores, streaming, production frontend |
| [Frontend README.md](../frontend/README.md) | Frontend env and deploy steps |
