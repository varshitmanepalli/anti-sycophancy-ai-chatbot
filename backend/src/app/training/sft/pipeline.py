"""SFT dataset generation pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.config.training import TrainingSettings, get_training_settings
from app.logging.setup import get_logger
from app.training.sft.converter import ConversationToSFTConverter
from app.training.sft.io import (
    load_conversations,
    split_examples,
    write_jsonl,
    write_qlora_dataset_info,
)
from app.training.sft.models import ConversationRecord, SFTExample

logger = get_logger(__name__)


@dataclass(frozen=True)
class SFTDatasetResult:
    """Artifacts produced by SFT dataset generation."""

    conversations_loaded: int
    examples_generated: int
    train_count: int
    val_count: int
    train_path: Path
    val_path: Path | None
    info_path: Path


class SFTDatasetPipeline:
    """Compose conversation loading, conversion, splitting, and export."""

    def __init__(
        self,
        *,
        settings: TrainingSettings | None = None,
        converter: ConversationToSFTConverter | None = None,
    ) -> None:
        self._settings = settings or get_training_settings()
        self._converter = converter or ConversationToSFTConverter(
            instruction=self._settings.sft_instruction
        )

    def from_conversations(
        self,
        conversations: list[ConversationRecord],
        *,
        output_dir: Path | None = None,
        val_ratio: float | None = None,
        seed: int | None = None,
        include_metadata: bool | None = None,
        instruction: str | None = None,
    ) -> SFTDatasetResult:
        """Convert conversations and write train/val JSONL files."""
        if instruction is not None:
            converter = ConversationToSFTConverter(instruction=instruction)
        else:
            converter = self._converter

        examples = converter.convert_many(conversations)
        if not examples:
            raise ValueError("No SFT examples generated from input conversations")

        return self._write_examples(
            examples,
            conversations_loaded=len(conversations),
            output_dir=output_dir,
            val_ratio=val_ratio,
            seed=seed,
            include_metadata=include_metadata,
            instruction=instruction or self._settings.sft_instruction,
        )

    def from_file(
        self,
        input_path: str | Path,
        *,
        output_dir: Path | None = None,
        val_ratio: float | None = None,
        seed: int | None = None,
        include_metadata: bool | None = None,
        instruction: str | None = None,
    ) -> SFTDatasetResult:
        """Load conversations from disk and export SFT JSONL."""
        conversations = load_conversations(input_path)
        logger.info(
            "Loaded conversations: path=%s count=%d",
            input_path,
            len(conversations),
        )
        return self.from_conversations(
            conversations,
            output_dir=output_dir,
            val_ratio=val_ratio,
            seed=seed,
            include_metadata=include_metadata,
            instruction=instruction,
        )

    def _write_examples(
        self,
        examples: list[SFTExample],
        *,
        conversations_loaded: int,
        output_dir: Path | None,
        val_ratio: float | None,
        seed: int | None,
        include_metadata: bool | None,
        instruction: str,
    ) -> SFTDatasetResult:
        resolved_output_dir = output_dir or self._settings.sft_output_dir
        resolved_val_ratio = (
            self._settings.sft_val_ratio if val_ratio is None else val_ratio
        )
        resolved_seed = self._settings.sft_seed if seed is None else seed
        resolved_metadata = (
            self._settings.sft_include_metadata
            if include_metadata is None
            else include_metadata
        )

        train_rows, val_rows = split_examples(
            examples,
            val_ratio=resolved_val_ratio,
            seed=resolved_seed,
        )

        resolved_output_dir.mkdir(parents=True, exist_ok=True)
        train_path = resolved_output_dir / "train.jsonl"
        val_path = resolved_output_dir / "val.jsonl"
        info_path = resolved_output_dir / "dataset_info.json"

        train_count = write_jsonl(
            train_rows,
            train_path,
            include_metadata=resolved_metadata,
        )
        val_count = 0
        if val_rows:
            val_count = write_jsonl(
                val_rows,
                val_path,
                include_metadata=resolved_metadata,
            )

        write_qlora_dataset_info(
            info_path,
            train_file=train_path.name,
            val_file=val_path.name if val_count else None,
            instruction=instruction,
        )

        logger.info(
            "SFT dataset exported: conversations=%d examples=%d train=%d val=%d dir=%s",
            conversations_loaded,
            len(examples),
            train_count,
            val_count,
            resolved_output_dir,
        )

        return SFTDatasetResult(
            conversations_loaded=conversations_loaded,
            examples_generated=len(examples),
            train_count=train_count,
            val_count=val_count,
            train_path=train_path,
            val_path=val_path if val_count else None,
            info_path=info_path,
        )
