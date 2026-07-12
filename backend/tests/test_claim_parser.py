"""ClaimExtractionParser unit tests."""

import pytest

from app.services.claims.parser import ClaimExtractionParser


@pytest.fixture
def parser() -> ClaimExtractionParser:
    return ClaimExtractionParser()


SAMPLE_JSON = """
{
  "main_claims": [
    {"text": "Remote work increases productivity", "confidence": 0.9}
  ],
  "supporting_claims": [
    {"text": "Employees save commute time", "confidence": 0.85}
  ],
  "hidden_assumptions": [
    {"text": "Productivity is the primary measure of work value", "confidence": 0.7}
  ],
  "evidence_provided": [
    {"text": "A 2023 Stanford study showed 13% productivity gain", "confidence": 0.95, "source": "Stanford study"}
  ],
  "unknown_information": [
    {"text": "Whether results generalize beyond tech workers", "confidence": 0.8}
  ]
}
"""


class TestClaimExtractionParser:
    def test_parse_clean_json(self, parser: ClaimExtractionParser):
        result = parser.parse(SAMPLE_JSON)
        assert len(result.main_claims) == 1
        assert result.main_claims[0].text == "Remote work increases productivity"
        assert result.main_claims[0].confidence == 0.9

    def test_parse_markdown_fenced_json(self, parser: ClaimExtractionParser):
        raw = f"```json\n{SAMPLE_JSON}\n```"
        result = parser.parse(raw)
        assert len(result.supporting_claims) == 1
        assert len(result.hidden_assumptions) == 1

    def test_parse_evidence_with_source(self, parser: ClaimExtractionParser):
        result = parser.parse(SAMPLE_JSON)
        assert result.evidence_provided[0].source == "Stanford study"

    def test_parse_string_items(self, parser: ClaimExtractionParser):
        raw = '{"main_claims": ["Simple claim text"], "supporting_claims": []}'
        result = parser.parse(raw)
        assert result.main_claims[0].text == "Simple claim text"

    def test_parse_empty_json(self, parser: ClaimExtractionParser):
        result = parser.parse("not json at all")
        assert result.is_empty

    def test_parse_clamps_confidence(self, parser: ClaimExtractionParser):
        raw = '{"main_claims": [{"text": "test", "confidence": 5.0}]}'
        result = parser.parse(raw)
        assert result.main_claims[0].confidence == 1.0

    def test_to_dict(self, parser: ClaimExtractionParser):
        result = parser.parse(SAMPLE_JSON)
        data = result.to_dict()
        assert "main_claims" in data
        assert "unknown_information" in data
        assert isinstance(data["main_claims"], list)

    def test_normalize_directly(self, parser: ClaimExtractionParser):
        data = {
            "main_claims": [{"text": "Claim A", "confidence": 0.8}],
            "supporting_claims": [],
            "hidden_assumptions": [],
            "evidence_provided": [],
            "unknown_information": [],
        }
        result = parser.normalize(data)
        assert len(result.main_claims) == 1

    def test_skips_empty_text_items(self, parser: ClaimExtractionParser):
        raw = '{"main_claims": [{"text": ""}, {"text": "valid"}], "supporting_claims": []}'
        result = parser.parse(raw)
        assert len(result.main_claims) == 1
        assert result.main_claims[0].text == "valid"
