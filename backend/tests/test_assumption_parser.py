"""AssumptionDetectionParser unit tests."""

import pytest

from app.services.assumptions.parser import AssumptionDetectionParser


@pytest.fixture
def parser() -> AssumptionDetectionParser:
    return AssumptionDetectionParser()


SAMPLE_JSON = """
{
  "unsupported_assumptions": [
    {
      "text": "Assumes all managers dislike remote work",
      "confidence": 0.85,
      "quote": "every manager hates remote work",
      "severity": "high"
    }
  ],
  "emotional_reasoning": [
    {
      "text": "Conclusion based on frustration rather than data",
      "confidence": 0.9,
      "quote": "I feel like they're punishing us",
      "severity": "medium"
    }
  ],
  "confirmation_bias": [
    {
      "text": "Only cites studies supporting remote work",
      "confidence": 0.75,
      "quote": null,
      "severity": "medium"
    }
  ],
  "mind_reading": [
    {
      "text": "Claims to know management's hidden motives",
      "confidence": 0.8,
      "quote": "they just want control",
      "severity": "high"
    }
  ],
  "overconfidence": [
    {
      "text": "Absolute certainty about future policy",
      "confidence": 0.7,
      "quote": "they will never allow it again",
      "severity": "medium"
    }
  ],
  "summary": "The message relies on emotional reasoning and mind reading."
}
"""


class TestAssumptionDetectionParser:
    def test_parse_all_categories(self, parser: AssumptionDetectionParser):
        result = parser.parse(SAMPLE_JSON)
        assert len(result.unsupported_assumptions) == 1
        assert len(result.emotional_reasoning) == 1
        assert len(result.confirmation_bias) == 1
        assert len(result.mind_reading) == 1
        assert len(result.overconfidence) == 1
        assert result.total_issues == 5

    def test_parse_summary(self, parser: AssumptionDetectionParser):
        result = parser.parse(SAMPLE_JSON)
        assert "emotional reasoning" in result.summary

    def test_parse_severity_and_quote(self, parser: AssumptionDetectionParser):
        result = parser.parse(SAMPLE_JSON)
        issue = result.unsupported_assumptions[0]
        assert issue.severity == "high"
        assert issue.quote == "every manager hates remote work"

    def test_parse_fenced_json(self, parser: AssumptionDetectionParser):
        raw = f"```json\n{SAMPLE_JSON}\n```"
        result = parser.parse(raw)
        assert result.total_issues == 5

    def test_parse_string_items(self, parser: AssumptionDetectionParser):
        raw = '{"unsupported_assumptions": ["Simple assumption"], "emotional_reasoning": []}'
        result = parser.parse(raw)
        assert result.unsupported_assumptions[0].text == "Simple assumption"

    def test_parse_empty_on_invalid(self, parser: AssumptionDetectionParser):
        result = parser.parse("not json")
        assert result.is_empty

    def test_to_dict(self, parser: AssumptionDetectionParser):
        result = parser.parse(SAMPLE_JSON)
        data = result.to_dict()
        assert "unsupported_assumptions" in data
        assert "mind_reading" in data
        assert "summary" in data

    def test_invalid_severity_ignored(self, parser: AssumptionDetectionParser):
        raw = '{"unsupported_assumptions": [{"text": "test", "severity": "critical"}]}'
        result = parser.parse(raw)
        assert result.unsupported_assumptions[0].severity is None
