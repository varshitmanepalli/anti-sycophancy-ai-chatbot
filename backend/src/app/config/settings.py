"""Application settings loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All configuration values with sensible defaults for local development."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "Anti-Sycophancy Chatbot"
    app_version: str = "0.1.0"
    debug: bool = False
    api_prefix: str = "/api"

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/chatbot"
    )
    database_echo: bool = False
    database_pool_size: int = 5
    database_max_overflow: int = 10

    # LLM / Model
    llm_backend: Literal["vllm", "transformers"] = "vllm"
    model_name: str = "meta-llama/Llama-3.1-8B-Instruct"
    model_device: str = "auto"
    vllm_base_url: str = "http://localhost:8001/v1"

    # Generation defaults
    max_tokens: int = 1024
    temperature: float = 0.7
    top_p: float = 0.9

    # Memory
    max_context_turns: int = 20

    # Logging
    log_level: str = "INFO"
    log_format: Literal["json", "text"] = "json"


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton — safe to call on every request."""
    return Settings()
