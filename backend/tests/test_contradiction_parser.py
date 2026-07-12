"""ContradictionCheckParser unit tests."""

import pytest

from app.domain.memory import ContradictionSeverity, MemorySourceType
from app.services.contradictions.parser import ContradictionCheckParser


@pytest.fixture
def parser() -> ContradictionCheckParser:
    return ContradictionCheckParser()


SAMPLE_JSON = """
{
  "contradictions": [
    {
      "memory_statement": "User works as a backend developer",
      "new_statement": "I just started as a frontend developer",
      "memory_source": "fact",
      "memory_source_id": "550e8400-e29b-41d4-a716-446655440000",
      "description": "Role changed from backend to frontend; neither may be current.",
      "severity": "high",
      "clarification_question": "Has your role changed from backend to frontend, or are you working in both areas now?",
      "confidence": 0.9
    }
  ],
  "clarification_question": "Has your role changed from backend to frontend, or are you working in both areas now?",
  "summary": "One career contradiction detected."
}
"""


class TestContradictionCheckParser:
    def test_parse_contradiction(self, parser: ContradictionCheckParser):
        result = parser.parse(SAMPLE_JSON)
        assert len(result.contradictions) == 1
        item = result.contradictions[0]
        assert item.memory_statement.startswith("User works")
        assert item.new_statement.startswith("I just started")
        assert item.severity == ContradictionSeverity.HIGH
        assert item.memory_source == MemorySourceType.FACT

    def test_parse_clarification_question(self, parser: ContradictionCheckParser):
        result = parser.parse(SAMPLE_JSON)
        assert "role changed" in result.clarification_question.lower()

    def test_parse_source_id(self, parser: ContradictionCheckParser):
        result = parser.parse(SAMPLE_JSON)
        assert result.contradictions[0].memory_source_id == "550e8400-e29b-41d4-a716-446655440000"

    def test_parse_fenced_json(self, parser: ContradictionCheckParser):
        raw = f"```json\n{SAMPLE_JSON}\n```"
        result = parser.parse(raw)
        assert len(result.contradictions) == 1

    def test_parse_empty_on_invalid(self, parser: ContradictionCheckParser):
        result = parser.parse("not json")
        assert not result.has_contradictions

    def test_generates_default_clarification(self, parser: ContradictionCheckParser):
        raw = '{"contradictions": [{"memory_statement": "a", "new_statement": "b", "description": "x"}]}'
        result = parser.parse(raw)
        assert result.contradictions[0].clarification_question

    def test_to_dict(self, parser: ContradictionCheckParser):
        result = parser.parse(SAMPLE_JSON)
        data = result.to_dict()
        assert "clarification_question" in data
        assert len(data["contradictions"]) == 1
