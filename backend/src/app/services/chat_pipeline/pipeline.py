"""Chat pipeline — staged processing skeleton.

Each step mutates a shared ``PipelineContext`` and passes it to the next
stage. Inference, confidence scoring, and reasoning extraction are stubbed
until implemented.
"""

from dataclasses import dataclass, field

from app.domain.assumptions import AssumptionDetectionResult
from app.domain.claims import ClaimExtractionResult
from app.domain.classification import InputCategory
from app.domain.confidence import ConfidenceResult
from app.domain.fallacies import FallacyDetectionResult
from app.schemas.chat_pipeline import (
    ChatPipelineRequest,
    ChatPipelineResponse,
    ReasoningItem,
    ReasoningStep,
    StructuredReasoning,
)
from app.services.assumptions.detector import AssumptionDetector
from app.services.fallacies.detector import LogicalFallacyDetector
from app.services.claims.extractor import ClaimExtractor
from app.services.classification.classifier import InputClassifier
from app.services.confidence.engine import ConfidenceEngine
from app.logging.setup import get_logger

logger = get_logger(__name__)


@dataclass
class PipelineContext:
    """Mutable state passed through every pipeline stage."""

    user_id: str
    conversation_id: str
    message: str
    history: list[dict[str, str]] = field(default_factory=list)
    prompt_messages: list[dict[str, str]] = field(default_factory=list)
    input_category: InputCategory | None = None
    classification_confidence: float = 0.0
    claims: ClaimExtractionResult | None = None
    assumptions: AssumptionDetectionResult | None = None
    fallacies: FallacyDetectionResult | None = None
    confidence_result: ConfidenceResult | None = None
    response: str = ""
    confidence: float = 0.0
    reasoning_steps: list[ReasoningStep] = field(default_factory=list)


