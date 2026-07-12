# Anti-Sycophancy AI Chatbot

A production-ready reasoning engine that uses open-source Hugging Face models to deliver honest, critical responses instead of sycophantic agreement. The backend exposes a multi-stage reasoning pipeline, specialized analysis agents, and tooling for SFT dataset generation and benchmark evaluation.

## Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Backend    | Python 3.12, FastAPI, SQLAlchemy    |
| Inference  | vLLM (production), Transformers (dev) |
| Database   | PostgreSQL 16                       |
| Frontend   | React 19, Next.js 15, TypeScript    |
| Infra      | Docker, Docker Compose              |

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

### Training & evaluation

| Tool | Script | Purpose |
|------|--------|---------|
| SFT dataset generation | `scripts/generate_sft_dataset.py` | Convert conversations to QLoRA-compatible JSONL |
| DB export | `scripts/export_sft_from_db.py` | Export PostgreSQL conversations to SFT JSONL |
| Benchmark evaluation | `scripts/run_eval.py` | Score model outputs and generate reports |

Evaluation metrics: agreement rate, hallucination rate, evidence usage, logical consistency, bias detection, and confidence calibration (ECE/Brier).

## Project Structure

```
ai-reasoning-engine/
├── backend/
│   ├── src/app/
│   │   ├── api/              # HTTP routers & dependency injection
│   │   ├── services/         # Engines, detectors, parsers, chat pipeline
│   │   ├── domain/           # Dataclass business types & ports
│   │   ├── models/           # LLM inference adapters (vLLM, Transformers)
│   │   ├── prompts/          # Jinja2 templates & PromptManager
│   │   ├── memory/           # Conversation context management
│   │   ├── database/         # SQLAlchemy ORM & repositories
│   │   ├── training/         # SFT dataset & benchmark evaluation
│   │   │   ├── sft/          # Conversation → Alpaca JSONL converter
│   │   │   └── eval/         # Metrics, runner, report generation
│   │   ├── config/           # Pydantic settings (app + training)
│   │   ├── logging/          # Structured logging
│   │   ├── schemas/          # API request/response DTOs
│   │   └── core/             # Lifespan, exceptions, middleware
│   ├── scripts/              # CLI tools (SFT, eval, DB export)
│   ├── data/                 # Sample conversations, benchmarks, reports
│   ├── alembic/              # Database migrations
│   ├── tests/                # 235 unit & integration tests
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── app/              # App Router pages
│   │   ├── components/       # React components
│   │   ├── lib/              # API client
│   │   └── types/            # TypeScript interfaces
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── ARCHITECTURE.md
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- (Optional) NVIDIA GPU + drivers for vLLM

### 1. Configure environment

```bash
cp .env.example .env
```

### 2. Start all services

```bash
docker compose up --build
```

| Service  | URL                        |
|----------|----------------------------|
| Frontend | http://localhost:3000      |
| API      | http://localhost:8000/api  |
| API docs | http://localhost:8000/docs |
| vLLM     | http://localhost:8001/v1   |

### 3. Run backend locally (without Docker)

```bash
cd backend
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

pip install -e ".[dev]"
uvicorn app.main:app --reload --app-dir src
```

### 4. Run frontend locally

```bash
cd frontend
npm install
npm run dev
```

## Training & Evaluation

All commands run from the `backend/` directory with `PYTHONPATH=src`.

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

Training settings use the `TRAINING_` env prefix (e.g. `TRAINING_SFT_VAL_RATIO`, `TRAINING_EVAL_OUTPUT_DIR`). See `backend/src/app/config/training.py`.

## Development

```bash
cd backend

# Tests (requires PYTHONPATH=src)
PYTHONPATH=src python -m pytest tests/ -q

# Lint
ruff check src/

# Type check
mypy src/app

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
```

On Windows PowerShell, set `$env:PYTHONPATH="src"` before running pytest or scripts.

## API Overview

Base URL: `http://localhost:8000/api`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness probe |
| GET | `/ready` | Readiness probe |
| POST | `/chat` | Full reasoning pipeline (structured analysis output) |
| POST | `/v1/chat/` | Chat message via ChatService |
| POST | `/v1/chat/stream` | Streaming chat response (SSE) |
| POST | `/v1/classify` | Input classification |
| POST | `/v1/claims/extract` | Claim extraction |
| POST | `/v1/assumptions/detect` | Assumption detection |
| POST | `/v1/fallacies/detect` | Fallacy detection |
| POST | `/v1/debate/run` | Multi-agent debate |
| POST | `/v1/confidence/score` | Confidence scoring |
| POST | `/v1/memory/extract` | Memory extraction |
| POST | `/v1/memory/store` | Persist extracted memory |
| POST | `/v1/contradictions/check` | Contradiction detection |
| POST | `/v1/contradictions/check-and-store` | Detect and persist contradictions |

Interactive docs: http://localhost:8000/docs

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for layer responsibilities, data flow, and design decisions.

## License

MIT
