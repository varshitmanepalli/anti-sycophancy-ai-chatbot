"""FallacyDetectionParser unit tests."""

import pytest

from app.domain.fallacies import FallacyType
from app.services.fallacies.parser import FallacyDetectionParser


@pytest.fixture
def parser() -> FallacyDetectionParser:
    return FallacyDetectionParser()


SAMPLE_JSON = """
{
  "fallacies": [
    {
      "fallacy": "hasty_generalization",
      "confidence": 0.9,
      "explanation": "Concludes all politicians are corrupt from one scandal.",
      "quote": "they're all corrupt"
    },
    {
      "fallacy": "false_dilemma",
      "confidence": 0.85,
      "explanation": "Presents only two options when alternatives exist.",
      "quote": "either we ban it or society collapses"
    },
    {
      "fallacy": "slippery_slope",
      "confidence": 0.8,
      "explanation": "Claims a minor policy change leads inevitably to tyranny.",
      "quote": null
    },
    {
      "fallacy": "appeal_to_emotion",
      "confidence": 0.75,
      "explanation": "Uses fear instead of evidence.",
      "quote": "think of the children"
    },
    {
      "fallacy": "appeal_to_popularity",
      "confidence": 0.7,
      "explanation": "Argues something is true because everyone believes it.",
      "quote": "everyone knows"
    },
    {
      "fallacy": "circular_reasoning",
      "confidence": 0.88,
      "explanation": "The conclusion is assumed in the premise.",
      "quote": "it's true because it's correct"
    },
    {
      "fallacy": "confirmation_bias",
      "confidence": 0.82,
      "explanation": "Only cites evidence supporting a pre-existing view.",
      "quote": null
    },
    {
      "fallacy": "post_hoc",
      "confidence": 0.78,
      "explanation": "Assumes causation from temporal sequence alone.",
      "quote": "after the vaccine, he got sick"
    }
  ],
  "summary": "Multiple fallacies weaken the argument."
}
"""


class TestFallacyDetectionParser:
    def test_parse_all_fallacy_types(self, parser: FallacyDetectionParser):
        result = parser.parse(SAMPLE_JSON)
        assert len(result.fallacies) == 8
        types = {f.fallacy for f in result.fallacies}
        assert types == set(FallacyType)

    def test_parse_fields(self, parser: FallacyDetectionParser):
        result = parser.parse(SAMPLE_JSON)
        item = result.fallacies[0]
        assert item.fallacy == FallacyType.HASTY_GENERALIZATION
        assert item.confidence == 0.9
        assert "politicians" in item.explanation
        assert item.quote == "they're all corrupt"

    def test_parse_summary(self, parser: FallacyDetectionParser):
        result = parser.parse(SAMPLE_JSON)
        assert "Multiple fallacies" in result.summary

    def test_parse_fenced_json(self, parser: FallacyDetectionParser):
        raw = f"```json\n{SAMPLE_JSON}\n```"
        result = parser.parse(raw)
        assert len(result.fallacies) == 8

    def test_parse_bare_array(self, parser: FallacyDetectionParser):
        raw = '[{"fallacy": "post_hoc", "confidence": 0.6, "explanation": "Sequence implies cause."}]'
        result = parser.parse(raw)
        assert len(result.fallacies) == 1
        assert result.fallacies[0].fallacy == FallacyType.POST_HOC

    def test_parse_alias_labels(self, parser: FallacyDetectionParser):
        raw = '{"fallacies": [{"fallacy": "bandwagon", "confidence": 0.5, "explanation": "Popular so true."}]}'
        result = parser.parse(raw)
        assert result.fallacies[0].fallacy == FallacyType.APPEAL_TO_POPULARITY

    def test_parse_empty_on_invalid(self, parser: FallacyDetectionParser):
        result = parser.parse("not json")
        assert result.is_empty

    def test_skips_unknown_fallacy(self, parser: FallacyDetectionParser):
        raw = '{"fallacies": [{"fallacy": "ad_hominem", "confidence": 0.9, "explanation": "x"}]}'
        result = parser.parse(raw)
        assert len(result.fallacies) == 0

    def test_clamps_confidence(self, parser: FallacyDetectionParser):
        raw = '{"fallacies": [{"fallacy": "post_hoc", "confidence": 1.5, "explanation": "x"}]}'
        result = parser.parse(raw)
        assert result.fallacies[0].confidence == 1.0

    def test_to_dict(self, parser: FallacyDetectionParser):
        result = parser.parse(SAMPLE_JSON)
        data = result.to_dict()
        assert "fallacies" in data
        assert data["fallacies"][0]["fallacy_label"] == "Hasty Generalization"
