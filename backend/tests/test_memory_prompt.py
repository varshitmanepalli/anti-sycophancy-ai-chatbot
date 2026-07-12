"""Memory extractor prompt tests."""

from app.prompts.manager import PromptManager
from app.prompts.types import PromptType


def test_v1_prompt_renders():
    pm = PromptManager()
    text = pm.render(
        PromptType.MEMORY_EXTRACTOR,
        variables={
            "message": "I'm a Python developer working on an AI chatbot.",
            "context": "",
        },
    )
    assert "Python developer" in text
    assert "career" in text
    assert "programming_language" in text
    assert "goals" in text
    assert "preferences" in text
    assert "projects" in text
    assert "Do NOT extract" in text


def test_default_version_is_v1():
    pm = PromptManager()
    assert pm.get_version(PromptType.MEMORY_EXTRACTOR) == "1"
