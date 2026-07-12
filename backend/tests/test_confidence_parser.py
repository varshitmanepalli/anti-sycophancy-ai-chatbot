"""ConfidenceScoreParser unit tests."""

import pytest

from app.services.confidence.parser import ConfidenceScoreParser


@pytest.fixture
def parser() -> ConfidenceScoreParser:
    return ConfidenceScoreParser()


SAMPLE_JSON = """
{
  "evidence_quality": {
    "score": 72,
    "explanation": "Some supporting facts cited but no primary sources."
  },
  "reasoning_strength": {
    "score": 65,
    "explanation": "Logical structure is sound but contains a false dilemma."
  },
  "source_reliability": {
    "score": 40,
    "explanation": "Sources are anecdotal and unverified."
  },
  "uncertainty": {
    "score": 55,
    "explanation": "Key variables about team context are unknown."
  },
  "confidence": 58,
  "explanation": "Moderate confidence due to weak sources and unresolved unknowns."
}
"""


class TestConfidenceScoreParser:
    def test_parse_all_dimensions(self, parser: ConfidenceScoreParser):
        result = parser.parse(SAMPLE_JSON)
        assert result.evidence_quality.score == 72
        assert result.reasoning_strength.score == 65
        assert result.source_reliability.score == 40
        assert result.uncertainty.score == 55
        assert result.confidence == 58

    def test_parse_explanations(self, parser: ConfidenceScoreParser):
        result = parser.parse(SAMPLE_JSON)
        assert "primary sources" in result.evidence_quality.explanation
        assert "Moderate confidence" in result.explanation

    def test_parse_fenced_json(self, parser: ConfidenceScoreParser):
        raw = f"```json\n{SAMPLE_JSON}\n```"
        result = parser.parse(raw)
        assert result.confidence == 58

    def test_parse_empty_on_invalid(self, parser: ConfidenceScoreParser):
        result = parser.parse("not json")
        assert result.confidence == 50

    def test_clamps_scores(self, parser: ConfidenceScoreParser):
        raw = '{"evidence_quality": {"score": 150, "explanation": "x"}, "confidence": -5, "explanation": "y"}'
        result = parser.parse(raw)
        assert result.evidence_quality.score == 100
        assert result.confidence == 0

    def test_normalized_confidence(self, parser: ConfidenceScoreParser):
        result = parser.parse(SAMPLE_JSON)
        assert result.normalized_confidence == 0.58

    def test_to_dict(self, parser: ConfidenceScoreParser):
        result = parser.parse(SAMPLE_JSON)
        data = result.to_dict()
        assert data["confidence"] == 58
        assert "evidence_quality" in data
