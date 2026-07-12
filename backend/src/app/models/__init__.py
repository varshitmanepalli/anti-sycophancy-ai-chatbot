"""Model layer — LLM inference adapters.

Abstracts Hugging Face Transformers and vLLM behind a common interface.
Use ``ModelManager`` as the primary entry point for loading and inference.
"""

from app.models.backend_types import BackendType, ModelInfo
from app.models.base import BaseLLMClient, GenerationConfig
from app.models.model_manager import ModelManager
from app.models.transformers_client import TransformersClient
from app.models.vllm_client import VLLMClient, VLLMServerClient
from app.models.vllm_local import VLLMLocalClient

__all__ = [
    "BackendType",
    "BaseLLMClient",
    "GenerationConfig",
    "ModelInfo",
    "ModelManager",
    "TransformersClient",
    "VLLMClient",
    "VLLMLocalClient",
    "VLLMServerClient",
]
