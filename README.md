# Anti-Sycophancy AI Chatbot

A production-ready, modular chatbot that uses open-source Hugging Face models to deliver honest, critical responses instead of sycophantic agreement.

## Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Backend    | Python 3.12, FastAPI, SQLAlchemy    |
| Inference  | vLLM (production), Transformers (dev) |
| Database   | PostgreSQL 16                       |
| Frontend   | React 19, Next.js 15, TypeScript    |
| Infra      | Docker, Docker Compose              |

## Project Structure

```
ai-reasoning-engine/
├── backend/                  # FastAPI application
│   ├── src/app/
│   │   ├── api/              # HTTP routers & dependencies
│   │   ├── services/         # Use-case orchestration
│   │   ├── domain/           # Entities & ports (interfaces)
│   │   ├── models/           # LLM inference adapters
│   │   ├── prompts/          # Anti-sycophancy prompt templates
│   │   ├── memory/           # Conversation context management
│   │   ├── database/         # SQLAlchemy ORM & repositories
│   │   ├── config/           # Pydantic settings
│   │   ├── logging/          # Structured logging
│   │   ├── utils/            # Shared helpers
│   │   ├── schemas/          # API request/response DTOs
│   │   └── core/             # Lifespan, exceptions
│   ├── alembic/              # Database migrations
│   ├── tests/
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/                 # Next.js application
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
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --app-dir src
```

### 4. Run frontend locally

```bash
cd frontend
npm install
npm run dev
```

## Development

```bash
# Backend tests
cd backend && pytest

# Lint
cd backend && ruff check src/

# Database migrations
cd backend && alembic revision --autogenerate -m "description"
cd backend && alembic upgrade head
```

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for layer responsibilities, data flow, and design decisions.

## License

MIT
