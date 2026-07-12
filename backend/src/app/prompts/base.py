"""Base prompt template abstractions."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PromptMessage:
    """A single message in a prompt (role + content)."""

    role: str
    content: str


class BasePromptTemplate(ABC):
    """Abstract prompt template that produces a list of chat messages."""

    @abstractmethod
    def render(self, **kwargs) -> list[PromptMessage]:
        """Build the prompt messages from template variables."""
        ...

    def to_chat_format(self, **kwargs) -> list[dict[str, str]]:
        """Render and convert to OpenAI/vLLM chat message format."""
        return [{"role": m.role, "content": m.content} for m in self.render(**kwargs)]
