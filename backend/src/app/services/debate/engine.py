"""DebateEngine — multi-agent reasoning pipeline.

Pipeline::

    Support Agent → Opponent Agent → Fact Checker → Judge

Each stage uses the same ``ModelManager`` LLM and receives output from
the previous stage. All stages run asynchronously via ``async/await``.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from app.config.settings import Settings
from app.domain.debate import (
    DebateResult,
    DebateStage,
    DebateStageResult,
)
from app.models.base import GenerationConfig
from app.models.model_manager import ModelManager
from app.prompts.manager import PromptManager
from app.prompts.types import PromptType
from app.services.debate.judge_parser import JudgeVerdictParser
from app.services.debate.opponent_parser import OpponentAgentParser
from app.services.debate.support_parser import SupportAgentParser
from app.logging.setup import get_logger

logger = get_logger(__name__)

_JUDGE_VERSION = "4"
_SUPPORT_VERSION = "2"
_OPPONENT_VERSION = "2"


@dataclass
class DebateContext:
    """Mutable state passed through each debate stage."""

    user_message: str
    user_facts: list[str] = field(default_factory=list)
    conversation_summary: str = ""
    conversation_memory: str = ""
    known_facts: list[str] = field(default_factory=list)

    support_argument: str = ""
    opponent_argument: str = ""
    fact_check_report: str = ""
    stages: list[DebateStageResult] = field(default_factory=list)
    total_duration_ms: float = 0.0


class DebateEngine:
    """Orchestrate the four-stage debate pipeline on a single LLM."""

    def __init__(
        self,
        model_manager: ModelManager,
        settings: Settings,
        prompt_manager: PromptManager | None = None,
        judge_parser: JudgeVerdictParser | None = None,
        support_parser: SupportAgentParser | None = None,
        opponent_parser: OpponentAgentParser | None = None,
    ) -> None:
        self._model = model_manager
        self._settings = settings
        self._prompts = prompt_manager or PromptManager()
        self._judge_parser = judge_parser or JudgeVerdictParser()
        self._support_parser = support_parser or SupportAgentParser()
        self._opponent_parser = opponent_parser or OpponentAgentParser()

    async def run(
        self,
        message: str,
        *,
        user_facts: list[str] | None = None,
        conversation_summary: str = "",
        conversation_memory: str = "",
        known_facts: list[str] | None = None,
    ) -> DebateResult:
        """Execute the full debate pipeline and return structured results."""
        ctx = DebateContext(
            user_message=message,
            user_facts=list(user_facts or []),
            conversation_summary=conversation_summary,
            conversation_memory=conversation_memory,
            known_facts=list(known_facts or []),
        )

        pipeline_start = time.perf_counter()

        if not self._model.is_loaded:
            await self._model.load()

        ctx = await self.run_support(ctx)
        ctx = await self.run_opponent(ctx)
        ctx = await self.run_fact_checker(ctx)
        ctx = await self.run_judge(ctx)

        ctx.total_duration_ms = (time.perf_counter() - pipeline_start) * 1000

        verdict = None
        judge_stage = next(
            (s for s in ctx.stages if s.stage == DebateStage.JUDGE),
            None,
        )
        if judge_stage is not None:
            verdict = self._judge_parser.parse(judge_stage.output)

        result = DebateResult(
            user_message=ctx.user_message,
            support_argument=ctx.support_argument,
            opponent_argument=ctx.opponent_argument,
            fact_check_report=ctx.fact_check_report,
            verdict=verdict,
            stages=ctx.stages,
            total_duration_ms=ctx.total_duration_ms,
        )

        logger.info(
            "Debate complete: stages=%d total_ms=%.0f",
            len(result.stages),
            result.total_duration_ms,
        )
        return result

    async def run_support(self, ctx: DebateContext) -> DebateContext:
        """Stage 1 — find all arguments supporting the user's position."""
        raw_output, duration_ms = await self._run_stage(
            DebateStage.SUPPORT_AGENT,
            PromptType.SUPPORT_AGENT,
            version=_SUPPORT_VERSION,
            variables={
                "user_message": ctx.user_message,
                "user_facts": ctx.user_facts,
                "conversation_summary": ctx.conversation_summary,
                "known_facts": ctx.known_facts,
            },
        )
        parsed = self._support_parser.parse(raw_output)
        ctx.support_argument = parsed.to_argument_text() or raw_output
        ctx.stages.append(
            DebateStageResult(
                stage=DebateStage.SUPPORT_AGENT,
                output=raw_output,
                duration_ms=duration_ms,
            )
        )
        return ctx

    async def run_opponent(self, ctx: DebateContext) -> DebateContext:
        """Stage 2 — find weaknesses, alternatives, and logical gaps."""
        raw_output, duration_ms = await self._run_stage(
            DebateStage.OPPONENT,
            PromptType.OPPONENT,
            version=_OPPONENT_VERSION,
            variables={
                "user_message": ctx.user_message,
                "support_argument": ctx.support_argument,
                "user_facts": ctx.user_facts,
                "conversation_summary": ctx.conversation_summary,
                "known_facts": ctx.known_facts,
            },
        )
        parsed = self._opponent_parser.parse(raw_output)
        ctx.opponent_argument = parsed.to_argument_text() or raw_output
        ctx.stages.append(
            DebateStageResult(
                stage=DebateStage.OPPONENT,
                output=raw_output,
                duration_ms=duration_ms,
            )
        )
        return ctx

    async def run_fact_checker(self, ctx: DebateContext) -> DebateContext:
        """Stage 3 — verify factual claims from both prior arguments."""
        claim = self._build_fact_check_claim(ctx)
        context = self._build_fact_check_context(ctx)

        output, duration_ms = await self._run_stage(
            DebateStage.FACT_CHECKER,
            PromptType.FACT_CHECKER,
            variables={
                "claim": claim,
                "context": context,
                "known_facts": ctx.known_facts,
            },
        )
        ctx.fact_check_report = output
        ctx.stages.append(
            DebateStageResult(
                stage=DebateStage.FACT_CHECKER,
                output=output,
                duration_ms=duration_ms,
            )
        )
        return ctx

    async def run_judge(self, ctx: DebateContext) -> DebateContext:
        """Stage 4 — synthesize all inputs and deliver a structured verdict."""
        output, duration_ms = await self._run_stage(
            DebateStage.JUDGE,
            PromptType.JUDGE,
            version=_JUDGE_VERSION,
            variables={
                "user_message": ctx.user_message,
                "support_argument": ctx.support_argument,
                "opponent_argument": ctx.opponent_argument,
                "fact_check_report": ctx.fact_check_report,
                "conversation_memory": self._build_conversation_memory(ctx),
            },
            max_tokens=self._settings.debate_judge_max_tokens,
            temperature=self._settings.debate_judge_temperature,
        )
        ctx.stages.append(
            DebateStageResult(
                stage=DebateStage.JUDGE,
                output=output,
                duration_ms=duration_ms,
            )
        )
        return ctx

    async def _run_stage(
        self,
        stage: DebateStage,
        prompt_type: PromptType,
        *,
        variables: dict[str, Any],
        version: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> tuple[str, float]:
        start = time.perf_counter()
        output = await self._generate(
            prompt_type,
            version=version,
            variables=variables,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        duration_ms = (time.perf_counter() - start) * 1000
        logger.debug(
            "Debate[%s] completed in %.0fms output_len=%d",
            stage.value,
            duration_ms,
            len(output),
        )
        return output, duration_ms

    async def _generate(
        self,
        prompt_type: PromptType,
        *,
        version: str | None = None,
        variables: dict[str, Any],
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        messages = self._prompts.to_chat_format(
            prompt_type,
            version=version,
            variables=variables,
        )

        return await self._model.generate(
            messages,
            GenerationConfig(
                max_tokens=max_tokens or self._settings.debate_max_tokens,
                temperature=(
                    temperature
                    if temperature is not None
                    else self._settings.debate_temperature
                ),
            ),
        )

    @staticmethod
    def _build_fact_check_claim(ctx: DebateContext) -> str:
        parts = [
            "Support Agent argument:",
            ctx.support_argument,
            "",
            "Opponent Agent argument:",
            ctx.opponent_argument,
        ]
        return "\n".join(parts).strip()

    @staticmethod
    def _build_fact_check_context(ctx: DebateContext) -> str:
        parts = [f"User question: {ctx.user_message}"]
        if ctx.conversation_summary:
            parts.append(f"Conversation: {ctx.conversation_summary}")
        parts.append(
            "Verify factual assertions in both arguments above. "
            "Prior stage was the Opponent Agent rebuttal."
        )
        return "\n".join(parts)

    @staticmethod
    def _build_conversation_memory(ctx: DebateContext) -> str:
        if ctx.conversation_memory.strip():
            return ctx.conversation_memory.strip()

        parts: list[str] = []
        if ctx.conversation_summary:
            parts.append(f"Conversation summary:\n{ctx.conversation_summary}")

        if ctx.user_facts:
            parts.append("User facts:")
            parts.extend(f"- {fact}" for fact in ctx.user_facts)

        if ctx.known_facts:
            parts.append("Known external facts:")
            parts.extend(f"- {fact}" for fact in ctx.known_facts)

        if not parts:
            return "No prior conversation memory available."

        return "\n".join(parts)
