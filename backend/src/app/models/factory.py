"""Model client factory.

Selects the appropriate LLM backend (vLLM or Transformers) based on
application settings.
"""

from app.config.settings import Settings
from app.models.base import BaseLLMClient
from app.models.transformers_client import TransformersClient
from app.models.vllm_client import VLLMClient


def create_llm_client(settings: Settings) -> BaseLLMClient:
    """Instantiate the configured LLM inference backend."""
    if settings.llm_backend == "vllm":
        return VLLMClient(
            base_url=settings.vllm_base_url,
            model_name=settings.model_name,
        )
    if settings.llm_backend == "transformers":
        return TransformersClient(
            model_id=settings.model_name,
            device=settings.model_device,
        )
    raise ValueError(f"Unknown LLM backend: {settings.llm_backend!r}")
