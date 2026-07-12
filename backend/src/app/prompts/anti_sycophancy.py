"""Anti-sycophancy system prompt template.

Legacy wrapper — delegates to ``PromptManager`` for versioned templates.
"""

from app.prompts.base import BasePromptTemplate, PromptMessage
from app.prompts.manager import PromptManager
from app.prompts.types import PromptType


class AntiSycophancyPrompt(BasePromptTemplate):
    """System prompt that establishes the anti-sycophancy persona."""

    def __init__(
        self,
        manager: PromptManager | None = None,
        version: str | None = None,
    ) -> None:
        self._manager = manager or PromptManager()
        self._version = version

    def render(self, **kwargs) -> list[PromptMessage]:
        return self._manager.render_messages(
            PromptType.SYSTEM,
            version=self._version,
            variables=kwargs,
        )


class ConversationPrompt(BasePromptTemplate):
    """Assembles system prompt + conversation history + user message."""

    def __init__(
        self,
        system_template: BasePromptTemplate | None = None,
        manager: PromptManager | None = None,
        system_version: str | None = None,
    ) -> None:
        self._system = system_template or AntiSycophancyPrompt(
            manager=manager, version=system_version
        )

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
