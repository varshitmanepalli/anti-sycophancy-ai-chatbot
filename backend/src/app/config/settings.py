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
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/chatbot"
    )
    database_echo: bool = False
    database_pool_size: int = 5
    database_max_overflow: int = 10

    # LLM / Model — defaults to Qwen3-14B
    model_name: str = "Qwen/Qwen3-14B"
    model_path: str | None = None
    model_backend: Literal["auto", "vllm_server", "vllm_local", "transformers"] = "auto"
    model_device: str = "auto"
    allow_cpu_fallback: bool = True
    prefer_vllm: bool = True
    llm_backend: Literal["vllm", "transformers"] = "vllm"  # legacy alias

    # vLLM server
    vllm_base_url: str = "http://localhost:8001/v1"
    vllm_timeout: float = 300.0
    vllm_tensor_parallel_size: int = 1
    vllm_gpu_memory_utilization: float = 0.9
    vllm_max_model_len: int | None = None

    # Transformers
    transformers_torch_dtype: str = "auto"

    # Generation defaults
    max_tokens: int = 1024
    temperature: float = 0.7
    top_p: float = 0.9

    # Memory
    max_context_turns: int = 20

    # Model warmup on startup
    model_auto_load: bool = False

    # Authentication (placeholder)
    auth_enabled: bool = False
    api_key: str | None = None

    # Rate limiting (placeholder)
    rate_limit_enabled: bool = False
    rate_limit_requests: int = 60
    rate_limit_window_seconds: int = 60

    # Input classifier
    classifier_mode: Literal["rules", "llm", "hybrid"] = "rules"
    classifier_confidence_threshold: float = 0.75

    # Claim extraction
    claim_extraction_max_tokens: int = 1024
    claim_extraction_temperature: float = 0.1

    # Assumption detection
    assumption_detection_max_tokens: int = 1024
    assumption_detection_temperature: float = 0.1

    # Fallacy detection
    fallacy_detection_max_tokens: int = 1024
    fallacy_detection_temperature: float = 0.1

    # Debate engine
    debate_max_tokens: int = 2048
    debate_temperature: float = 0.7
    debate_judge_max_tokens: int = 1024
    debate_judge_temperature: float = 0.3

    # Confidence scoring
    confidence_scoring_max_tokens: int = 1024
    confidence_scoring_temperature: float = 0.1

    # Memory extraction
    memory_extraction_max_tokens: int = 1024
    memory_extraction_temperature: float = 0.1

    # Contradiction detection
    contradiction_detection_max_tokens: int = 1024
    contradiction_detection_temperature: float = 0.1

    # Logging
    log_level: str = "INFO"
    log_format: Literal["json", "text"] = "json"

    # Prompts — edit ``prompts/prompts.yml`` to change template text and defaults
    prompts_file: str | None = None
    system_prompt_version: str | None = None


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton — safe to call on every request."""
    return Settings()
