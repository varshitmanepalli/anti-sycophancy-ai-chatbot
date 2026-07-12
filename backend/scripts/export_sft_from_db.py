#!/usr/bin/env python3
"""Export conversations from PostgreSQL and generate SFT JSONL for QLoRA.

Usage:
    python scripts/export_sft_from_db.py \\
        --database-url postgresql+asyncpg://postgres:postgres@localhost:5432/chatbot \\
        --output-dir data/sft

Requires DATABASE_URL or --database-url.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT / "src"))

from app.config.settings import get_settings
from app.config.training import get_training_settings
from app.database.models.conversation import ConversationORM
from app.logging.setup import configure_logging, get_logger
from app.training.sft.models import ConversationRecord, MessageRecord
from app.training.sft.pipeline import SFTDatasetPipeline

logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export DB conversations to SFT JSONL")
    parser.add_argument("--database-url", default=None, help="Async SQLAlchemy database URL")
    parser.add_argument("--output-dir", default=None, help="Output directory")
    parser.add_argument("--limit", type=int, default=0, help="Max conversations (0 = all)")
    parser.add_argument(
        "--instruction",
        default=None,
        help="Instruction text for each SFT row",
    )
    parser.add_argument("--split", type=float, default=None, help="Validation split ratio")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument(
        "--raw-output",
        default=None,
        help="Optional path to save raw exported conversations JSON",
    )
    return parser.parse_args()


async def fetch_conversations(
    session: AsyncSession,
    *,
    limit: int = 0,
) -> list[ConversationRecord]:
    """Load conversation records from the database."""
    stmt = select(ConversationORM).options(selectinload(ConversationORM.messages))
    if limit > 0:
        stmt = stmt.limit(limit)

    result = await session.execute(stmt)
    conversations: list[ConversationRecord] = []
    for orm in result.scalars().all():
        messages = [
            MessageRecord(role=m.role.value, content=m.content)
            for m in sorted(orm.messages, key=lambda item: item.created_at)
        ]
        conversations.append(
            ConversationRecord(
                messages=messages,
                conversation_id=str(orm.id),
                user_id=orm.user_id,
            )
        )
    return conversations


async def run_export(args: argparse.Namespace) -> int:
    settings = get_training_settings()
    database_url = args.database_url or get_settings().database_url

    engine = create_async_engine(database_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        conversations = await fetch_conversations(session, limit=args.limit)

    await engine.dispose()
    logger.info("Exported %d conversations from database", len(conversations))

    if args.raw_output:
        raw_path = Path(args.raw_output)
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        payload = [
            {
                "id": conversation.conversation_id,
                "user_id": conversation.user_id,
                "messages": [
                    {"role": message.role, "content": message.content}
                    for message in conversation.messages
                ],
            }
            for conversation in conversations
        ]
        raw_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        logger.info("Raw conversations saved: %s", raw_path)

    output_dir = Path(args.output_dir) if args.output_dir else settings.sft_output_dir
    instruction = args.instruction or settings.sft_instruction

    try:
        result = SFTDatasetPipeline(settings=settings).from_conversations(
            conversations,
            output_dir=output_dir,
            val_ratio=args.split,
            seed=args.seed,
            instruction=instruction,
        )
    except ValueError as exc:
        logger.error("SFT export failed: %s", exc)
        return 1

    logger.info("SFT examples generated: %d", result.examples_generated)
    logger.info("Train rows written: %d -> %s", result.train_count, result.train_path)
    if result.val_count:
        logger.info("Validation rows written: %d -> %s", result.val_count, result.val_path)
    logger.info("QLoRA dataset info: %s", result.info_path)
    return 0


def main() -> int:
    configure_logging(get_settings())
    args = parse_args()
    return asyncio.run(run_export(args))


if __name__ == "__main__":
    raise SystemExit(main())
