"""Default template variables per prompt type — loaded from ``prompts.yml``."""

from typing import Any

from app.prompts.config_loader import get_default_variables as _yaml_defaults
from app.prompts.types import PromptType


def merge_variables(
    prompt_type: PromptType,
    overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return YAML defaults merged with caller overrides."""
    base = dict(_yaml_defaults(prompt_type))
    if overrides:
        base.update(overrides)
    return base
