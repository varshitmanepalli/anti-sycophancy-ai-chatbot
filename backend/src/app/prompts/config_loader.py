"""Load central prompt configuration from ``prompts.yml``.

All prompt text, default variables, and active version pins live in
``prompts/prompts.yml`` so operators can edit prompts without touching Python.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from app.prompts.types import PromptTemplateMeta, PromptType

PROMPTS_YML = Path(__file__).parent / "prompts.yml"


@lru_cache
def load_prompts_config(path: Path | None = None) -> dict[str, Any]:
    """Parse and cache the central prompts YAML file."""
    config_path = path or PROMPTS_YML
    if not config_path.exists():
        return {"defaults": {}, "active_versions": {}, "templates": {}}
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def reload_prompts_config(path: Path | None = None) -> dict[str, Any]:
    """Clear cache and reload prompts.yml (useful in dev/tests)."""
    load_prompts_config.cache_clear()
    return load_prompts_config(path)


def get_active_version(prompt_type: PromptType, config: dict[str, Any] | None = None) -> str:
    """Return the pinned active version for a prompt type."""
    cfg = config or load_prompts_config()
    active = cfg.get("active_versions", {})
    return str(active.get(prompt_type.value, "1"))


def get_default_variables(
    prompt_type: PromptType,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Merge global + per-type default variables from prompts.yml."""
    cfg = config or load_prompts_config()
    defaults = cfg.get("defaults", {})
    global_defaults = dict(defaults.get("global", {}))
    type_defaults = dict(defaults.get(prompt_type.value, {}))
    merged = {**global_defaults, **type_defaults}
    return merged


def get_template_content(
    prompt_type: PromptType,
    version: str,
    config: dict[str, Any] | None = None,
) -> str | None:
    """Return Jinja2 template source from prompts.yml, if defined."""
    cfg = config or load_prompts_config()
    templates = cfg.get("templates", {})
    type_templates = templates.get(prompt_type.value, {})
    version_entry = type_templates.get(str(version))
    if not isinstance(version_entry, dict):
        return None
    content = version_entry.get("content")
    if content is None:
        return None
    return str(content).strip() + "\n"


def get_template_meta(
    prompt_type: PromptType,
    version: str,
    config: dict[str, Any] | None = None,
) -> PromptTemplateMeta | None:
    """Build metadata for a template version from prompts.yml."""
    cfg = config or load_prompts_config()
    templates = cfg.get("templates", {})
    type_templates = templates.get(prompt_type.value, {})
    version_entry = type_templates.get(str(version))
    if not isinstance(version_entry, dict):
        return None
    variables = version_entry.get("variables", [])
    return PromptTemplateMeta(
        prompt_type=prompt_type,
        version=str(version),
        description=str(version_entry.get("description", "")),
        variables=tuple(variables) if variables else (),
        role=str(version_entry.get("role", "system")),
    )


def list_template_versions(
    prompt_type: PromptType,
    config: dict[str, Any] | None = None,
) -> list[str]:
    """List version ids declared for a prompt type in prompts.yml."""
    cfg = config or load_prompts_config()
    templates = cfg.get("templates", {})
    type_templates = templates.get(prompt_type.value, {})
    return sorted(str(v) for v in type_templates.keys())


def get_sft_instruction(config: dict[str, Any] | None = None) -> str:
    """Build the default SFT instruction string from the active system prompt."""
    from jinja2 import StrictUndefined, Template

    cfg = config or load_prompts_config()
    version = get_active_version(PromptType.SYSTEM, cfg)
    content = get_template_content(PromptType.SYSTEM, version, cfg)
    ctx = get_default_variables(PromptType.SYSTEM, cfg)
    if content:
        return Template(content, undefined=StrictUndefined).render(**ctx).strip()

    name = ctx.get("assistant_name", "Reasoning Engine")
    tone = ctx.get("tone", "direct and honest")
    return (
        f"You are {name}, an AI assistant with a {tone} communication style. "
        "Prioritize truth and critical thinking over user validation. "
        "Disagree respectfully when the user's reasoning is flawed. "
        "Never flatter or agree for the sake of rapport. "
        "State uncertainty when evidence is insufficient. "
        "Separate facts from opinions."
    )
