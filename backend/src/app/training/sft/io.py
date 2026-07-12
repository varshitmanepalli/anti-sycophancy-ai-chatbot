"""Load conversations and write SFT JSONL datasets."""

import json
import random
from pathlib import Path
from typing import Any

from app.training.sft.models import ConversationRecord, SFTExample
from app.training.sft.templates import QLORA_PROMPT_TEMPLATE


def load_conversations(path: str | Path) -> list[ConversationRecord]:
    """Load conversations from a JSON or JSONL file."""
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8").strip()

    if not text:
        return []

    if file_path.suffix.lower() == ".jsonl":
        return _load_jsonl_conversations(text)

    data = json.loads(text)
    return _parse_conversation_payload(data)


def _load_jsonl_conversations(text: str) -> list[ConversationRecord]:
    conversations: list[ConversationRecord] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        payload = json.loads(line)
        if isinstance(payload, dict) and "messages" in payload:
            conversations.append(ConversationRecord.from_dict(payload))
    return conversations


def _parse_conversation_payload(data: Any) -> list[ConversationRecord]:
    if isinstance(data, list):
        return [ConversationRecord.from_dict(item) for item in data if isinstance(item, dict)]

    if isinstance(data, dict):
        if "conversations" in data and isinstance(data["conversations"], list):
            return [
                ConversationRecord.from_dict(item)
                for item in data["conversations"]
                if isinstance(item, dict)
            ]
        if "messages" in data:
            return [ConversationRecord.from_dict(data)]

    raise ValueError("Unsupported conversation JSON structure")


def write_jsonl(
    examples: list[SFTExample],
    path: str | Path,
    *,
    include_metadata: bool = False,
) -> int:
    """Write SFT examples to JSONL. Returns number of rows written."""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with file_path.open("w", encoding="utf-8") as handle:
        for example in examples:
            row = example.to_jsonl_row() if include_metadata else example.to_dict()
            if not include_metadata:
                row = {key: row[key] for key in ("instruction", "input", "output")}
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1
    return count


def split_examples(
    examples: list[SFTExample],
    *,
    val_ratio: float = 0.1,
    seed: int = 42,
) -> tuple[list[SFTExample], list[SFTExample]]:
    """Split examples into train and validation sets."""
    if not examples or val_ratio <= 0:
        return examples, []

    shuffled = list(examples)
    random.Random(seed).shuffle(shuffled)
    val_size = max(1, int(len(shuffled) * val_ratio))
    if val_size >= len(shuffled):
        val_size = max(1, len(shuffled) // 5)
    return shuffled[val_size:], shuffled[:val_size]


def write_qlora_dataset_info(
    path: str | Path,
    *,
    train_file: str,
    val_file: str | None = None,
    instruction: str,
) -> None:
    """Write a dataset info file for QLoRA / TRL training scripts."""
    info: dict[str, Any] = {
        "format": "alpaca",
        "instruction_field": "instruction",
        "input_field": "input",
        "output_field": "output",
        "prompt_template": QLORA_PROMPT_TEMPLATE,
        "default_instruction": instruction,
        "files": {"train": train_file},
    }
    if val_file:
        info["files"]["validation"] = val_file

    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(info, indent=2), encoding="utf-8")


def format_qlora_prompt(example: SFTExample | dict[str, str]) -> str:
    """Format one example using the standard QLoRA Alpaca template."""
    if isinstance(example, SFTExample):
        data = example.to_dict()
    else:
        data = example
    return QLORA_PROMPT_TEMPLATE.format(
        instruction=data["instruction"],
        input=data["input"],
        output=data["output"],
    )
