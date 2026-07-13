"""Prompt template layer.

Versioned Jinja2 templates managed by ``PromptManager``.

**Edit prompts in ``prompts.yml``** — all template text, default variables,
and active version pins live in that single file for easy updates without
code changes. Legacy ``templates/{type}/v{N}.j2`` files remain as fallback.
"""

from app.prompts.config_loader import (
    get_active_version,
    get_default_variables,
    get_sft_instruction,
    get_template_content,
    load_prompts_config,
    reload_prompts_config,
)
from app.prompts.manager import PromptManager, get_prompt_manager
from app.prompts.types import PromptTemplateMeta, PromptType

__all__ = [
    "PromptManager",
    "PromptTemplateMeta",
    "PromptType",
    "get_prompt_manager",
    "load_prompts_config",
    "reload_prompts_config",
    "get_default_variables",
    "get_active_version",
    "get_template_content",
    "get_sft_instruction",
]
