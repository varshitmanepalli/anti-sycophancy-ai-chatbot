"""Prompt type definitions and template metadata."""

from dataclasses import dataclass, field
from enum import StrEnum


class PromptType(StrEnum):
    """Supported prompt template categories."""

    SYSTEM = "system"
    SUPPORT_AGENT = "support_agent"
    OPPONENT = "opponent"
    JUDGE = "judge"
    FACT_CHECKER = "fact_checker"
    ASSUMPTION_DETECTOR = "assumption_detector"
    INPUT_CLASSIFIER = "input_classifier"
    CLAIM_EXTRACTOR = "claim_extractor"
    FALLACY_DETECTOR = "fallacy_detector"
    CONFIDENCE_SCORER = "confidence_scorer"
    MEMORY_EXTRACTOR = "memory_extractor"
    CONTRADICTION_DETECTOR = "contradiction_detector"


@dataclass(frozen=True)
class PromptTemplateMeta:
    """Metadata for a single versioned template."""

    prompt_type: PromptType
    version: str
    description: str
    variables: tuple[str, ...] = field(default_factory=tuple)
    role: str = "system"

    @property
    def template_id(self) -> str:
        return f"{self.prompt_type.value}@v{self.version}"
