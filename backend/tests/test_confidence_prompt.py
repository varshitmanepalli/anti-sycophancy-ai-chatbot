"""Confidence scorer prompt tests."""

from app.prompts.manager import PromptManager
from app.prompts.types import PromptType


def test_v1_prompt_renders():
    pm = PromptManager()
    text = pm.render(
        PromptType.CONFIDENCE_SCORER,
        variables={
            "message": "Studies show remote work improves productivity.",
            "context": "Claim extraction found one main claim.",
            "response": "",
        },
    )
    assert "Studies show remote work" in text
    assert "evidence_quality" in text
    assert "reasoning_strength" in text
    assert "source_reliability" in text
    assert "uncertainty" in text
    assert "confidence" in text


def test_default_version_is_v1():
    pm = PromptManager()
    assert pm.get_version(PromptType.CONFIDENCE_SCORER) == "1"
