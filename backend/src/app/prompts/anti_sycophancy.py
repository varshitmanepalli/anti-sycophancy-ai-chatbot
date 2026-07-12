"""Anti-sycophancy system prompt template.

Defines the core persona instructions that discourage flattery, agreement
bias, and uncritical validation. The actual prompt text will be refined
during implementation.
"""

from app.prompts.base import BasePromptTemplate, PromptMessage

# Placeholder — replace with the full anti-sycophancy system prompt.
ANTI_SYCOPHANCY_SYSTEM_PROMPT = (
    "You are a direct, honest assistant. Prioritize truth and critical "
    "thinking over user validation. Disagree respectfully when warranted."
)


class AntiSycophancyPrompt(BasePromptTemplate):
    """System prompt that establishes the anti-sycophancy persona."""

    def render(self, **kwargs) -> list[PromptMessage]:
        return [
            PromptMessage(role="system", content=ANTI_SYCOPHANCY_SYSTEM_PROMPT),
        ]


class ConversationPrompt(BasePromptTemplate):
    """Assembles system prompt + conversation history + user message."""

    def __init__(self, system_template: BasePromptTemplate | None = None) -> None:
        self._system = system_template or AntiSycophancyPrompt()

    def render(
        self,
        user_message: str,
        history: list[dict[str, str]] | None = None,
        **kwargs,
    ) -> list[PromptMessage]:
        messages = self._system.render(**kwargs)

        if history:
            messages.extend(
                PromptMessage(role=turn["role"], content=turn["content"])
                for turn in history
            )

        messages.append(PromptMessage(role="user", content=user_message))
        return messages
