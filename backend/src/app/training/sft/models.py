"""Data models for SFT dataset generation."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MessageRecord:
    """A single turn in conversation history."""

    role: str
    content: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MessageRecord | None":
        role = str(data.get("role", "")).strip().lower()
        content = str(data.get("content", "")).strip()
        if not role or not content:
            return None
        return cls(role=role, content=content)


@dataclass
class ConversationRecord:
    """Conversation history used as SFT source material."""

    messages: list[MessageRecord] = field(default_factory=list)
    conversation_id: str | None = None
    user_id: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConversationRecord":
        raw_messages = data.get("messages", [])
        messages: list[MessageRecord] = []
        if isinstance(raw_messages, list):
            for item in raw_messages:
                if isinstance(item, dict):
                    message = MessageRecord.from_dict(item)
                    if message is not None:
                        messages.append(message)

        conversation_id = data.get("id") or data.get("conversation_id")
        return cls(
            messages=messages,
            conversation_id=str(conversation_id) if conversation_id else None,
            user_id=str(data["user_id"]) if data.get("user_id") else None,
        )


@dataclass
class SFTExample:
    """One supervised fine-tuning row."""

    instruction: str
    input: str
    output: str
    conversation_id: str | None = None
    turn_index: int | None = None

    def to_dict(self) -> dict[str, str]:
        """Alpaca-style dict compatible with QLoRA trainers."""
        return {
            "instruction": self.instruction,
            "input": self.input,
            "output": self.output,
        }

    def to_jsonl_row(self) -> dict[str, Any]:
        """JSONL row with optional metadata stripped for training."""
        row = self.to_dict()
        if self.conversation_id is not None:
            row["conversation_id"] = self.conversation_id
        if self.turn_index is not None:
            row["turn_index"] = self.turn_index
        return row

    @property
    def expected_output(self) -> str:
        """Alias used in documentation and some tooling."""
        return self.output
