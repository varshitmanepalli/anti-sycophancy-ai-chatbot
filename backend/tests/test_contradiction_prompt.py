"""Contradiction detector prompt tests."""

from app.prompts.manager import PromptManager
from app.prompts.types import PromptType


def test_v1_prompt_renders():
    pm = PromptManager()
    text = pm.render(
        PromptType.CONTRADICTION_DETECTOR,
        variables={
            "message": "I switched to frontend development.",
            "memory_context": "Stored facts:\n- [career] backend developer",
        },
    )
    assert "frontend development" in text
    assert "backend developer" in text
    assert "contradictions" in text
    assert "clarification_question" in text
    assert "Do NOT assume the new statement is correct" in text


def test_default_version_is_v1():
    pm = PromptManager()
    assert pm.get_version(PromptType.CONTRADICTION_DETECTOR) == "1"