class ChatPipeline:
    """Orchestrates the end-to-end chat processing stages."""

    def __init__(
        self,
        classifier: InputClassifier | None = None,
        claim_extractor: ClaimExtractor | None = None,
        assumption_detector: AssumptionDetector | None = None,
        fallacy_detector: LogicalFallacyDetector | None = None,
        confidence_engine: ConfidenceEngine | None = None,
    ) -> None:
        self._classifier = classifier
        self._claim_extractor = claim_extractor
        self._assumption_detector = assumption_detector
        self._fallacy_detector = fallacy_detector
        self._confidence_engine = confidence_engine

    async def run(self, request: ChatPipelineRequest) -> ChatPipelineResponse:
        """Execute all pipeline stages and return the structured response."""
        ctx = PipelineContext(
            user_id=request.user_id,
            conversation_id=request.conversation_id,
            message=request.message,
        )

        ctx = await self.load_context(ctx)
        ctx = await self.classify_input(ctx)
        ctx = await self.extract_claims(ctx)
        ctx = await self.detect_assumptions(ctx)
        ctx = await self.detect_fallacies(ctx)
        ctx = await self.build_prompt(ctx)
        ctx = await self.run_inference(ctx)
        ctx = await self.score_confidence(ctx)
        ctx = await self.extract_reasoning(ctx)

        return self.build_response(ctx)

    async def load_context(self, ctx: PipelineContext) -> PipelineContext:
        """Retrieve prior turns for the conversation."""
        logger.debug(
            "Pipeline[load_context] user=%s conversation=%s",
            ctx.user_id,
            ctx.conversation_id,
        )
        # TODO: load history from memory store / database
        ctx.history = []
        return ctx

    async def classify_input(self, ctx: PipelineContext) -> PipelineContext:
        """Classify the user message into a semantic category."""
        if self._classifier is None:
            return ctx

        result = await self._classifier.classify(ctx.message)
        ctx.input_category = result.category
        ctx.classification_confidence = result.confidence
        ctx.reasoning_steps.append(
            ReasoningStep(
                label="input_classification",
                content=(
                    f"category={result.category.value}, "
                    f"confidence={result.confidence:.2f}, "
                    f"method={result.method}"
                ),
            )
        )
        logger.debug(
            "Pipeline[classify_input] %s (%.2f)",
            result.category.value,
            result.confidence,
        )
        return ctx

    async def extract_claims(self, ctx: PipelineContext) -> PipelineContext:
        """Extract structured claims from the user message."""
        if self._claim_extractor is None:
            return ctx

        result = await self._claim_extractor.extract(ctx.message)
        ctx.claims = result
        ctx.reasoning_steps.append(
            ReasoningStep(
                label="claim_extraction",
                content=(
                    f"main={len(result.main_claims)}, "
                    f"supporting={len(result.supporting_claims)}, "
                    f"assumptions={len(result.hidden_assumptions)}, "
                    f"evidence={len(result.evidence_provided)}, "
                    f"unknowns={len(result.unknown_information)}"
                ),
            )
        )
        logger.debug("Pipeline[extract_claims] main_claims=%d", len(result.main_claims))
        return ctx

    async def detect_assumptions(self, ctx: PipelineContext) -> PipelineContext:
        """Detect reasoning flaws and cognitive biases in the user message."""
        if self._assumption_detector is None:
            return ctx

        result = await self._assumption_detector.detect(ctx.message)
        ctx.assumptions = result
        ctx.reasoning_steps.append(
            ReasoningStep(
                label="assumption_detection",
                content=(
                    f"issues={result.total_issues}, "
                    f"unsupported={len(result.unsupported_assumptions)}, "
                    f"emotional={len(result.emotional_reasoning)}, "
                    f"bias={len(result.confirmation_bias)}, "
                    f"mind_reading={len(result.mind_reading)}, "
                    f"overconfidence={len(result.overconfidence)}"
                ),
            )
        )
        logger.debug("Pipeline[detect_assumptions] total_issues=%d", result.total_issues)
        return ctx

    async def detect_fallacies(self, ctx: PipelineContext) -> PipelineContext:
        """Detect logical fallacies in the user message."""
        if self._fallacy_detector is None:
            return ctx

        result = await self._fallacy_detector.detect(ctx.message)
        ctx.fallacies = result
        ctx.reasoning_steps.append(
            ReasoningStep(
                label="fallacy_detection",
                content=(
                    f"fallacies={len(result.fallacies)}, "
                    f"types={sorted({f.fallacy.value for f in result.fallacies})}"
                ),
            )
        )
        logger.debug("Pipeline[detect_fallacies] count=%d", len(result.fallacies))
        return ctx

    async def build_prompt(self, ctx: PipelineContext) -> PipelineContext:
        """Assemble system prompt + history + user message."""
        logger.debug("Pipeline[build_prompt] message_len=%d", len(ctx.message))
        # TODO: use ConversationPrompt from app.prompts.anti_sycophancy
        ctx.prompt_messages = [
            {"role": "system", "content": "[placeholder] anti-sycophancy system prompt"},
            *ctx.history,
            {"role": "user", "content": ctx.message},
        ]
        return ctx

    async def run_inference(self, ctx: PipelineContext) -> PipelineContext:
        """Generate a model response from the assembled prompt."""
        logger.debug(
            "Pipeline[run_inference] prompt_messages=%d",
            len(ctx.prompt_messages),
        )
        # TODO: call ModelManager.generate(ctx.prompt_messages)
        ctx.response = ""
        return ctx

    async def score_confidence(self, ctx: PipelineContext) -> PipelineContext:
        """Score how confident the reasoning is in the message or response."""
        if self._confidence_engine is None:
            return ctx

        context = self._build_confidence_context(ctx)
        target = ctx.response.strip() or ctx.message
        result = await self._confidence_engine.score(
            target,
            context=context,
            response=ctx.response,
        )
        ctx.confidence_result = result
        ctx.confidence = result.normalized_confidence
        ctx.reasoning_steps.append(
            ReasoningStep(
                label="confidence_scoring",
                content=(
                    f"confidence={result.confidence}/100, "
                    f"evidence={result.evidence_quality.score}, "
                    f"reasoning={result.reasoning_strength.score}, "
                    f"sources={result.source_reliability.score}, "
                    f"uncertainty={result.uncertainty.score}"
                ),
            )
        )
        logger.debug("Pipeline[score_confidence] confidence=%d", result.confidence)
        return ctx

    async def extract_reasoning(self, ctx: PipelineContext) -> PipelineContext:
        """Extract structured reasoning steps from the model output."""
        logger.debug("Pipeline[extract_reasoning]")
        # TODO: parse chain-of-thought / reasoning tokens from response
        return ctx

    @staticmethod
    def build_response(ctx: PipelineContext) -> ChatPipelineResponse:
        """Map pipeline context to the API response schema."""
        structured = ChatPipeline._build_structured_reasoning(ctx)
        return ChatPipelineResponse(
            response=ctx.response,
            confidence=ctx.confidence,
            category=ctx.input_category,
            reasoning_steps=ctx.reasoning_steps,
            structured_reasoning=structured,
        )

    @staticmethod
    def _item(text: str, confidence: float = 0.5, source: str | None = None) -> ReasoningItem:
        return ReasoningItem(
            text=text.strip(),
            confidence=max(0.0, min(1.0, confidence)),
            source=source,
        )

    @classmethod
    def _build_structured_reasoning(cls, ctx: PipelineContext) -> StructuredReasoning | None:
        """Assemble user-facing structured reasoning from pipeline stage outputs."""
        facts: list[ReasoningItem] = []
        assumptions: list[ReasoningItem] = []
        evidence: list[ReasoningItem] = []
        counterarguments: list[ReasoningItem] = []
        alternative_explanations: list[ReasoningItem] = []

        if ctx.claims is not None:
            for item in ctx.claims.main_claims + ctx.claims.supporting_claims:
                facts.append(cls._item(item.text, item.confidence, item.source))
            for item in ctx.claims.hidden_assumptions:
                assumptions.append(cls._item(item.text, item.confidence, item.source))
            for item in ctx.claims.evidence_provided:
                evidence.append(cls._item(item.text, item.confidence, item.source))
            for item in ctx.claims.unknown_information:
                alternative_explanations.append(
                    cls._item(item.text, item.confidence, item.source)
                )

        if ctx.assumptions is not None:
            for issue in ctx.assumptions.unsupported_assumptions:
                assumptions.append(cls._item(issue.text, issue.confidence))
            for issue in (
                *ctx.assumptions.emotional_reasoning,
                *ctx.assumptions.confirmation_bias,
                *ctx.assumptions.mind_reading,
                *ctx.assumptions.overconfidence,
            ):
                counterarguments.append(cls._item(issue.text, issue.confidence))

        if ctx.fallacies is not None:
            for fallacy in ctx.fallacies.fallacies:
                counterarguments.append(
                    cls._item(fallacy.explanation, fallacy.confidence, fallacy.fallacy.value)
                )

        confidence_score = ctx.confidence
        if confidence_score > 1.0:
            confidence_score = confidence_score / 100.0

        structured = StructuredReasoning(
            facts=facts,
            assumptions=assumptions,
            evidence=evidence,
            counterarguments=counterarguments,
            confidence_score=max(0.0, min(1.0, confidence_score)),
            alternative_explanations=alternative_explanations,
        )

        if not any(
            [
                structured.facts,
                structured.assumptions,
                structured.evidence,
                structured.counterarguments,
                structured.alternative_explanations,
                structured.confidence_score > 0,
            ]
        ):
            return None

        return structured

    @staticmethod
    def _build_confidence_context(ctx: PipelineContext) -> str:
        parts: list[str] = []
        if ctx.input_category is not None:
            parts.append(f"Input category: {ctx.input_category.value}")
        if ctx.claims is not None:
            parts.append(
                f"Claims: main={len(ctx.claims.main_claims)}, "
                f"assumptions={len(ctx.claims.hidden_assumptions)}"
            )
        if ctx.assumptions is not None:
            parts.append(f"Detected issues: {ctx.assumptions.total_issues}")
        if ctx.fallacies is not None:
            parts.append(f"Fallacies: {len(ctx.fallacies.fallacies)}")
        return "\n".join(parts)
