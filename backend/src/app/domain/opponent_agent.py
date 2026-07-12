"""Domain types for Opposition Agent structured output."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Weakness:
    """A weakness in the user's or support agent's reasoning."""

    text: str
    target: str | None = None
    confidence: float = 0.5

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "text": self.text,
            "confidence": round(self.confidence, 4),
        }
        if self.target is not None:
            result["target"] = self.target
        return result


@dataclass
class AlternativeExplanation:
    """An alternative explanation for the same observations."""

    text: str
    evidence: str | None = None
    confidence: float = 0.5

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "text": self.text,
            "confidence": round(self.confidence, 4),
        }
        if self.evidence is not None:
            result["evidence"] = self.evidence
        return result


@dataclass
class ChallengedAssumption:
    """An assumption being challenged."""

    text: str
    quote: str | None = None
    confidence: float = 0.5

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "text": self.text,
            "confidence": round(self.confidence, 4),
        }
        if self.quote is not None:
            result["quote"] = self.quote
        return result


@dataclass
class LogicalGap:
    """A gap or flaw in the chain of reasoning."""

    text: str
    gap_type: str | None = None
    confidence: float = 0.5

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "text": self.text,
            "confidence": round(self.confidence, 4),
        }
        if self.gap_type is not None:
            result["gap_type"] = self.gap_type
        return result


@dataclass
class OpponentAgentResult:
    """Structured output from the Opposition Agent."""

    weaknesses: list[Weakness] = field(default_factory=list)
    alternative_explanations: list[AlternativeExplanation] = field(default_factory=list)
    challenged_assumptions: list[ChallengedAssumption] = field(default_factory=list)
    logical_gaps: list[LogicalGap] = field(default_factory=list)
    summary: str = ""
    missing_information: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "weaknesses": [w.to_dict() for w in self.weaknesses],
            "alternative_explanations": [a.to_dict() for a in self.alternative_explanations],
            "challenged_assumptions": [a.to_dict() for a in self.challenged_assumptions],
            "logical_gaps": [g.to_dict() for g in self.logical_gaps],
            "summary": self.summary,
            "missing_information": self.missing_information,
        }

    @property
    def is_empty(self) -> bool:
        return not any(
            (
                self.weaknesses,
                self.alternative_explanations,
                self.challenged_assumptions,
                self.logical_gaps,
                self.summary,
            )
        )

    @property
    def total_issues(self) -> int:
        return (
            len(self.weaknesses)
            + len(self.alternative_explanations)
            + len(self.challenged_assumptions)
            + len(self.logical_gaps)
        )

    def to_argument_text(self) -> str:
        """Format structured output as prose for downstream debate stages."""
        if self.is_empty:
            return self.summary or ""

        lines: list[str] = []

        if self.weaknesses:
            lines.append("Weaknesses:")
            for index, item in enumerate(self.weaknesses, start=1):
                target = f" (targets: {item.target})" if item.target else ""
                lines.append(f"{index}. {item.text}{target}")

        if self.alternative_explanations:
            lines.append("")
            lines.append("Alternative explanations:")
            for index, item in enumerate(self.alternative_explanations, start=1):
                lines.append(f"{index}. {item.text}")
                if item.evidence:
                    lines.append(f"   Evidence: {item.evidence}")

        if self.challenged_assumptions:
            lines.append("")
            lines.append("Challenged assumptions:")
            for index, item in enumerate(self.challenged_assumptions, start=1):
                quote = f' — "{item.quote}"' if item.quote else ""
                lines.append(f"{index}. {item.text}{quote}")

        if self.logical_gaps:
            lines.append("")
            lines.append("Logical gaps:")
            for index, item in enumerate(self.logical_gaps, start=1):
                gap_type = f" [{item.gap_type}]" if item.gap_type else ""
                lines.append(f"{index}. {item.text}{gap_type}")

        if self.missing_information:
            lines.append("")
            lines.append("Information needed for stronger rebuttal:")
            for item in self.missing_information:
                lines.append(f"- {item}")

        return "\n".join(lines).strip()
