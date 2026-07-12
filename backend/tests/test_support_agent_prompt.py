"""Support Agent prompt tests."""

from app.prompts.manager import PromptManager
from app.prompts.types import PromptType


def test_v2_prompt_renders():
    pm = PromptManager()
    text = pm.render(
        PromptType.SUPPORT_AGENT,
        version="2",
        variables={
            "user_message": "I think remote work is better because I commute 2 hours daily.",
            "user_facts": ["Software engineer", "6 months savings"],
            "conversation_summary": "Career discussion",
            "known_facts": ["Company offers hybrid policy"],
        },
    )
    assert "commute 2 hours daily" in text
    assert "Software engineer" in text
    assert "hybrid policy" in text
    assert "arguments" in text
    assert "Do NOT invent" in text
    assert "missing_information" in text


def test_default_version_is_v2():
    pm = PromptManager()
    assert pm.get_version(PromptType.SUPPORT_AGENT) == "2"


def test_v2_listed_in_versions():
    pm = PromptManager()
    versions = [m.version for m in pm.list_versions(PromptType.SUPPORT_AGENT)]
    assert "1" in versions
    assert "2" in versions
