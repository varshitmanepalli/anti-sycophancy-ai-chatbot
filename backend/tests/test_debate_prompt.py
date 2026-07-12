"""Judge Agent prompt tests."""

from app.prompts.manager import PromptManager
from app.prompts.types import PromptType


def test_v4_prompt_renders():
    pm = PromptManager()
    text = pm.render(
        PromptType.JUDGE,
        version="4",
        variables={
            "user_message": "Is remote work better?",
            "support_argument": "It saves commute time.",
            "opponent_argument": "Collaboration suffers.",
            "fact_check_report": "Productivity claim: disputed.",
            "conversation_memory": "User is a software engineer with hybrid policy.",
        },
    )
    assert "Is remote work better?" in text
    assert "saves commute time" in text
    assert "Collaboration suffers" in text
    assert "Productivity claim: disputed" in text
    assert "software engineer" in text
    assert "facts" in text
    assert "assumptions" in text
    assert "evidence" in text
    assert "unknowns" in text
    assert "final_conclusion" in text
    assert "Do NOT agree with the user" in text


def test_default_judge_version_is_v4():
    pm = PromptManager()
    assert pm.get_version(PromptType.JUDGE) == "4"
