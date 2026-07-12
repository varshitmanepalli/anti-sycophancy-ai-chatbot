"""SupportAgentParser unit tests."""

import pytest

from app.services.debate.support_parser import SupportAgentParser


@pytest.fixture
def parser() -> SupportAgentParser:
    return SupportAgentParser()


SAMPLE_JSON = """
{
  "arguments": [
    {
      "text": "Remote work eliminates a long daily commute",
      "evidence": "User spends 2 hours commuting each day",
      "source": "user_message",
      "confidence": 0.95
    },
    {
      "text": "Savings provide a financial buffer during transition",
      "evidence": "Has savings for 6 months",
      "source": "user_facts",
      "confidence": 0.9
    },
    {
      "text": "Focus may improve without office distractions",
      "evidence": null,
      "source": "inference",
      "confidence": 0.55
    }
  ],
  "position_summary": "User believes remote work is better for their situation.",
  "summary": "Found 3 supporting arguments from available information.",
  "missing_information": [
    "No data on team collaboration requirements"
  ]
}
"""


class TestSupportAgentParser:
    def test_parse_arguments(self, parser: SupportAgentParser):
        result = parser.parse(SAMPLE_JSON)
        assert len(result.arguments) == 3
        assert result.arguments[0].text.startswith("Remote work")
        assert result.arguments[0].source == "user_message"
        assert result.arguments[2].evidence is None

    def test_parse_summary_fields(self, parser: SupportAgentParser):
        result = parser.parse(SAMPLE_JSON)
        assert "remote work" in result.position_summary.lower()
        assert "3 supporting" in result.summary
        assert len(result.missing_information) == 1

    def test_parse_fenced_json(self, parser: SupportAgentParser):
        raw = f"```json\n{SAMPLE_JSON}\n```"
        result = parser.parse(raw)
        assert len(result.arguments) == 3

    def test_parse_string_arguments(self, parser: SupportAgentParser):
        raw = '{"arguments": ["Simple supporting point"], "position_summary": "x"}'
        result = parser.parse(raw)
        assert result.arguments[0].text == "Simple supporting point"

    def test_parse_empty_on_invalid(self, parser: SupportAgentParser):
        result = parser.parse("not json")
        assert result.is_empty

    def test_clamps_confidence(self, parser: SupportAgentParser):
        raw = '{"arguments": [{"text": "x", "confidence": 2.0}]}'
        result = parser.parse(raw)
        assert result.arguments[0].confidence == 1.0

    def test_to_argument_text(self, parser: SupportAgentParser):
        result = parser.parse(SAMPLE_JSON)
        text = result.to_argument_text()
        assert "Remote work eliminates" in text
        assert "Evidence:" in text
        assert "Information not available" in text

    def test_to_dict(self, parser: SupportAgentParser):
        result = parser.parse(SAMPLE_JSON)
        data = result.to_dict()
        assert len(data["arguments"]) == 3
        assert "missing_information" in data
