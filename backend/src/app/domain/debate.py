"""Domain types for the multi-agent debate pipeline."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class DebateStage(StrEnum):
    """Ordered stages in the debate pipeline."""

    SUPPORT_AGENT = "support_agent"
    OPPONENT = "opponent"
    FACT_CHECKER = "fact_checker"
    JUDGE = "judge"


DEBATE_STAGE_ORDER: tuple[DebateStage, ...] = tuple(DebateStage)


DEFAULT_SCORING_RUBRIC = (
    "Evidence quality and citation of verifiable facts; "
    "logical coherence and absence of fallacies; "
    "calibration and acknowledgment of uncertainty; "
    "direct relevance to the user's question"
)


@dataclass
class DebateStageResult:
    """Output from a single debate stage."""

    stage: DebateStage
    output: str
    duration_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage.value,
            "output": self.output,
            "duration_ms": round(self.duration_ms, 2),
        }


@dataclass
class JudgedItem:
    """A single categorized item in the judge's verdict."""

    text: str
    source: str | None = None
    confidence: float = 0.5

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "text": self.text,
            "confidence": round(self.confidence, 4),
        }
        if self.source is not None:
            result["source"] = self.source
        return result


@dataclass
class JudgeVerdict:
    """Structured verdict parsed from the Judge Agent."""

    facts: list[JudgedItem] = field(default_factory=list)
    assumptions: list[JudgedItem] = field(default_factory=list)
    evidence: list[JudgedItem] = field(default_factory=list)
    unknowns: list[JudgedItem] = field(default_factory=list)
    final_conclusion: str = ""
    confidence: float = 0.5
    raw_output: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "facts": [item.to_dict() for item in self.facts],
            "assumptions": [item.to_dict() for item in self.assumptions],
            "evidence": [item.to_dict() for item in self.evidence],
            "unknowns": [item.to_dict() for item in self.unknowns],
            "final_conclusion": self.final_conclusion,
            "confidence": round(self.confidence, 4),
        }

    @property
    def verdict(self) -> str:
        """Alias for backward compatibility."""
        return self.final_conclusion


@dataclass
class DebateResult:
    """Complete output from the debate pipeline."""

    user_message: str
    support_argument: str = ""
    opponent_argument: str = ""
    fact_check_report: str = ""
    verdict: JudgeVerdict | None = None
    stages: list[DebateStageResult] = field(default_factory=list)
    total_duration_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_message": self.user_message,
            "support_argument": self.support_argument,
            "opponent_argument": self.opponent_argument,
            "fact_check_report": self.fact_check_report,
            "verdict": self.verdict.to_dict() if self.verdict else None,
            "stages": [s.to_dict() for s in self.stages],
            "total_duration_ms": round(self.total_duration_ms, 2),
        }

    @property
    def final_verdict(self) -> str:
        if self.verdict is not None:
            return self.verdict.verdict
        return ""
