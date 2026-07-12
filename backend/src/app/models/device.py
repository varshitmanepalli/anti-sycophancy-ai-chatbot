"""Hardware detection and backend availability probes."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import httpx

from app.logging.setup import get_logger

logger = get_logger(__name__)


def is_package_available(package: str) -> bool:
    """Return True if *package* is importable."""
    return importlib.util.find_spec(package) is not None


def detect_torch_device() -> str:
    """Pick the best available PyTorch device: cuda > mps > cpu."""
    if not is_package_available("torch"):
        logger.warning("PyTorch not installed — defaulting to CPU")
        return "cpu"

    import torch

    if torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(0)
        logger.info("CUDA GPU detected: %s", device_name)
        return "cuda"

    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        logger.info("Apple MPS backend detected")
        return "mps"

    logger.info("No GPU detected — using CPU")
    return "cpu"


def is_vllm_package_available() -> bool:
    """Return True if the vLLM Python package is installed."""
    return is_package_available("vllm")


async def is_vllm_server_reachable(base_url: str, timeout: float = 5.0) -> bool:
    """Ping a vLLM OpenAI-compatible server."""
    url = base_url.rstrip("/")
    endpoints = (f"{url}/models", f"{url}/health")

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            for endpoint in endpoints:
                try:
                    response = await client.get(endpoint)
                    if response.status_code == 200:
                        logger.info("vLLM server reachable at %s", endpoint)
                        return True
                except httpx.HTTPError:
                    continue
    except Exception as exc:
        logger.debug("vLLM server probe failed: %s", exc)

    return False


def resolve_model_path(model_name: str, local_path: str | None = None) -> str:
    """Return *local_path* when it exists on disk, otherwise *model_name*."""
    if local_path:
        path = Path(local_path).expanduser().resolve()
        if path.exists():
            logger.info("Using local model path: %s", path)
            return str(path)
        logger.warning("Local model path %s not found — falling back to %s", path, model_name)
    return model_name
