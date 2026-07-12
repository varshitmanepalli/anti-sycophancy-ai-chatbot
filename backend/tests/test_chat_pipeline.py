"""POST /chat pipeline endpoint tests."""

from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_chat_pipeline, get_db
from app.domain.assumptions import AssumptionDetectionResult, DetectedIssue
from app.domain.claims import ClaimExtractionResult, ExtractedItem
from app.domain.confidence import ConfidenceResult, DimensionScore
from app.main import create_app
from app.services.chat_pipeline.pipeline import ChatPipeline
from app.domain.fallacies import DetectedFallacy, FallacyDetectionResult, FallacyType
from app.services.classification.classifier import InputClassifier
from app.services.confidence.engine import ConfidenceEngine
from app.config.settings import Settings


@pytest.fixture
async def pipeline_client(mock_db_session):
    """Client with mocked chat pipeline (no LLM calls)."""
    mock_extractor = AsyncMock()
    mock_extractor.extract = AsyncMock(
        return_value=ClaimExtractionResult(
            main_claims=[ExtractedItem(text="User seeks trust evaluation", confidence=0.8)],
        )
    )
    mock_assumption_detector = AsyncMock()
    mock_assumption_detector.detect = AsyncMock(
        return_value=AssumptionDetectionResult(
            mind_reading=[DetectedIssue(text="Assumes plan is untrustworthy", confidence=0.7)],
            summary="Mind reading detected.",
        )
    )
    mock_fallacy_detector = AsyncMock()
    mock_fallacy_detector.detect = AsyncMock(
        return_value=FallacyDetectionResult(
            fallacies=[
                DetectedFallacy(
                    fallacy=FallacyType.FALSE_DILEMMA,
                    confidence=0.75,
                    explanation="Presents trust as binary.",
                )
            ],
            summary="False dilemma detected.",
        )
    )
    mock_confidence_engine = AsyncMock()
    mock_confidence_engine.score = AsyncMock(
        return_value=ConfidenceResult(
            evidence_quality=DimensionScore(score=60, explanation="Limited evidence."),
            reasoning_strength=DimensionScore(score=55, explanation="Some gaps."),
            source_reliability=DimensionScore(score=40, explanation="Weak sources."),
            uncertainty=DimensionScore(score=70, explanation="Many unknowns."),
            confidence=52,
            explanation="Low-moderate confidence due to unknowns.",
        )
    )
    classifier = InputClassifier(settings=Settings(classifier_mode="rules"))
    pipeline = ChatPipeline(
        classifier=classifier,
        claim_extractor=mock_extractor,
        assumption_detector=mock_assumption_detector,
        fallacy_detector=mock_fallacy_detector,
        confidence_engine=mock_confidence_engine,
    )

    app = create_app()

    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_chat_pipeline] = lambda: pipeline

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_chat_pipeline_returns_skeleton(pipeline_client: AsyncClient):
    response = await pipeline_client.post(
        "/api/chat",
        json={
            "user_id": "user-123",
            "conversation_id": "conv-456",
            "message": "Should I trust this plan?",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["response"] == ""
    assert data["confidence"] == 0.52
    assert data["category"] is not None
    assert len(data["reasoning_steps"]) >= 5
    labels = [s["label"] for s in data["reasoning_steps"]]
    assert "input_classification" in labels
    assert "claim_extraction" in labels
    assert "assumption_detection" in labels
    assert "fallacy_detection" in labels
    assert "confidence_scoring" in labels


@pytest.mark.asyncio
async def test_chat_pipeline_requires_message(pipeline_client: AsyncClient):
    response = await pipeline_client.post(
        "/api/chat",
        json={"user_id": "user-123", "conversation_id": "conv-456", "message": ""},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_chat_pipeline_accepts_empty_ids(pipeline_client: AsyncClient):
    response = await pipeline_client.post(
        "/api/chat",
        json={"user_id": "", "conversation_id": "", "message": "Hello"},
    )

    assert response.status_code == 200
    assert response.json()["response"] == ""
