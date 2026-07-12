# Architecture

This document describes the clean-architecture layout of the anti-sycophancy reasoning engine.

## Design Principles

1. **Dependency rule** — inner layers never import from outer layers. Domain types and service logic do not depend on FastAPI, SQLAlchemy, or vLLM.
2. **Ports & adapters** — domain interfaces (ports) are implemented by infrastructure adapters (repositories, LLM clients).
3. **Single responsibility** — each package has one reason to change (e.g. parsers parse, engines orchestrate, routers translate HTTP).
4. **Configuration over code** — swap LLM backends, database URLs, log formats, and training defaults via environment variables.
5. **Dependency injection** — FastAPI `Depends()` in `api/deps.py` wires settings, `ModelManager`, `PromptManager`, repositories, and services. CLI pipelines accept injectable settings and registries.
6. **Composition over inheritance** — orchestrators (`ChatPipeline`, `DebateEngine`, `EvalPipeline`) compose injected collaborators rather than extending base classes.

## Layer Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                         │
│              components/  lib/api.ts  types/                   │
└──────────────────────────┬───────────────────────────────────┘
                           │ HTTP
┌──────────────────────────▼───────────────────────────────────┐
│                      API Layer                               │
│         api/router.py  api/v1/  api/deps.py                   │
│         (FastAPI routers, dependency injection)              │
└──────────────────────────┬───────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────┐
│                    Service Layer                             │
│   chat_service  chat_pipeline  debate  classification         │
│   claims  assumptions  fallacies  confidence  memory           │
│   contradictions  (+ parsers per feature)                    │
└──────┬──────────┬──────────┬──────────┬──────────┬──────────┘
       │          │          │          │          │
       ▼          ▼          ▼          ▼          ▼
┌──────────┐ ┌────────┐ ┌────────┐ ┌──────────┐ ┌──────────┐
│ Prompts  │ │ Memory │ │ Models │ │ Database │ │ Training │
│ (Jinja2) │ │        │ │ (LLM)  │ │          │ │ SFT/eval │
└──────────┘ └────────┘ └────────┘ └──────────┘ └──────────┘
       │          │          │          │          │
       └──────────┴──────────┴──────────┴──────────┘
                           │
┌──────────────────────────▼───────────────────────────────────┐
│                     Domain Layer                             │
│   debate  fallacies  confidence  memory  claims  ...          │
│   entities  interfaces  llm_interface  memory_interfaces     │
│          (dataclass business types & abstract ports)           │
└──────────────────────────────────────────────────────────────┘

Cross-cutting: config/  logging/  utils/  core/  schemas/
```

## Feature Module Pattern

Every LLM-backed analyzer follows the same structure:

```
domain/{feature}.py          → dataclass result types
services/{feature}/
    engine.py | detector.py | extractor.py   → orchestrates LLM call
    parser.py                                → JSON → domain object
