"""Version registry for prompt templates.

Each prompt type has a manifest (``manifest.yaml``) in its template
directory declaring available versions, the default, and required variables.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from app.prompts.types import PromptTemplateMeta, PromptType

TEMPLATES_DIR = Path(__file__).parent / "templates"


class PromptRegistry:
    """Loads and indexes versioned template metadata from disk."""

    def __init__(self, templates_dir: Path | None = None) -> None:
        self._dir = templates_dir or TEMPLATES_DIR
        self._catalog: dict[PromptType, dict[str, PromptTemplateMeta]] = {}
        self._defaults: dict[PromptType, str] = {}
        self._load_all()

    def _load_all(self) -> None:
        for prompt_type in PromptType:
            type_dir = self._dir / prompt_type.value
            if not type_dir.exists():
                continue
            self._catalog[prompt_type] = {}
            manifest_path = type_dir / "manifest.yaml"
            if manifest_path.exists():
                self._load_manifest(prompt_type, manifest_path)
            else:
                self._discover_versions(prompt_type, type_dir)

    def _load_manifest(self, prompt_type: PromptType, path: Path) -> None:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        self._defaults[prompt_type] = str(data.get("default_version", "1"))
        for version, meta in data.get("versions", {}).items():
            self._catalog[prompt_type][str(version)] = PromptTemplateMeta(
                prompt_type=prompt_type,
                version=str(version),
                description=meta.get("description", ""),
                variables=tuple(meta.get("variables", [])),
                role=meta.get("role", "system"),
            )

    def _discover_versions(self, prompt_type: PromptType, type_dir: Path) -> None:
        versions = sorted(
            p.stem.lstrip("v")
            for p in type_dir.glob("v*.j2")
        )
        if not versions:
            return
        self._defaults[prompt_type] = versions[-1]
        for ver in versions:
            self._catalog[prompt_type][ver] = PromptTemplateMeta(
                prompt_type=prompt_type,
                version=ver,
                description=f"Auto-discovered v{ver}",
            )

    def get_default_version(self, prompt_type: PromptType) -> str:
        return self._defaults.get(prompt_type, "1")

    def get_meta(self, prompt_type: PromptType, version: str) -> PromptTemplateMeta:
        versions = self._catalog.get(prompt_type, {})
        if version not in versions:
            available = ", ".join(sorted(versions)) or "none"
            raise KeyError(
                f"Template {prompt_type.value}@v{version} not found. "
                f"Available: {available}"
            )
        return versions[version]

    def list_versions(self, prompt_type: PromptType) -> list[PromptTemplateMeta]:
        return sorted(
            self._catalog.get(prompt_type, {}).values(),
            key=lambda m: m.version,
        )

    def list_types(self) -> list[PromptType]:
        return [t for t in PromptType if t in self._catalog]

    def template_path(
        self, prompt_type: PromptType, version: str | None = None
    ) -> Path:
        ver = version or self.get_default_version(prompt_type)
        path = self._dir / prompt_type.value / f"v{ver}.j2"
        if not path.exists():
            raise FileNotFoundError(f"Template file not found: {path}")
        return path
