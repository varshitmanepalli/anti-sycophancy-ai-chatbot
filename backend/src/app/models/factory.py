"""Model client factory.

Delegates to ``ModelManager`` for backend selection and lifecycle.
"""

from app.config.settings import Settings
from app.models.base import BaseLLMClient
from app.models.model_manager import ModelManager


async def create_llm_client(settings: Settings | None = None) -> BaseLLMClient:
    """Return the active backend from the ``ModelManager`` singleton.

    Loads the model on first call if not already loaded.
    """
    manager = await ModelManager.get_instance(settings)
    if not manager.is_loaded:
        await manager.load()
    return manager.get_active_backend()
