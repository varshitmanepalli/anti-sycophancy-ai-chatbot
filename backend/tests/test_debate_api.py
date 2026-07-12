"""POST /debate endpoint tests."""

from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_db, get_debate_engine
from app.domain.debate import (
    DebateResult,
    DebateStage,
    DebateStageResult,
    JudgedItem,
    JudgeVerdict,
)
from app.main import create_app
from app.services.debate.engine import DebateEngine


@pytest.fixture
async def debate_client(mock_db_session):
    mock_engine = AsyncMock(spec=DebateEngine)
    mock_engine.run = AsyncMock(
        return_value=DebateResult(
            user_message="Is remote work better?",
            support_argument="Productivity gains.",
            opponent_argument="Collaboration suffers.",
            fact_check_report="Mixed evidence.",
            verdict=JudgeVerdict(
                facts=[JudgedItem(text="Hybrid policies exist", source="memory", confidence=0.9)],
                assumptions=[JudgedItem(text="Productivity always improves", source="support")],
                evidence=[JudgedItem(text="Mixed productivity data", source="fact_checker")],
                unknowns=[JudgedItem(text="Team size unknown")],
                final_conclusion="It depends on the role.",
                confidence=0.7,
            ),
            stages=[
                DebateStageResult(stage=DebateStage.SUPPORT_AGENT, output="Productivity gains."),
                DebateStageResult(stage=DebateStage.OPPONENT, output="Collaboration suffers."),
                DebateStageResult(stage=DebateStage.FACT_CHECKER, output="Mixed evidence."),
                DebateStageResult(stage=DebateStage.JUDGE, output='{"final_conclusion": "It depends"}'),
            ],
            total_duration_ms=100.0,
        )
    )

    app = create_app()

    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_debate_engine] = lambda: mock_engine

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_debate_run_returns_full_pipeline(debate_client: AsyncClient):
    response = await debate_client.post(
        "/api/v1/debate/run",
        json={"message": "Is remote work better?"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user_message"] == "Is remote work better?"
    assert data["support_argument"] == "Productivity gains."
    assert data["opponent_argument"] == "Collaboration suffers."
    assert data["fact_check_report"] == "Mixed evidence."
    assert data["verdict"]["final_conclusion"] == "It depends on the role."
    assert len(data["verdict"]["facts"]) == 1
    assert len(data["verdict"]["assumptions"]) == 1
    assert len(data["stages"]) == 4


@pytest.mark.asyncio
async def test_debate_run_requires_message(debate_client: AsyncClient):
    response = await debate_client.post(
        "/api/v1/debate/run",
        json={"message": ""},
    )
    assert response.status_code == 422
