"""Convert conversation history into SFT training examples."""

from app.training.sft.models import ConversationRecord, MessageRecord, SFTExample
from app.training.sft.templates import DEFAULT_INSTRUCTION, HISTORY_HEADER


class ConversationToSFTConverter:
    """Build instruction/input/output rows from multi-turn conversations.

    Creates one SFT example for each assistant turn:
    - instruction: system behavior prompt
    - input: prior conversation + current user message
    - output: assistant response (expected output)
    """

    def __init__(
        self,
        *,
        instruction: str = DEFAULT_INSTRUCTION,
        include_system_in_history: bool = False,
        min_input_chars: int = 1,
        min_output_chars: int = 1,
    ) -> None:
        self.instruction = instruction.strip()
        self.include_system_in_history = include_system_in_history
        self.min_input_chars = min_input_chars
        self.min_output_chars = min_output_chars

    def convert(self, conversation: ConversationRecord) -> list[SFTExample]:
        """Convert a single conversation into SFT examples."""
        examples: list[SFTExample] = []
        history: list[MessageRecord] = []

        for index, message in enumerate(conversation.messages):
            if message.role == "assistant":
                user_message = self._latest_user_message(history)
                if user_message is None:
                    history.append(message)
                    continue

                input_text = self._format_input(history, user_message)
                if len(input_text) < self.min_input_chars:
                    history.append(message)
                    continue
                if len(message.content) < self.min_output_chars:
                    history.append(message)
                    continue

                examples.append(
                    SFTExample(
                        instruction=self.instruction,
                        input=input_text,
                        output=message.content,
                        conversation_id=conversation.conversation_id,
                        turn_index=index,
                    )
                )

            if message.role != "system" or self.include_system_in_history:
                history.append(message)

        return examples

    def convert_many(self, conversations: list[ConversationRecord]) -> list[SFTExample]:
        """Convert multiple conversations."""
        rows: list[SFTExample] = []
        for conversation in conversations:
            rows.extend(self.convert(conversation))
        return rows

    def _format_input(
        self,
        history: list[MessageRecord],
        user_message: MessageRecord,
    ) -> str:
        parts: list[str] = []

        prior = [m for m in history if m.role in {"user", "assistant"}]
        if prior:
            parts.append(HISTORY_HEADER)
            for message in prior:
                parts.append(f"{message.role.capitalize()}: {message.content}")

        parts.append(f"User: {user_message.content}")
        return "\n".join(parts).strip()

    @staticmethod
    def _latest_user_message(history: list[MessageRecord]) -> MessageRecord | None:
        for message in reversed(history):
            if message.role == "user":
                return message
        return None
