"""PromptManager — loads, versions, and renders Jinja2 prompt templates."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, Template

from app.prompts.base import PromptMessage
from app.prompts.config_loader import get_template_content, reload_prompts_config
from app.prompts.registry import PromptRegistry, TEMPLATES_DIR
from app.prompts.types import PromptTemplateMeta, PromptType
from app.prompts.variables import merge_variables
from app.logging.setup import get_logger

logger = get_logger(__name__)


class PromptManager:
    """Central manager for all versioned prompt templates.

    Usage::

        manager = PromptManager()

        # Render with defaults + overrides
        text = manager.render(
            PromptType.SYSTEM,
            variables={"tone": "blunt"},
        )

        # Pin a specific version
        text = manager.render(
            PromptType.JUDGE,
            version="2",
            variables={"user_message": "...", "support_argument": "..."},
        )

        # Render as chat message
        messages = manager.render_messages(PromptType.SUPPORT_AGENT, ...)
    """

    def __init__(
        self,
        templates_dir: Path | None = None,
        registry: PromptRegistry | None = None,
    ) -> None:
        self._dir = templates_dir or TEMPLATES_DIR
        self._registry = registry or PromptRegistry(self._dir)
        self._env = Environment(
            loader=FileSystemLoader(str(self._dir)),
            undefined=StrictUndefined,
            autoescape=False,
            keep_trailing_newline=True,
        )
        self._pinned_versions: dict[PromptType, str] = {}
        self._yaml_templates: dict[tuple[PromptType, str], Template] = {}

    def reload(self) -> None:
        """Reload prompts.yml and rebuild the registry (dev hot-reload)."""
        reload_prompts_config()
        self._registry = PromptRegistry(self._dir)
        self._yaml_templates.clear()
        self._pinned_versions.clear()
        logger.info("PromptManager reloaded from prompts.yml")

    # ------------------------------------------------------------------
    # Version management
    # ------------------------------------------------------------------

    def pin_version(self, prompt_type: PromptType, version: str) -> None:
        """Pin a prompt type to a specific version for all subsequent renders."""
        self.get_meta(prompt_type, version)  # validate exists
        self._pinned_versions[prompt_type] = version
        logger.info("Pinned %s to v%s", prompt_type.value, version)

    def unpin(self, prompt_type: PromptType) -> None:
        """Remove version pin — revert to registry default."""
        self._pinned_versions.pop(prompt_type, None)

    def get_version(self, prompt_type: PromptType) -> str:
        """Return the active version (pinned or default)."""
        return self._pinned_versions.get(
            prompt_type,
            self._registry.get_default_version(prompt_type),
        )

    def list_versions(self, prompt_type: PromptType) -> list[PromptTemplateMeta]:
        return self._registry.list_versions(prompt_type)

    def list_types(self) -> list[PromptType]:
        return self._registry.list_types()

    def get_meta(
        self, prompt_type: PromptType, version: str | None = None
    ) -> PromptTemplateMeta:
        ver = version or self.get_version(prompt_type)
        return self._registry.get_meta(prompt_type, ver)

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def render(
        self,
        prompt_type: PromptType,
        *,
        version: str | None = None,
        variables: dict[str, Any] | None = None,
    ) -> str:
        """Render a template to a plain string."""
        ver = version or self.get_version(prompt_type)
        template = self._load_template(prompt_type, ver)
        ctx = merge_variables(prompt_type, variables)
        self._validate_variables(prompt_type, ver, ctx)
        return template.render(**ctx).strip()

    def render_messages(
        self,
        prompt_type: PromptType,
        *,
        version: str | None = None,
        variables: dict[str, Any] | None = None,
        role: str | None = None,
    ) -> list[PromptMessage]:
        """Render a template and wrap as a chat ``PromptMessage``."""
        meta = self.get_meta(prompt_type, version)
        content = self.render(prompt_type, version=version, variables=variables)
        return [PromptMessage(role=role or meta.role, content=content)]

    def to_chat_format(
        self,
        prompt_type: PromptType,
        *,
        version: str | None = None,
        variables: dict[str, Any] | None = None,
    ) -> list[dict[str, str]]:
        """Render and return OpenAI/vLLM-compatible chat messages."""
        return [
            {"role": m.role, "content": m.content}
            for m in self.render_messages(
                prompt_type, version=version, variables=variables
            )
        ]

    def render_all(
        self,
        variables_by_type: dict[PromptType, dict[str, Any]] | None = None,
    ) -> dict[PromptType, str]:
        """Render all registered prompt types (useful for multi-agent pipelines)."""
        overrides = variables_by_type or {}
        return {
            pt: self.render(pt, variables=overrides.get(pt))
            for pt in self.list_types()
        }

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _load_template(self, prompt_type: PromptType, version: str) -> Template:
        cache_key = (prompt_type, version)
        if cache_key in self._yaml_templates:
            return self._yaml_templates[cache_key]

        yaml_content = get_template_content(prompt_type, version)
        if yaml_content is not None:
            template = Template(yaml_content, undefined=StrictUndefined)
            self._yaml_templates[cache_key] = template
            return template

        relative = f"{prompt_type.value}/v{version}.j2"
        return self._env.get_template(relative)

    def _validate_variables(
        self,
        prompt_type: PromptType,
        version: str,
        ctx: dict[str, Any],
    ) -> None:
        """Warn when required manifest variables are missing (non-blocking)."""
        try:
            meta = self._registry.get_meta(prompt_type, version)
        except KeyError:
            return
        missing = [v for v in meta.variables if v not in ctx]
        if missing:
            logger.warning(
                "Template %s missing variables: %s",
                meta.template_id,
                missing,
            )


@lru_cache
def get_prompt_manager() -> PromptManager:
    """Cached singleton for application-wide use."""
    return PromptManager()
