"""Tests for central prompts.yml configuration."""

from app.prompts.config_loader import (
    get_active_version,
    get_default_variables,
    get_template_content,
    load_prompts_config,
)
from app.prompts.types import PromptType


def test_prompts_yml_loads():
    config = load_prompts_config()
    assert "defaults" in config
    assert "active_versions" in config
    assert "templates" in config
    assert config["templates"]["system"]["1"]["content"]


def test_active_versions_from_yaml():
    assert get_active_version(PromptType.JUDGE) == "4"
    assert get_active_version(PromptType.SYSTEM) == "1"


def test_global_defaults_merged_for_system():
    defaults = get_default_variables(PromptType.SYSTEM)
    assert defaults["assistant_name"] == "Reasoning Engine"
    assert "reasoning_protocol" in defaults


def test_template_content_from_yaml():
    content = get_template_content(PromptType.SYSTEM, "1")
    assert content is not None
    assert "assistant_name" in content
    assert "critical thinking" in content
