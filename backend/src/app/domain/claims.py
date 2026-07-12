"""Domain types for claim extraction."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExtractedItem:
    """A single extracted claim, assumption, evidence item, or gap."""

    text: str
    confidence: float = 1.0
    source: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"text": self.text, "confidence": round(self.confidence, 4)}
        if self.source is not None:
            result["source"] = self.source
        return result


@dataclass
class ClaimExtractionResult:
    """Structured output from the claim extractor."""

    main_claims: list[ExtractedItem] = field(default_factory=list)
    supporting_claims: list[ExtractedItem] = field(default_factory=list)
    hidden_assumptions: list[ExtractedItem] = field(default_factory=list)
    evidence_provided: list[ExtractedItem] = field(default_factory=list)
    unknown_information: list[ExtractedItem] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "main_claims": [c.to_dict() for c in self.main_claims],
            "supporting_claims": [c.to_dict() for c in self.supporting_claims],
            "hidden_assumptions": [c.to_dict() for c in self.hidden_assumptions],
            "evidence_provided": [c.to_dict() for c in self.evidence_provided],
            "unknown_information": [c.to_dict() for c in self.unknown_information],
        }

    @property
    def is_empty(self) -> bool:
        return not any(
            [
                self.main_claims,
                self.supporting_claims,
                self.hidden_assumptions,
                self.evidence_provided,
                self.unknown_information,
            ]
        )
