"""PromptManager unit tests."""

import pytest

from app.prompts.manager import PromptManager
from app.prompts.types import PromptType


@pytest.fixture
def manager() -> PromptManager:
    return PromptManager()


def test_list_all_prompt_types(manager: PromptManager):
    types = manager.list_types()
    assert PromptType.SYSTEM in types
    assert PromptType.SUPPORT_AGENT in types
    assert PromptType.OPPONENT in types
    assert PromptType.JUDGE in types
    assert PromptType.FACT_CHECKER in types
    assert PromptType.ASSUMPTION_DETECTOR in types
    assert PromptType.INPUT_CLASSIFIER in types


def test_render_system_prompt_v1(manager: PromptManager):
    text = manager.render(
        PromptType.SYSTEM,
        version="1",
        variables={"assistant_name": "TestBot", "tone": "blunt"},
    )
    assert "TestBot" in text
    assert "blunt" in text
    assert "critical thinking" in text


def test_render_system_prompt_v2_requires_reasoning_protocol(manager: PromptManager):
    with pytest.raises(Exception):
        manager.render(PromptType.SYSTEM, version="2")

    text = manager.render(
        PromptType.SYSTEM,
        version="2",
        variables={
            "assistant_name": "TestBot",
            "tone": "direct",
            "reasoning_protocol": "Step-by-step analysis",
        },
    )
    assert "Step-by-step analysis" in text


def test_render_support_agent_with_facts(manager: PromptManager):
    text = manager.render(
        PromptType.SUPPORT_AGENT,
        variables={
            "user_message": "Should I quit my job?",
            "user_facts": ["Works in tech", "Has savings for 6 months"],
            "conversation_summary": "Career discussion",
        },
    )
    assert "Should I quit my job?" in text
    assert "Works in tech" in text
    assert "Career discussion" in text


def test_render_opponent_prompt(manager: PromptManager):
    text = manager.render(
        PromptType.OPPONENT,
        variables={
            "user_message": "Is remote work better?",
            "support_argument": "Remote work improves productivity.",
            "user_facts": [],
        },
    )
    assert "Remote work improves productivity" in text
    assert "weaknesses" in text
    assert "logical_gaps" in text


def test_render_judge_v2(manager: PromptManager):
    text = manager.render(
        PromptType.JUDGE,
        version="2",
        variables={
            "user_message": "Is AI dangerous?",
            "support_argument": "Yes, alignment is unsolved.",
            "opponent_argument": "Current systems are narrow and controllable.",
            "scoring_rubric": "Evidence quality, logical coherence, calibration",
        },
    )
    assert "support_score" in text
    assert "scoring rubric" in text.lower() or "Evidence quality" in text


def test_render_fact_checker(manager: PromptManager):
    text = manager.render(
        PromptType.FACT_CHECKER,
        variables={
            "claim": "Python was created in 1991",
            "context": "Programming language history",
            "known_facts": ["Guido van Rossum created Python"],
        },
    )
    assert "Python was created in 1991" in text
    assert "verified" in text


def test_render_assumption_detector(manager: PromptManager):
    text = manager.render(
        PromptType.ASSUMPTION_DETECTOR,
        version="1",
        variables={
            "statement": "Everyone should learn to code",
            "context": "Career advice discussion",
        },
    )
    assert "Everyone should learn to code" in text
    assert "assumption" in text.lower()


def test_version_pinning(manager: PromptManager):
    assert manager.get_version(PromptType.SYSTEM) == "1"

    manager.pin_version(PromptType.SYSTEM, "2")
    assert manager.get_version(PromptType.SYSTEM) == "2"

    manager.unpin(PromptType.SYSTEM)
    assert manager.get_version(PromptType.SYSTEM) == "1"


def test_list_versions(manager: PromptManager):
    versions = manager.list_versions(PromptType.SYSTEM)
    assert len(versions) == 2
    assert versions[0].version == "1"
    assert versions[1].version == "2"


def test_render_messages_format(manager: PromptManager):
    messages = manager.render_messages(PromptType.SYSTEM, version="1")
    assert len(messages) == 1
    assert messages[0].role == "system"
    assert len(messages[0].content) > 0


def test_to_chat_format(manager: PromptManager):
    chat = manager.to_chat_format(PromptType.JUDGE, version="1", variables={
        "user_message": "test",
        "support_argument": "pro",
        "opponent_argument": "con",
    })
    assert chat[0]["role"] == "system"
    assert "test" in chat[0]["content"]


def test_render_all(manager: PromptManager):
    rendered = manager.render_all({
        PromptType.SUPPORT_AGENT: {"user_message": "hello", "user_facts": [], "conversation_summary": ""},
        PromptType.OPPONENT: {"user_message": "hello", "support_argument": "arg", "user_facts": []},
    })
    assert len(rendered) == 12
    assert all(isinstance(v, str) for v in rendered.values())
