"""Debate engine API schemas."""

from pydantic import BaseModel, Field

from app.domain.debate import DebateStage


class DebateRequest(BaseModel):
    """Request to run the full debate pipeline."""

    message: str = Field(..., min_length=1, max_length=32_000)
    user_facts: list[str] = Field(default_factory=list)
    conversation_summary: str = ""
    conversation_memory: str = ""
    known_facts: list[str] = Field(default_factory=list)


class DebateStageResultSchema(BaseModel):
    """Single stage output in API responses."""

    stage: DebateStage
    output: str
    duration_ms: float = 0.0


class JudgedItemSchema(BaseModel):
    """A categorized item in the judge's verdict."""

    text: str
    source: str | None = None
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class JudgeVerdictSchema(BaseModel):
    """Structured judge verdict."""

    facts: list[JudgedItemSchema] = Field(default_factory=list)
    assumptions: list[JudgedItemSchema] = Field(default_factory=list)
    evidence: list[JudgedItemSchema] = Field(default_factory=list)
    unknowns: list[JudgedItemSchema] = Field(default_factory=list)
    final_conclusion: str = ""
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class DebateResponse(BaseModel):
    """Complete debate pipeline response."""

    user_message: str
    support_argument: str = ""
    opponent_argument: str = ""
    fact_check_report: str = ""
    verdict: JudgeVerdictSchema | None = None
    stages: list[DebateStageResultSchema] = Field(default_factory=list)
    total_duration_ms: float = 0.0

    @classmethod
    def from_domain(cls, result) -> "DebateResponse":
        verdict = None
        if result.verdict is not None:
            v = result.verdict
            verdict = JudgeVerdictSchema(
                facts=[
                    JudgedItemSchema(text=i.text, source=i.source, confidence=i.confidence)
                    for i in v.facts
                ],
                assumptions=[
                    JudgedItemSchema(text=i.text, source=i.source, confidence=i.confidence)
                    for i in v.assumptions
                ],
                evidence=[
                    JudgedItemSchema(text=i.text, source=i.source, confidence=i.confidence)
                    for i in v.evidence
                ],
                unknowns=[
                    JudgedItemSchema(text=i.text, source=i.source, confidence=i.confidence)
                    for i in v.unknowns
                ],
                final_conclusion=v.final_conclusion,
                confidence=v.confidence,
            )
        return cls(
            user_message=result.user_message,
            support_argument=result.support_argument,
            opponent_argument=result.opponent_argument,
            fact_check_report=result.fact_check_report,
            verdict=verdict,
            stages=[
                DebateStageResultSchema(
                    stage=s.stage,
                    output=s.output,
                    duration_ms=s.duration_ms,
                )
                for s in result.stages
            ],
            total_duration_ms=result.total_duration_ms,
        )
