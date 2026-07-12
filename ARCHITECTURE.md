# Architecture

This document describes the clean-architecture layout of the anti-sycophancy chatbot.

## Design Principles

1. **Dependency rule** — inner layers never import from outer layers. Domain and services know nothing about FastAPI, SQLAlchemy, or vLLM.
2. **Ports & adapters** — domain interfaces (ports) are implemented by infrastructure adapters (repositories, LLM clients).
3. **Single responsibility** — each package has one reason to change.
4. **Configuration over code** — swap LLM backends, database URLs, and log formats via environment variables.

## Layer Diagram

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                  │
│              components/  lib/api.ts  types/              │
└──────────────────────────┬──────────────────────────────┘
                           │ HTTP
┌──────────────────────────▼──────────────────────────────┐
│                      API Layer                          │
│           api/router.py  api/v1/  api/deps.py            │
│         (FastAPI routers, dependency injection)           │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│                    Service Layer                        │
│                  services/chat_service.py               │
│     (orchestrates prompts + memory + model + DB)        │
└──────┬──────────┬──────────┬──────────┬────────────────┘
       │          │          │          │
       ▼          ▼          ▼          ▼
┌──────────┐ ┌────────┐ ┌────────┐ ┌──────────┐
│ Prompts  │ │ Memory │ │ Models │ │ Database │
│          │ │        │ │ (LLM)  │ │          │
└──────────┘ └────────┘ └────────┘ └──────────┘
       │          │          │          │
       └──────────┴──────────┴──────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│                     Domain Layer                        │
│            domain/entities.py  domain/interfaces.py     │
│          (pure business objects & abstract ports)         │
└─────────────────────────────────────────────────────────┘

Cross-cutting: config/  logging/  utils/  core/  schemas/
```

## Layer Responsibilities

### `api/` — HTTP Interface

| File | Purpose |
|------|---------|
| `router.py` | Aggregates versioned sub-routers |
| `deps.py` | FastAPI `Depends()` wiring (DB sessions, services) |
| `v1/health.py` | Liveness / readiness probes |
| `v1/chat.py` | Chat message endpoints |

Translates HTTP requests into service calls and returns Pydantic schemas. No business logic.

### `services/` — Application Use Cases

| File | Purpose |
|------|---------|
| `chat_service.py` | End-to-end chat flow orchestrator |

The only layer that coordinates across prompts, memory, models, and database. Will contain the anti-sycophancy pipeline once implemented.

### `domain/` — Business Core

| File | Purpose |
|------|---------|
| `entities.py` | `Conversation`, `Message`, `MessageRole` |
| `interfaces.py` | `LLMProvider`, `ConversationRepository` protocols |

Pure Python with zero framework imports. Defines *what* the system does, not *how*.

### `models/` — LLM Inference Layer

| File | Purpose |
|------|---------|
| `base.py` | `BaseLLMClient`, `GenerationConfig` |
| `vllm_client.py` | vLLM OpenAI-compatible HTTP client |
| `transformers_client.py` | Local Hugging Face Transformers inference |
| `factory.py` | Selects backend from settings |

Implements the `LLMProvider` port. Swap between vLLM (production) and Transformers (dev) via `LLM_BACKEND` env var.

### `prompts/` — Prompt Templates

| File | Purpose |
|------|---------|
| `base.py` | `BasePromptTemplate`, `PromptMessage` |
| `anti_sycophancy.py` | System prompt + conversation assembly |

Version-controlled prompt engineering. The anti-sycophancy persona lives here, separate from service logic.

### `memory/` — Context Management

| File | Purpose |
|------|---------|
| `base.py` | `BaseMemoryStore` interface |
| `conversation.py` | In-memory store (dev/test) |
| `context_manager.py` | Token-budget trimming and summarization |

Manages what prior turns are included in each LLM request.

### `database/` — Persistence

| File | Purpose |
|------|---------|
| `base.py` | SQLAlchemy `DeclarativeBase`, `TimestampMixin` |
| `session.py` | Async engine and session factory |
| `models/conversation.py` | `ConversationORM`, `MessageORM` |
| `repositories/conversation_repository.py` | PostgreSQL data access |

Implements the `ConversationRepository` port. Alembic migrations live in `backend/alembic/`.

### `config/` — Configuration

| File | Purpose |
|------|---------|
| `settings.py` | Pydantic `Settings` loaded from `.env` |

Single source of truth for all environment-driven values.

### `logging/` — Observability

| File | Purpose |
|------|---------|
| `setup.py` | JSON (production) or text (dev) log formatting |

### `utils/` — Shared Helpers

| File | Purpose |
|------|---------|
| `helpers.py` | `utc_now`, `truncate_text`, `hash_content` |
| `tokenizer.py` | Token counting for context windows |

No imports from other application layers.

### `schemas/` — API DTOs

| File | Purpose |
|------|---------|
| `chat.py` | `ChatRequest`, `ChatResponse` |
| `common.py` | `HealthResponse`, `ErrorResponse` |

Pydantic models for request validation and response serialization. Separate from domain entities and ORM models.

### `core/` — Cross-Cutting

| File | Purpose |
|------|---------|
| `lifespan.py` | Startup/shutdown hooks |
| `exceptions.py` | `AppError` hierarchy and handlers |

## Request Flow (planned)

```
User message
  → API (chat.py) validates ChatRequest
  → ChatService.process_message()
      1. ContextManager.build_context()     ← memory/
      2. ConversationPrompt.render()          ← prompts/
      3. VLLMClient.generate()               ← models/
      4. SQLConversationRepository.save()    ← database/
  → API returns ChatResponse
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

See [`.env.example`](.env.example) for the full list. Key variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_BACKEND` | `vllm` | `vllm` or `transformers` |
| `MODEL_NAME` | `meta-llama/Llama-3.1-8B-Instruct` | Hugging Face model ID |
| `VLLM_BASE_URL` | `http://localhost:8001/v1` | vLLM server endpoint |
| `DATABASE_URL` | `postgresql+asyncpg://...` | PostgreSQL connection string |

## Next Steps

1. Implement `ChatService.process_message()` pipeline
2. Wire `VLLMClient` to the vLLM OpenAI-compatible API
3. Implement `SQLConversationRepository` CRUD operations
4. Create initial Alembic migration
5. Build chat UI with streaming support
6. Refine anti-sycophancy system prompt
