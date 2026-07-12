"""Parse confidence scoring JSON from LLM output."""

import json
import re
from typing import Any

from app.domain.confidence import ConfidenceResult, DimensionScore
from app.logging.setup import get_logger

logger = get_logger(__name__)

_DIMENSION_KEYS = (
    "evidence_quality",
    "reasoning_strength",
    "source_reliability",
    "uncertainty",
)


class ConfidenceScoreParser:
    """Parse raw LLM text into a validated ``ConfidenceResult``."""

    def parse(self, raw: str) -> ConfidenceResult:
        data = self.extract_json(raw)
        return self.normalize(data)

    @staticmethod
    def extract_json(raw: str) -> dict[str, Any]:
        text = raw.strip()
        fence_match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
        if fence_match:
            text = fence_match.group(1).strip()

        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

        brace_match = re.search(r"\{.*\}", text, re.DOTALL)
        if brace_match:
            try:
                parsed = json.loads(brace_match.group())
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError as exc:
                logger.warning("Failed to parse confidence JSON: %s", exc)

        logger.warning("No valid JSON found in confidence scoring output")
        return {}

    def normalize(self, data: dict[str, Any]) -> ConfidenceResult:
        dimensions = {
            key: self._parse_dimension(data.get(key, {}), key)
            for key in _DIMENSION_KEYS
        }

        confidence = self._clamp_score(data.get("confidence", 50))
        explanation = str(data.get("explanation", "")).strip()
        if not explanation:
            explanation = self._build_fallback_explanation(dimensions, confidence)

        return ConfidenceResult(
            evidence_quality=dimensions["evidence_quality"],
            reasoning_strength=dimensions["reasoning_strength"],
            source_reliability=dimensions["source_reliability"],
            uncertainty=dimensions["uncertainty"],
            confidence=confidence,
            explanation=explanation,
        )

    def _parse_dimension(self, item: Any, key: str) -> DimensionScore:
        if isinstance(item, dict):
            score = self._clamp_score(item.get("score", 50))
            explanation = str(item.get("explanation", "")).strip()
            if not explanation:
                explanation = f"No explanation provided for {key.replace('_', ' ')}."
            return DimensionScore(score=score, explanation=explanation)

        if isinstance(item, (int, float)):
            return DimensionScore(
                score=self._clamp_score(item),
                explanation=f"Score provided without explanation for {key.replace('_', ' ')}.",
            )

        return DimensionScore(
            score=50,
            explanation=f"Unable to parse {key.replace('_', ' ')} from model output.",
        )

    @staticmethod
    def _build_fallback_explanation(
        dimensions: dict[str, DimensionScore],
        confidence: int,
    ) -> str:
        return (
            f"Overall confidence {confidence}/100 based on evidence quality "
            f"({dimensions['evidence_quality'].score}), reasoning strength "
            f"({dimensions['reasoning_strength'].score}), source reliability "
            f"({dimensions['source_reliability'].score}), and uncertainty "
            f"({dimensions['uncertainty'].score})."
        )

    @staticmethod
    def _clamp_score(value: Any) -> int:
        try:
            score = int(round(float(value)))
        except (TypeError, ValueError):
            return 50
        return max(0, min(100, score))

    @staticmethod
    def empty() -> ConfidenceResult:
        unknown = DimensionScore(score=50, explanation="Unable to score.")
        return ConfidenceResult(
            evidence_quality=unknown,
            reasoning_strength=unknown,
            source_reliability=unknown,
            uncertainty=unknown,
            confidence=50,
            explanation="Confidence scoring failed to produce valid output.",
        )