prompts/templates/{type}/v{N}.j2             → versioned Jinja2 template
prompts/templates/{type}/manifest.yaml       → metadata & variables
schemas/{feature}.py                         → Pydantic API DTOs
api/v1/{feature}.py                          → thin HTTP endpoint
tests/test_{feature}_*.py                    → parser, engine, API tests
```

| Module | Engine class | Parser | API endpoint |
|--------|-------------|--------|--------------|
| Classification | `InputClassifier` | — | `POST /v1/classify` |
| Claims | `ClaimExtractor` | `ClaimExtractionParser` | `POST /v1/claims/extract` |
| Assumptions | `AssumptionDetector` | `AssumptionDetectionParser` | `POST /v1/assumptions/detect` |
| Fallacies | `LogicalFallacyDetector` | `FallacyDetectionParser` | `POST /v1/fallacies/detect` |
| Debate | `DebateEngine` | `SupportAgentParser`, `OpponentAgentParser`, `JudgeVerdictParser` | `POST /v1/debate/run` |
| Confidence | `ConfidenceEngine` | `ConfidenceScoreParser` | `POST /v1/confidence/score` |
| Memory | `MemoryExtractor`, `MemoryStore` | `MemoryExtractionParser` | `POST /v1/memory/extract`, `/store` |
| Contradictions | `ContradictionDetector`, `MemoryContradictionChecker` | `ContradictionCheckParser` | `POST /v1/contradictions/check`, `/check-and-store` |

Engines receive `ModelManager`, `Settings`, and `PromptManager` via constructor injection (wired in `api/deps.py`).

## Layer Responsibilities

### `api/` — HTTP Interface

| File | Purpose |
|------|---------|
| `router.py` | Aggregates `/chat` pipeline route and `/v1` sub-routers |
| `chat.py` | `POST /chat` — full reasoning pipeline entry point |
| `deps.py` | FastAPI `Depends()` wiring for all services and repositories |
| `v1/router.py` | Versioned sub-router aggregation |
| `v1/*.py` | One router per feature (health, chat, classify, debate, …) |

Translates HTTP requests into service calls and returns Pydantic schemas. No business logic.

### `services/` — Application Use Cases

| Package | Purpose |
|---------|---------|
| `chat_service.py` | End-to-end chat: memory → prompt → inference → response |
| `chat_pipeline/` | Staged reasoning pipeline (classify → claims → assumptions → fallacies → inference → confidence) |
| `debate/` | Four-stage debate: Support → Opponent → Fact Checker → Judge |
| `classification/` | Rule-based, LLM, and hybrid input classification |
| `claims/` | Factual claim extraction |
| `assumptions/` | Hidden assumption detection |
| `fallacies/` | Logical fallacy detection (8 categories) |
| `confidence/` | Multi-dimension confidence scoring |
| `memory/` | Long-term memory extraction and persistence |
| `contradictions/` | Memory contradiction detection and storage |
| `health_service.py` | Liveness/readiness checks |

### `domain/` — Business Core

| File | Purpose |
|------|---------|
| `entities.py` | `Conversation`, `Message`, `MessageRole` |
| `debate.py` | `DebateStage`, `JudgeVerdict`, `DebateResult` |
| `fallacies.py` | `FallacyType`, `DetectedFallacy`, `FallacyDetectionResult` |
| `confidence.py` | `DimensionScore`, `ConfidenceResult` |
| `memory.py` | `UserFact`, `UserOpinion`, `UserGoal`, `MemoryContradiction` |
| `memory_extraction.py` | `ExtractedMemoryItem`, `MemoryExtractionResult` |
| `claims.py`, `assumptions.py`, `classification.py`, `contradiction_check.py` | Feature-specific domain types |
| `support_agent.py`, `opponent_agent.py` | Structured debate agent outputs |
| `llm_interface.py` | `LLMProvider` protocol |
| `memory_interfaces.py` | Memory repository protocols |
| `interfaces.py` | Re-exports of domain ports |

All domain types are plain `@dataclass` objects with `to_dict()`. No framework imports.

### `models/` — LLM Inference Layer

| File | Purpose |
|------|---------|
| `base.py` | `GenerationConfig`, shared client interface |
| `model_manager.py` | Singleton that owns the active LLM backend |
| `vllm_client.py` | vLLM OpenAI-compatible HTTP client |
| `vllm_local.py` | In-process vLLM engine |
| `transformers_client.py` | Local Hugging Face Transformers inference |
| `factory.py` | Selects backend from settings (`auto`, `vllm_server`, `vllm_local`, `transformers`) |

Implements the `LLMProvider` port. Swap backends via `MODEL_BACKEND` / `LLM_BACKEND` env vars.

### `prompts/` — Prompt Templates

| File | Purpose |
|------|---------|
| `manager.py` | `PromptManager` — load, version, and render Jinja2 templates |
| `registry.py` | Discovers templates from `manifest.yaml` files |
| `types.py` | `PromptType` enum (12 template categories) |
| `variables.py` | Default template variable merging |
| `anti_sycophancy.py` | Legacy conversation prompt assembly for `ChatService` |
| `templates/` | Versioned `.j2` templates per agent |

Version-controlled prompt engineering. Each agent has independent version history (e.g. Judge v4, Support v2, Opponent v2).

### `memory/` — Context Management

| File | Purpose |
|------|---------|
| `conversation.py` | `InMemoryStore` for dev/test chat history |
| `context_manager.py` | Token-budget trimming for chat context |
| `postgres_store.py` | PostgreSQL-backed memory persistence |

### `database/` — Persistence

| File | Purpose |
|------|---------|
| `session.py` | Async SQLAlchemy engine and session factory |
| `models/conversation.py` | `ConversationORM`, `MessageORM` |
| `models/memory.py` | `UserFactORM`, `UserOpinionORM`, `UserGoalORM`, `MemoryContradictionORM` |
| `repositories/memory_repository.py` | PostgreSQL memory CRUD |

Alembic migrations live in `backend/alembic/`. Initial migration: `001_memory_schema.py`.

### `training/` — SFT & Evaluation (offline)

| Package | Purpose |
|---------|---------|
| `sft/converter.py` | `ConversationToSFTConverter` — one Alpaca row per assistant turn |
| `sft/pipeline.py` | `SFTDatasetPipeline` — load, convert, split, write JSONL |
| `sft/io.py` | JSON/JSONL I/O, QLoRA `dataset_info.json` |
| `eval/metrics/` | Six heuristic metrics (agreement, hallucination, evidence, consistency, bias, calibration) |
| `eval/registry.py` | `MetricRegistry` — DI-friendly metric factory |
| `eval/runner.py` | `EvaluationRunner` — per-case scoring and aggregation |
| `eval/pipeline.py` | `EvalPipeline` — load benchmark, run, write reports |
| `eval/report_writer.py` | JSON, Markdown, and HTML report output |
| `constants.py` | Shared metric name constants |

CLI scripts in `backend/scripts/` invoke these pipelines. Configuration is in `config/training.py` (`TRAINING_` env prefix).

### `config/` — Configuration

| File | Purpose |
|------|---------|
| `settings.py` | Application `Settings` (LLM, DB, feature knobs, logging) |
| `training.py` | `TrainingSettings` (SFT split, eval metrics, calibration thresholds) |

### `logging/` — Observability

| File | Purpose |
|------|---------|
| `setup.py` | `configure_logging()`, `get_logger()` — JSON (production) or text (dev) |

All services and pipelines use structured logging. CLI scripts call `configure_logging(get_settings())` on startup.

### `schemas/` — API DTOs

Pydantic models for request validation and response serialization. Each feature has a matching schema file with `from_domain()` classmethods where applicable. Separate from domain dataclasses and ORM models.

### `core/` — Cross-Cutting

| File | Purpose |
|------|---------|
| `lifespan.py` | Startup/shutdown hooks (optional model warmup) |
| `exceptions.py` | `AppError` hierarchy and FastAPI handlers |
| `middleware.py` | Request middleware |
| `security.py` | Auth placeholder (`get_current_user`) |

## Request Flows

### Chat pipeline (`POST /api/chat`)

```
ChatPipelineRequest
  → ChatPipeline.run()
      1. load_context          ← memory / DB (TODO: wire DB history)
      2. classify_input        ← InputClassifier
      3. extract_claims        ← ClaimExtractor
      4. detect_assumptions    ← AssumptionDetector
      5. detect_fallacies      ← LogicalFallacyDetector
      6. build_prompt          ← PromptManager
      7. run_inference         ← ModelManager
      8. score_confidence      ← ConfidenceEngine
      9. extract_reasoning     ← structured reasoning steps
  → ChatPipelineResponse
```

Each stage mutates a shared `PipelineContext` dataclass and logs at DEBUG level.

### Standard chat (`POST /api/v1/chat/`)

```
ChatRequest
  → ChatService.process_message()
      1. InMemoryStore.append(user message)
      2. ContextManager.build_context()
      3. ConversationPrompt.to_chat_format()
      4. ModelManager.generate()
      5. InMemoryStore.append(assistant reply)
  → ChatResponse  (or SSE stream via /v1/chat/stream)
```

### Debate engine (`POST /api/v1/debate/run`)

```
DebateRequest
  → DebateEngine.run()
      1. Support Agent (v2)    → SupportAgentParser → JSON arguments
      2. Opponent Agent (v2)   → OpponentAgentParser → weaknesses/challenges
      3. Fact Checker (v1)     → plain-text report
      4. Judge (v4)            → JudgeVerdictParser → facts/assumptions/evidence/unknowns/conclusion
  → DebateResponse
```

All four stages share one `ModelManager` LLM. Each stage receives output from prior stages via Jinja2 template variables.

### Benchmark evaluation (CLI)

```
Benchmark JSON/JSONL
  → EvalPipeline.run()
      1. load_benchmark_dataset()
      2. EvaluationRunner.run()
           → per-case metrics via MetricRegistry
           → dataset-level calibration (ECE, Brier)
      3. ReportWriter.write()  → report.json, report.md, report.html
```

## Dependency Injection

`api/deps.py` is the composition root for the HTTP layer:

| Dependency type | Examples |
|-----------------|----------|
| Settings | `SettingsDep` |
| Database | `DbSession`, `MemoryRepositoryDep` |
| LLM | `ModelManagerDep` |
| Prompts | `PromptManagerDep` |
| Services | `ChatServiceDep`, `DebateEngineDep`, `ConfidenceEngineDep`, … |

Training pipelines use constructor injection without FastAPI:

```python
EvalPipeline(settings=TrainingSettings(), registry=MetricRegistry())
SFTDatasetPipeline(settings=TrainingSettings(), converter=ConversationToSFTConverter())
```

## Frontend Structure

| Path | Purpose |
|------|---------|
| `src/app/` | Next.js App Router (layout, pages) |
| `src/components/chat/` | ChatWindow, MessageBubble, ChatInput |
| `src/components/ui/` | Shared UI primitives |
| `src/lib/api.ts` | HTTP client for FastAPI backend |
| `src/types/chat.ts` | TypeScript interfaces mirroring backend schemas |

Components never call `fetch()` directly — all API communication goes through `lib/api.ts`.

## Environment Variables

See [`.env.example`](.env.example) for the full application list. Key variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_NAME` | `Qwen/Qwen3-14B` | Hugging Face model ID |
| `MODEL_BACKEND` | `auto` | `auto`, `vllm_server`, `vllm_local`, `transformers` |
| `VLLM_BASE_URL` | `http://localhost:8001/v1` | vLLM OpenAI-compatible endpoint |
| `DATABASE_URL` | `postgresql+asyncpg://...` | PostgreSQL connection string |
| `CLASSIFIER_MODE` | `rules` | `rules`, `llm`, or `hybrid` |
| `LOG_FORMAT` | `json` | `json` or `text` |

Training-specific settings use the `TRAINING_` prefix (see `config/training.py`):

| Variable | Default | Description |
|----------|---------|-------------|
| `TRAINING_SFT_VAL_RATIO` | `0.1` | Validation split for SFT datasets |
| `TRAINING_SFT_OUTPUT_DIR` | `data/sft` | SFT JSONL output directory |
| `TRAINING_EVAL_OUTPUT_DIR` | `data/eval_reports` | Benchmark report output |
| `TRAINING_EVAL_CALIBRATION_BINS` | `10` | ECE bin count |

## Testing

235 tests in `backend/tests/` covering parsers, engines, prompts, APIs, pipelines, SFT generation, and evaluation metrics. Run with:

```bash
cd backend
PYTHONPATH=src python -m pytest tests/ -q
```

Tests use `AsyncMock` model managers with hardcoded JSON fixtures for deterministic parser and engine validation.

## Known Gaps & Future Work

1. **Chat pipeline context** — `load_context` does not yet load history from PostgreSQL; returns empty history.
2. **Chat pipeline inference** — `run_inference` is stubbed; response generation not fully wired to `ModelManager`.
3. **Fact Checker** — debate Fact Checker stage returns plain text (not structured JSON like other agents).
4. **Authentication** — `AUTH_ENABLED` placeholder; no production auth flow yet.
5. **Rate limiting** — configured but not enforced in middleware.
6. **LLM-as-judge eval** — benchmark metrics are heuristic/rule-based; LLM judge can be registered via `MetricRegistry.register()`.
