"""SFT pipeline tests."""

import json
from pathlib import Path

from app.config.training import TrainingSettings
from app.training.sft.models import ConversationRecord, MessageRecord
from app.training.sft.pipeline import SFTDatasetPipeline


SAMPLE_CONVERSATION = ConversationRecord(
    conversation_id="conv-1",
    messages=[
        MessageRecord(role="user", content="Should I trust this plan?"),
        MessageRecord(
            role="assistant",
            content="The plan lacks measurable milestones, so confidence should stay low.",
        ),
        MessageRecord(role="user", content="What should I verify first?"),
        MessageRecord(
            role="assistant",
            content="Verify the cost estimates against an independent source.",
        ),
    ],
)


class TestSFTDatasetPipeline:
    def test_from_conversations_writes_artifacts(self, tmp_path: Path):
        settings = TrainingSettings(sft_output_dir=tmp_path, sft_val_ratio=0.5, sft_seed=1)
        pipeline = SFTDatasetPipeline(settings=settings)
        result = pipeline.from_conversations([SAMPLE_CONVERSATION])

        assert result.conversations_loaded == 1
        assert result.examples_generated == 2
        assert result.train_count >= 1
        assert result.train_path.exists()
        assert result.info_path.exists()

    def test_from_file(self, tmp_path: Path):
        payload = [
            {
                "id": "c1",
                "messages": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi there."},
                ],
            }
        ]
        input_path = tmp_path / "conversations.json"
        input_path.write_text(json.dumps(payload), encoding="utf-8")

        output_dir = tmp_path / "sft"
        settings = TrainingSettings(sft_output_dir=output_dir)
        result = SFTDatasetPipeline(settings=settings).from_file(input_path)

        assert result.examples_generated == 1
        assert result.train_path.exists()

    def test_raises_when_no_examples(self, tmp_path: Path):
        empty = ConversationRecord(conversation_id="empty", messages=[])
        pipeline = SFTDatasetPipeline(settings=TrainingSettings(sft_output_dir=tmp_path))
        try:
            pipeline.from_conversations([empty])
            raise AssertionError("Expected ValueError")
        except ValueError as exc:
            assert "no sft examples" in str(exc).lower()
