"""Opposition Agent prompt tests."""

from app.prompts.manager import PromptManager
from app.prompts.types import PromptType


def test_v2_prompt_renders():
    pm = PromptManager()
    text = pm.render(
        PromptType.OPPONENT,
        version="2",
        variables={
            "user_message": "Remote work is better for everyone.",
            "support_argument": "It saves commute time and improves focus.",
            "user_facts": ["Software engineer"],
            "conversation_summary": "Career discussion",
            "known_facts": ["Company offers hybrid policy"],
        },
    )
    assert "Remote work is better" in text
    assert "saves commute time" in text
    assert "weaknesses" in text
    assert "alternative_explanations" in text
    assert "challenged_assumptions" in text
    assert "logical_gaps" in text
    assert "Never insult" in text


def test_default_version_is_v2():
    pm = PromptManager()
    assert pm.get_version(PromptType.OPPONENT) == "2"


def test_v2_listed_in_versions():
    pm = PromptManager()
    versions = [m.version for m in pm.list_versions(PromptType.OPPONENT)]
    assert "1" in versions
    assert "2" in versions
