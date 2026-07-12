"""DebateEngine unit tests."""

from unittest.mock import AsyncMock

import pytest

from app.config.settings import Settings
from app.domain.debate import DebateStage
from app.prompts.manager import PromptManager
from app.services.debate.engine import DebateEngine

SUPPORT_OUTPUT = """
{
  "arguments": [
    {
      "text": "Remote work improves focus and reduces commute time",
      "evidence": "User asked whether remote work is better",
      "source": "user_message",
      "confidence": 0.8
    }
  ],
  "position_summary": "User favors remote work.",
  "summary": "One supporting argument found.",
  "missing_information": []
}
"""
OPPONENT_OUTPUT = """
{
  "weaknesses": [
    {
      "text": "Remote work harms collaboration and mentorship",
      "target": "Remote work improves focus",
      "confidence": 0.8
    }
  ],
  "alternative_explanations": [],
  "challenged_assumptions": [],
  "logical_gaps": [],
  "summary": "Collaboration concerns weaken the support case.",
  "missing_information": []
}
"""
FACT_CHECK_OUTPUT = (
    "- Productivity claim: disputed (mixed studies)\n"
    "- Collaboration claim: verified (meta-analyses show decline)"
)
JUDGE_OUTPUT = """
{
  "facts": [
    {"text": "User asked about remote work", "source": "memory", "confidence": 0.9}
  ],
  "assumptions": [],
  "evidence": [
    {"text": "Productivity claim disputed by fact checker", "source": "fact_checker", "confidence": 0.8}
  ],
  "unknowns": [
    {"text": "Role-specific collaboration needs", "source": null, "confidence": 0.5}
  ],
  "final_conclusion": "Remote work benefits vary by role and team culture.",
  "confidence": 0.78
}
"""


@pytest.fixture
def mock_model():
    manager = AsyncMock()
    manager.is_loaded = True
    manager.generate = AsyncMock(
        side_effect=[SUPPORT_OUTPUT, OPPONENT_OUTPUT, FACT_CHECK_OUTPUT, JUDGE_OUTPUT]
    )
    return manager


@pytest.fixture
def engine(mock_model) -> DebateEngine:
    return DebateEngine(
        model_manager=mock_model,
        settings=Settings(),
        prompt_manager=PromptManager(),
    )


class TestDebateEngine:
    @pytest.mark.asyncio
    async def test_run_executes_all_stages(self, engine: DebateEngine, mock_model):
        result = await engine.run("Is remote work better?")

        assert len(result.stages) == 4
        assert [s.stage for s in result.stages] == list(DebateStage)
        assert "Remote work improves focus" in result.support_argument
        assert "Remote work harms collaboration" in result.opponent_argument
        assert result.fact_check_report == FACT_CHECK_OUTPUT
        assert mock_model.generate.await_count == 4

    @pytest.mark.asyncio
    async def test_run_parses_judge_verdict(self, engine: DebateEngine):
        result = await engine.run("Is remote work better?")

        assert result.verdict is not None
        assert "vary by role" in result.verdict.final_conclusion
        assert result.verdict.confidence == 0.78
        assert len(result.verdict.evidence) == 1

    @pytest.mark.asyncio
    async def test_stages_receive_previous_output(self, engine: DebateEngine, mock_model):
        await engine.run(
            "Is remote work better?",
            user_facts=["Works in software"],
            known_facts=["Hybrid policies are common"],
        )

        calls = mock_model.generate.await_args_list
        assert len(calls) == 4

        # Opponent prompt includes formatted support output
        opponent_messages = calls[1].args[0]
        assert "Remote work improves focus" in opponent_messages[0]["content"]

        # Fact checker includes both prior arguments
        fact_check_messages = calls[2].args[0]
        assert "Remote work improves focus" in fact_check_messages[0]["content"]
        assert "Remote work harms collaboration" in fact_check_messages[0]["content"]

        # Judge includes fact check report
        judge_messages = calls[3].args[0]
        assert FACT_CHECK_OUTPUT in judge_messages[0]["content"]
        assert "Works in software" in judge_messages[0]["content"]

    @pytest.mark.asyncio
    async def test_loads_model_if_needed(self, mock_model):
        mock_model.is_loaded = False
        mock_model.load = AsyncMock()
        engine = DebateEngine(model_manager=mock_model, settings=Settings())
        await engine.run("test")
        mock_model.load.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_records_timing(self, engine: DebateEngine):
        result = await engine.run("Is remote work better?")
        assert result.total_duration_ms >= 0
        assert all(s.duration_ms >= 0 for s in result.stages)

    @pytest.mark.asyncio
    async def test_individual_stages(self, engine: DebateEngine, mock_model):
        from app.services.debate.engine import DebateContext

        ctx = DebateContext(user_message="Is remote work better?")
        ctx = await engine.run_support(ctx)
        assert "Remote work improves focus" in ctx.support_argument

        ctx = await engine.run_opponent(ctx)
        assert "Remote work harms collaboration" in ctx.opponent_argument

        ctx = await engine.run_fact_checker(ctx)
        assert ctx.fact_check_report == FACT_CHECK_OUTPUT

        ctx = await engine.run_judge(ctx)
        assert ctx.stages[-1].stage == DebateStage.JUDGE
