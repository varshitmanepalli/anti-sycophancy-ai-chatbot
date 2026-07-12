"""Anti-sycophancy AI chatbot application package.

This is the root package for the FastAPI backend. All application code lives
under ``app/`` and is organized by clean-architecture layers:

- ``api/``        — HTTP interface (routers, dependencies)
- ``services/``   — Application / use-case orchestration
- ``domain/``     — Pure business entities and interfaces (no I/O)
- ``models/``     — LLM inference adapters (vLLM, Transformers)
- ``prompts/``    — System and task prompt templates
- ``memory/``     — Conversation context and memory management
- ``database/``   — PostgreSQL persistence (SQLAlchemy ORM + repositories)
- ``config/``     — Environment-driven settings
- ``logging/``    — Structured logging setup
- ``utils/``      — Shared helpers with no layer dependencies
- ``schemas/``    — Pydantic request/response DTOs
- ``core/``       — Cross-cutting concerns (exceptions, lifespan)
"""

__version__ = "0.1.0"
