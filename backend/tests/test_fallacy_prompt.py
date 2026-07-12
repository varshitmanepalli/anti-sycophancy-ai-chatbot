"""Fallacy detector prompt tests."""

from app.prompts.manager import PromptManager
from app.prompts.types import PromptType


def test_v1_prompt_renders():
    pm = PromptManager()
    text = pm.render(
        PromptType.FALLACY_DETECTOR,
        variables={
            "message": "Everyone knows that if we allow this, society will collapse.",
            "context": "Policy debate",
        },
    )
    assert "Everyone knows that if we allow this" in text
    assert "hasty_generalization" in text
    assert "false_dilemma" in text
    assert "slippery_slope" in text
    assert "appeal_to_emotion" in text
    assert "appeal_to_popularity" in text
    assert "circular_reasoning" in text
    assert "confirmation_bias" in text
    assert "post_hoc" in text


def test_default_version_is_v1():
    pm = PromptManager()
    assert pm.get_version(PromptType.FALLACY_DETECTOR) == "1"


def test_v1_listed_in_versions():
    pm = PromptManager()
    versions = [m.version for m in pm.list_versions(PromptType.FALLACY_DETECTOR)]
    assert "1" in versions
