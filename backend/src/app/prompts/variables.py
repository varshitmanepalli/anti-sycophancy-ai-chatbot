"""Default template variables per prompt type."""

from typing import Any

from app.prompts.types import PromptType

DEFAULT_VARIABLES: dict[PromptType, dict[str, Any]] = {
    PromptType.SYSTEM: {
        "assistant_name": "Reasoning Engine",
        "tone": "direct and honest",
    },
    PromptType.SUPPORT_AGENT: {
        "user_message": "",
        "user_facts": [],
        "conversation_summary": "",
        "known_facts": [],
    },
    PromptType.OPPONENT: {
        "user_message": "",
        "support_argument": "",
        "user_facts": [],
        "conversation_summary": "",
        "known_facts": [],
    },
    PromptType.JUDGE: {
        "user_message": "",
        "support_argument": "",
        "opponent_argument": "",
        "fact_check_report": "",
        "conversation_memory": "",
        "scoring_rubric": (
            "Evidence quality and citation of verifiable facts; "
            "logical coherence and absence of fallacies; "
            "calibration and acknowledgment of uncertainty; "
            "direct relevance to the user's question"
        ),
    },
    PromptType.FACT_CHECKER: {
        "claim": "",
        "context": "",
        "known_facts": [],
    },
    PromptType.ASSUMPTION_DETECTOR: {
        "statement": "",
        "context": "",
        "message": "",
    },
    PromptType.INPUT_CLASSIFIER: {
        "message": "",
        "categories": "",
    },
    PromptType.CLAIM_EXTRACTOR: {
        "message": "",
        "context": "",
    },
    PromptType.FALLACY_DETECTOR: {
        "message": "",
        "context": "",
    },
    PromptType.CONFIDENCE_SCORER: {
        "message": "",
        "context": "",
        "response": "",
    },
    PromptType.MEMORY_EXTRACTOR: {
        "message": "",
        "context": "",
    },
    PromptType.CONTRADICTION_DETECTOR: {
        "message": "",
        "memory_context": "",
    },
}


def merge_variables(
    prompt_type: PromptType,
    overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return default variables merged with caller overrides."""
    base = dict(DEFAULT_VARIABLES.get(prompt_type, {}))
    if overrides:
        base.update(overrides)
    return base
