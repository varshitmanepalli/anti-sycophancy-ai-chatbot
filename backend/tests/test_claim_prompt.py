"""Claim extractor prompt tests."""

from app.prompts.manager import PromptManager
from app.prompts.types import PromptType


def test_claim_extractor_prompt_renders():
    pm = PromptManager()
    text = pm.render(
        PromptType.CLAIM_EXTRACTOR,
        variables={
            "message": "Remote work is better than office work.",
            "context": "Career advice thread",
        },
    )
    assert "Remote work is better than office work." in text
    assert "Career advice thread" in text
    assert "main_claims" in text
    assert "hidden_assumptions" in text
    assert "unknown_information" in text


def test_claim_extractor_listed_in_registry():
    pm = PromptManager()
    assert PromptType.CLAIM_EXTRACTOR in pm.list_types()
    versions = pm.list_versions(PromptType.CLAIM_EXTRACTOR)
    assert len(versions) >= 1
