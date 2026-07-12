#!/usr/bin/env python3
"""Generate SFT JSONL datasets from conversation history for QLoRA training.

Usage:
    python scripts/generate_sft_dataset.py \\
        --input data/sample_conversations.json \\
        --output-dir data/sft \\
        --split 0.1

Output format (one JSON object per line):
    {"instruction": "...", "input": "...", "output": "..."}
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT / "src"))

from app.config.settings import get_settings
from app.config.training import get_training_settings
from app.logging.setup import configure_logging, get_logger
from app.training.sft.pipeline import SFTDatasetPipeline

logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate SFT JSONL from conversations")
    parser.add_argument(
        "--input",
        required=True,
        help="Path to conversations JSON or JSONL file",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory for train.jsonl, val.jsonl, and dataset_info.json",
    )
    parser.add_argument(
        "--instruction",
        default=None,
        help="Instruction text prepended to every training row",
    )
    parser.add_argument(
        "--split",
        type=float,
        default=None,
        help="Validation split ratio (0 disables val set)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for train/val split",
    )
    parser.add_argument(
        "--include-metadata",
        action="store_true",
        help="Include conversation_id and turn_index in JSONL rows",
    )
    return parser.parse_args()


def main() -> int:
    configure_logging(get_settings())
    args = parse_args()
    settings = get_training_settings()

    output_dir = Path(args.output_dir) if args.output_dir else settings.sft_output_dir
    instruction = args.instruction or settings.sft_instruction

    try:
        result = SFTDatasetPipeline(settings=settings).from_file(
            args.input,
            output_dir=output_dir,
            val_ratio=args.split,
            seed=args.seed,
            include_metadata=args.include_metadata or settings.sft_include_metadata,
            instruction=instruction,
        )
    except ValueError as exc:
        logger.error("SFT generation failed: %s", exc)
        return 1

    logger.info("Conversations loaded: %d", result.conversations_loaded)
    logger.info("SFT examples generated: %d", result.examples_generated)
    logger.info("Train rows written: %d -> %s", result.train_count, result.train_path)
    if result.val_count:
        logger.info("Validation rows written: %d -> %s", result.val_count, result.val_path)
    logger.info("QLoRA dataset info: %s", result.info_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
