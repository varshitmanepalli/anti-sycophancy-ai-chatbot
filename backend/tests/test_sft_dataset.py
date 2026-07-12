"""SFT dataset generation tests."""

import json
from pathlib import Path

import pytest

from app.training.sft.converter import ConversationToSFTConverter
from app.training.sft.io import (
    format_qlora_prompt,
    load_conversations,
    split_examples,
    write_jsonl,
    write_qlora_dataset_info,
)
from app.training.sft.models import ConversationRecord, MessageRecord, SFTExample


SAMPLE_CONVERSATION = ConversationRecord(
    conversation_id="conv-1",
    messages=[
        MessageRecord(role="user", content="Should I trust this plan?"),
        MessageRecord(
            role="assistant",
            content="The plan lacks measurable milestones, so confidence should stay low until you verify assumptions.",
        ),
        MessageRecord(role="user", content="What should I verify first?"),
        MessageRecord(
            role="assistant",
            content="Verify the cost estimates and the timeline against at least one independent source.",
        ),
    ],
)


class TestConversationToSFTConverter:
    def test_creates_one_row_per_assistant_turn(self):
        converter = ConversationToSFTConverter(instruction="Be honest.")
        rows = converter.convert(SAMPLE_CONVERSATION)

        assert len(rows) == 2
        assert rows[0].output.startswith("The plan lacks")
        assert rows[1].output.startswith("Verify the cost")

    def test_input_contains_history(self):
        converter = ConversationToSFTConverter(instruction="Be honest.")
        rows = converter.convert(SAMPLE_CONVERSATION)

        assert "Conversation history:" in rows[1].input
        assert "Should I trust this plan?" in rows[1].input
        assert "What should I verify first?" in rows[1].input

    def test_to_dict_uses_qlora_fields(self):
        example = SFTExample(instruction="Inst", input="In", output="Out")
        data = example.to_dict()
        assert set(data.keys()) == {"instruction", "input", "output"}
        assert example.expected_output == "Out"


class TestSFTIO:
    def test_write_and_read_jsonl(self, tmp_path: Path):
        examples = [
            SFTExample(instruction="I", input="A", output="B"),
            SFTExample(instruction="I", input="C", output="D"),
        ]
        path = tmp_path / "train.jsonl"
        count = write_jsonl(examples, path)
        assert count == 2

        lines = path.read_text(encoding="utf-8").strip().splitlines()
        first = json.loads(lines[0])
        assert first["instruction"] == "I"
        assert first["output"] == "B"

    def test_load_conversations_json(self, tmp_path: Path):
        payload = [
            {
                "id": "c1",
                "messages": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi"},
                ],
            }
        ]
        path = tmp_path / "conversations.json"
        path.write_text(json.dumps(payload), encoding="utf-8")

        conversations = load_conversations(path)
        assert len(conversations) == 1
        assert conversations[0].conversation_id == "c1"
        assert len(conversations[0].messages) == 2

    def test_split_examples(self):
        rows = [
            SFTExample(instruction="i", input=f"in-{n}", output=f"out-{n}")
            for n in range(10)
        ]
        train, val = split_examples(rows, val_ratio=0.2, seed=1)
        assert len(train) == 8
        assert len(val) == 2

    def test_format_qlora_prompt(self):
        prompt = format_qlora_prompt(
            SFTExample(instruction="Inst", input="Input text", output="Output text")
        )
        assert "### Instruction:" in prompt
        assert "### Input:" in prompt
        assert "### Response:" in prompt

    def test_write_qlora_dataset_info(self, tmp_path: Path):
        info_path = tmp_path / "dataset_info.json"
        write_qlora_dataset_info(
            info_path,
            train_file="train.jsonl",
            val_file="val.jsonl",
            instruction="Be direct.",
        )
        info = json.loads(info_path.read_text(encoding="utf-8"))
        assert info["format"] == "alpaca"
        assert info["output_field"] == "output"
        assert info["files"]["train"] == "train.jsonl"


class TestGenerateScript:
    def test_sample_conversations_file_exists(self):
        path = Path(__file__).resolve().parents[1] / "data" / "sample_conversations.json"
        assert path.exists()
        conversations = load_conversations(path)
        assert len(conversations) >= 2

        converter = ConversationToSFTConverter()
        rows = converter.convert_many(conversations)
        assert len(rows) >= 3
