"""JudgeVerdictParser unit tests."""

import pytest

from app.services.debate.judge_parser import JudgeVerdictParser


@pytest.fixture
def parser() -> JudgeVerdictParser:
    return JudgeVerdictParser()


SAMPLE_JSON = """
{
  "facts": [
    {
      "text": "Hybrid policies are common in the industry",
      "source": "memory",
      "confidence": 0.9
    }
  ],
  "assumptions": [
    {
      "text": "Remote work improves productivity for all roles",
      "source": "support",
      "confidence": 0.6
    }
  ],
  "evidence": [
    {
      "text": "Fact checker disputed productivity claims",
      "source": "fact_checker",
      "confidence": 0.85
    }
  ],
  "unknowns": [
    {
      "text": "Team collaboration requirements for this user",
      "source": null,
      "confidence": 0.5
    }
  ],
  "final_conclusion": "Remote work has trade-offs; neither side is universally correct.",
  "confidence": 0.81
}
"""


class TestJudgeVerdictParser:
    def test_parse_all_categories(self, parser: JudgeVerdictParser):
        result = parser.parse(SAMPLE_JSON)
        assert len(result.facts) == 1
        assert len(result.assumptions) == 1
        assert len(result.evidence) == 1
        assert len(result.unknowns) == 1
        assert "trade-offs" in result.final_conclusion
        assert result.confidence == 0.81

    def test_parse_item_source(self, parser: JudgeVerdictParser):
        result = parser.parse(SAMPLE_JSON)
        assert result.facts[0].source == "memory"
        assert result.evidence[0].source == "fact_checker"

    def test_verdict_alias(self, parser: JudgeVerdictParser):
        result = parser.parse(SAMPLE_JSON)
        assert result.verdict == result.final_conclusion

    def test_parse_fenced_json(self, parser: JudgeVerdictParser):
        raw = f"```json\n{SAMPLE_JSON}\n```"
        result = parser.parse(raw)
        assert result.confidence == 0.81

    def test_parse_fallback_on_plain_text(self, parser: JudgeVerdictParser):
        result = parser.parse("The opponent presented stronger evidence overall.")
        assert "opponent" in result.final_conclusion.lower()

    def test_parse_string_items(self, parser: JudgeVerdictParser):
        raw = '{"facts": ["Simple fact"], "final_conclusion": "Answer"}'
        result = parser.parse(raw)
        assert result.facts[0].text == "Simple fact"

    def test_clamps_confidence(self, parser: JudgeVerdictParser):
        raw = '{"facts": [{"text": "x", "confidence": 2.0}], "final_conclusion": "y", "confidence": 1.5}'
        result = parser.parse(raw)
        assert result.facts[0].confidence == 1.0
        assert result.confidence == 1.0

    def test_to_dict(self, parser: JudgeVerdictParser):
        result = parser.parse(SAMPLE_JSON)
        data = result.to_dict()
        assert "facts" in data
        assert "final_conclusion" in data
        assert data["confidence"] == 0.81
