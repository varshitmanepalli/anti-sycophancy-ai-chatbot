"""MemoryExtractionParser unit tests."""

import pytest

from app.domain.memory_extraction import MemoryCategory
from app.services.memory.parser import MemoryExtractionParser


@pytest.fixture
def parser() -> MemoryExtractionParser:
    return MemoryExtractionParser()


SAMPLE_JSON = """
{
  "career": [
    {"content": "software engineer at a fintech startup", "confidence": 0.95}
  ],
  "programming_language": [
    {"content": "Python", "confidence": 0.9},
    {"content": "TypeScript", "confidence": 0.85}
  ],
  "goals": [
    {"content": "learn Rust for systems programming", "confidence": 0.85}
  ],
  "preferences": [
    {"content": "prefers concise direct answers", "topic": "communication", "confidence": 0.8}
  ],
  "projects": [
    {"content": "building an anti-sycophancy chatbot", "confidence": 0.9}
  ],
  "summary": "Extracted career, languages, goal, preference, and project."
}
"""


class TestMemoryExtractionParser:
    def test_parse_all_categories(self, parser: MemoryExtractionParser):
        result = parser.parse(SAMPLE_JSON)
        assert len(result.career) == 1
        assert len(result.programming_language) == 2
        assert len(result.goals) == 1
        assert len(result.preferences) == 1
        assert len(result.projects) == 1
        assert result.total_items == 6

    def test_parse_preference_topic(self, parser: MemoryExtractionParser):
        result = parser.parse(SAMPLE_JSON)
        assert result.preferences[0].topic == "communication"

    def test_parse_summary(self, parser: MemoryExtractionParser):
        result = parser.parse(SAMPLE_JSON)
        assert "Extracted career" in result.summary

    def test_parse_fenced_json(self, parser: MemoryExtractionParser):
        raw = f"```json\n{SAMPLE_JSON}\n```"
        result = parser.parse(raw)
        assert result.total_items == 6

    def test_parse_string_items(self, parser: MemoryExtractionParser):
        raw = '{"career": ["Backend developer"], "programming_language": []}'
        result = parser.parse(raw)
        assert result.career[0].content == "Backend developer"
        assert result.career[0].category == MemoryCategory.CAREER

    def test_parse_empty_on_invalid(self, parser: MemoryExtractionParser):
        result = parser.parse("not json")
        assert result.is_empty

    def test_to_dict(self, parser: MemoryExtractionParser):
        result = parser.parse(SAMPLE_JSON)
        data = result.to_dict()
        assert "programming_language" in data
        assert len(data["projects"]) == 1
