"""Assumption detector prompt tests."""

from app.prompts.manager import PromptManager
from app.prompts.types import PromptType


def test_v2_prompt_renders():
    pm = PromptManager()
    text = pm.render(
        PromptType.ASSUMPTION_DETECTOR,
        version="2",
        variables={
            "message": "Everyone knows the policy is unfair.",
            "context": "Workplace discussion",
        },
    )
    assert "Everyone knows the policy is unfair." in text
    assert "unsupported_assumptions" in text
    assert "confirmation_bias" in text
    assert "mind_reading" in text
    assert "overconfidence" in text
    assert "emotional_reasoning" in text


def test_default_version_is_v2():
    pm = PromptManager()
    assert pm.get_version(PromptType.ASSUMPTION_DETECTOR) == "2"


def test_v2_listed_in_versions():
    pm = PromptManager()
    versions = [m.version for m in pm.list_versions(PromptType.ASSUMPTION_DETECTOR)]
    assert "1" in versions
    assert "2" in versions
