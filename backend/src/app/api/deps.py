"""FastAPI dependency injection.

Provides reusable ``Depends()`` callables for settings, services,
database sessions, authentication, and the model manager.
"""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import Settings, get_settings
from app.core.security import get_current_user
from app.database.session import get_async_session
from app.models.model_manager import ModelManager
from app.schemas.auth import UserContext
from app.database.repositories.memory_repository import SQLMemoryRepository
from app.prompts.manager import PromptManager, get_prompt_manager
from app.services.chat_pipeline.pipeline import ChatPipeline
from app.services.chat_service import ChatService
from app.services.assumptions.detector import AssumptionDetector
from app.services.debate.engine import DebateEngine
from app.services.fallacies.detector import LogicalFallacyDetector
from app.services.claims.extractor import ClaimExtractor
from app.services.classification.classifier import InputClassifier
from app.services.confidence.engine import ConfidenceEngine
from app.services.memory.extractor import MemoryExtractor
from app.services.contradictions.checker import MemoryContradictionChecker
from app.services.contradictions.detector import ContradictionDetector
from app.services.health_service import HealthService


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

SettingsDep = Annotated[Settings, Depends(get_settings)]


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session per request."""
    async for session in get_async_session():
        yield session


DbSession = Annotated[AsyncSession, Depends(get_db)]


# ---------------------------------------------------------------------------
# Model manager (singleton)
# ---------------------------------------------------------------------------

async def get_model_manager() -> ModelManager:
    """Return the ModelManager singleton."""
    return await ModelManager.get_instance()


ModelManagerDep = Annotated[ModelManager, Depends(get_model_manager)]


# ---------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------

async def get_health_service(
    settings: SettingsDep,
    model_manager: ModelManagerDep,
) -> HealthService:
    return HealthService(settings=settings, model_manager=model_manager)


async def get_chat_service(
    model_manager: ModelManagerDep,
    settings: SettingsDep,
) -> ChatService:
    return ChatService(model_manager=model_manager, settings=settings)


async def get_chat_pipeline(
    settings: SettingsDep,
    model_manager: ModelManagerDep,
    prompt_manager: PromptManagerDep,
) -> ChatPipeline:
    classifier = InputClassifier(
        settings=settings,
        model_manager=model_manager,
        prompt_manager=prompt_manager,
    )
    claim_extractor = ClaimExtractor(
        model_manager=model_manager,
        settings=settings,
        prompt_manager=prompt_manager,
    )
    assumption_detector = AssumptionDetector(
        model_manager=model_manager,
        settings=settings,
        prompt_manager=prompt_manager,
    )
    fallacy_detector = LogicalFallacyDetector(
        model_manager=model_manager,
        settings=settings,
        prompt_manager=prompt_manager,
    )
    confidence_engine = ConfidenceEngine(
        model_manager=model_manager,
        settings=settings,
        prompt_manager=prompt_manager,
    )
    return ChatPipeline(
        classifier=classifier,
        claim_extractor=claim_extractor,
        assumption_detector=assumption_detector,
        fallacy_detector=fallacy_detector,
        confidence_engine=confidence_engine,
    )


async def get_memory_repository(session: DbSession) -> SQLMemoryRepository:
    return SQLMemoryRepository(session)


async def get_prompt_manager_dep() -> PromptManager:
    return get_prompt_manager()


async def get_input_classifier(
    settings: SettingsDep,
    model_manager: ModelManagerDep,
    prompt_manager: PromptManagerDep,
) -> InputClassifier:
    return InputClassifier(
        settings=settings,
        model_manager=model_manager,
        prompt_manager=prompt_manager,
    )


HealthServiceDep = Annotated[HealthService, Depends(get_health_service)]
ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
ChatPipelineDep = Annotated[ChatPipeline, Depends(get_chat_pipeline)]
MemoryRepositoryDep = Annotated[SQLMemoryRepository, Depends(get_memory_repository)]
PromptManagerDep = Annotated[PromptManager, Depends(get_prompt_manager_dep)]
async def get_claim_extractor(
    settings: SettingsDep,
    model_manager: ModelManagerDep,
    prompt_manager: PromptManagerDep,
) -> ClaimExtractor:
    return ClaimExtractor(
        model_manager=model_manager,
        settings=settings,
        prompt_manager=prompt_manager,
    )


async def get_assumption_detector(
    settings: SettingsDep,
    model_manager: ModelManagerDep,
    prompt_manager: PromptManagerDep,
) -> AssumptionDetector:
    return AssumptionDetector(
        model_manager=model_manager,
        settings=settings,
        prompt_manager=prompt_manager,
    )


async def get_fallacy_detector(
    settings: SettingsDep,
    model_manager: ModelManagerDep,
    prompt_manager: PromptManagerDep,
) -> LogicalFallacyDetector:
    return LogicalFallacyDetector(
        model_manager=model_manager,
        settings=settings,
        prompt_manager=prompt_manager,
    )


async def get_confidence_engine(
    settings: SettingsDep,
    model_manager: ModelManagerDep,
    prompt_manager: PromptManagerDep,
) -> ConfidenceEngine:
    return ConfidenceEngine(
        model_manager=model_manager,
        settings=settings,
        prompt_manager=prompt_manager,
    )


InputClassifierDep = Annotated[InputClassifier, Depends(get_input_classifier)]
ClaimExtractorDep = Annotated[ClaimExtractor, Depends(get_claim_extractor)]
AssumptionDetectorDep = Annotated[AssumptionDetector, Depends(get_assumption_detector)]
FallacyDetectorDep = Annotated[LogicalFallacyDetector, Depends(get_fallacy_detector)]
ConfidenceEngineDep = Annotated[ConfidenceEngine, Depends(get_confidence_engine)]


async def get_memory_extractor(
    settings: SettingsDep,
    model_manager: ModelManagerDep,
    prompt_manager: PromptManagerDep,
) -> MemoryExtractor:
    return MemoryExtractor(
        model_manager=model_manager,
        settings=settings,
        prompt_manager=prompt_manager,
    )


MemoryExtractorDep = Annotated[MemoryExtractor, Depends(get_memory_extractor)]


async def get_contradiction_detector(
    settings: SettingsDep,
    model_manager: ModelManagerDep,
    prompt_manager: PromptManagerDep,
) -> ContradictionDetector:
    return ContradictionDetector(
        model_manager=model_manager,
        settings=settings,
        prompt_manager=prompt_manager,
    )


async def get_contradiction_checker(
    detector: Annotated[ContradictionDetector, Depends(get_contradiction_detector)],
    memory_repo: MemoryRepositoryDep,
) -> MemoryContradictionChecker:
    return MemoryContradictionChecker(
        detector=detector,
        memory_repository=memory_repo,
    )


ContradictionDetectorDep = Annotated[ContradictionDetector, Depends(get_contradiction_detector)]
ContradictionCheckerDep = Annotated[MemoryContradictionChecker, Depends(get_contradiction_checker)]


async def get_debate_engine(
    settings: SettingsDep,
    model_manager: ModelManagerDep,
    prompt_manager: PromptManagerDep,
) -> DebateEngine:
    return DebateEngine(
        model_manager=model_manager,
        settings=settings,
        prompt_manager=prompt_manager,
    )


DebateEngineDep = Annotated[DebateEngine, Depends(get_debate_engine)]


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

CurrentUserDep = Annotated[UserContext, Depends(get_current_user)]
