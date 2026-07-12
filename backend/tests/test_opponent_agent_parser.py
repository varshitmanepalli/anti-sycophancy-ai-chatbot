"""OpponentAgentParser unit tests."""

import pytest

from app.services.debate.opponent_parser import OpponentAgentParser


@pytest.fixture
def parser() -> OpponentAgentParser:
    return OpponentAgentParser()


SAMPLE_JSON = """
{
  "weaknesses": [
    {
      "text": "Productivity claim lacks supporting data",
      "target": "Remote work improves focus",
      "confidence": 0.85
    }
  ],
  "alternative_explanations": [
    {
      "text": "Commute reduction may explain satisfaction, not productivity",
      "evidence": "User asked about remote work generally",
      "confidence": 0.7
    }
  ],
  "challenged_assumptions": [
    {
      "text": "Assumes remote work applies equally to all roles",
      "quote": "remote work is better",
      "confidence": 0.8
    }
  ],
  "logical_gaps": [
    {
      "text": "Conclusion does not follow from a single personal preference",
      "gap_type": "non_sequitur",
      "confidence": 0.75
    }
  ],
  "summary": "The case relies on untested assumptions about productivity.",
  "missing_information": [
    "No team collaboration requirements specified"
  ]
}
"""


class TestOpponentAgentParser:
    def test_parse_all_categories(self, parser: OpponentAgentParser):
        result = parser.parse(SAMPLE_JSON)
        assert len(result.weaknesses) == 1
        assert len(result.alternative_explanations) == 1
        assert len(result.challenged_assumptions) == 1
        assert len(result.logical_gaps) == 1
        assert result.total_issues == 4

    def test_parse_weakness_target(self, parser: OpponentAgentParser):
        result = parser.parse(SAMPLE_JSON)
        assert result.weaknesses[0].target == "Remote work improves focus"

    def test_parse_logical_gap_type(self, parser: OpponentAgentParser):
        result = parser.parse(SAMPLE_JSON)
        assert result.logical_gaps[0].gap_type == "non_sequitur"

    def test_parse_summary(self, parser: OpponentAgentParser):
        result = parser.parse(SAMPLE_JSON)
        assert "untested assumptions" in result.summary

    def test_parse_fenced_json(self, parser: OpponentAgentParser):
        raw = f"```json\n{SAMPLE_JSON}\n```"
        result = parser.parse(raw)
        assert result.total_issues == 4

    def test_parse_string_items(self, parser: OpponentAgentParser):
        raw = '{"weaknesses": ["Simple weakness"], "alternative_explanations": []}'
        result = parser.parse(raw)
        assert result.weaknesses[0].text == "Simple weakness"

    def test_parse_empty_on_invalid(self, parser: OpponentAgentParser):
        result = parser.parse("not json")
        assert result.is_empty

    def test_invalid_gap_type_defaults_to_other(self, parser: OpponentAgentParser):
        raw = '{"logical_gaps": [{"text": "gap", "gap_type": "invalid"}]}'
        result = parser.parse(raw)
        assert result.logical_gaps[0].gap_type == "other"

    def test_to_argument_text(self, parser: OpponentAgentParser):
        result = parser.parse(SAMPLE_JSON)
        text = result.to_argument_text()
        assert "Weaknesses:" in text
        assert "Alternative explanations:" in text
        assert "Challenged assumptions:" in text
        assert "Logical gaps:" in text
        assert "non_sequitur" in text

    def test_to_dict(self, parser: OpponentAgentParser):
        result = parser.parse(SAMPLE_JSON)
        data = result.to_dict()
        assert "weaknesses" in data
        assert "logical_gaps" in data
