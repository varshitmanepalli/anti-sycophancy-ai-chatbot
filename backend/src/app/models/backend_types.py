"""Shared types for model backends and runtime metadata."""

from dataclasses import dataclass
from enum import StrEnum


class BackendType(StrEnum):
    """Supported inference backend identifiers."""

    VLLM_SERVER = "vllm_server"
    VLLM_LOCAL = "vllm_local"
    TRANSFORMERS = "transformers"


@dataclass(frozen=True)
class ModelInfo:
    """Snapshot of the currently loaded model."""

    model_id: str
    resolved_path: str
    backend: BackendType
    device: str
    is_loaded: bool = True

    def __str__(self) -> str:
        return (
            f"ModelInfo(model={self.model_id!r}, backend={self.backend}, "
            f"device={self.device}, loaded={self.is_loaded})"
        )
