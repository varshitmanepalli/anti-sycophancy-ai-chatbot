"""Prompt template layer.

Versioned Jinja2 templates managed by ``PromptManager``. Templates live
in ``templates/{type}/v{N}.j2`` with per-type ``manifest.yaml`` files.
"""

from app.prompts.manager import PromptManager, get_prompt_manager
from app.prompts.types import PromptTemplateMeta, PromptType

__all__ = [
    "PromptManager",
    "PromptTemplateMeta",
    "PromptType",
    "get_prompt_manager",
]
