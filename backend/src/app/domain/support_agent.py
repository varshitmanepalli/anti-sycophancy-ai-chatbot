"""Domain types for Support Agent structured output."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SupportingArgument:
    """A single argument in favor of the user's position."""

    text: str
    evidence: str | None = None
    source: str | None = None
    confidence: float = 0.5

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "text": self.text,
            "confidence": round(self.confidence, 4),
        }
        if self.evidence is not None:
            result["evidence"] = self.evidence
        if self.source is not None:
            result["source"] = self.source
        return result


@dataclass
class SupportAgentResult:
    """Structured output from the Support Agent."""

    arguments: list[SupportingArgument] = field(default_factory=list)
    position_summary: str = ""
    summary: str = ""
    missing_information: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "arguments": [a.to_dict() for a in self.arguments],
            "position_summary": self.position_summary,
            "summary": self.summary,
            "missing_information": self.missing_information,
        }

    @property
    def is_empty(self) -> bool:
        return not self.arguments and not self.position_summary

    def to_argument_text(self) -> str:
        """Format structured output as prose for downstream debate stages."""
        if self.is_empty:
            return self.summary or ""

        lines: list[str] = []
        if self.position_summary:
            lines.append(self.position_summary)
            lines.append("")

        for index, argument in enumerate(self.arguments, start=1):
            lines.append(f"{index}. {argument.text}")
            if argument.evidence:
                source = f" (source: {argument.source})" if argument.source else ""
                lines.append(f"   Evidence: {argument.evidence}{source}")

        if self.missing_information:
            lines.append("")
            lines.append("Information not available to support further arguments:")
            for item in self.missing_information:
                lines.append(f"- {item}")

        return "\n".join(lines).strip()
