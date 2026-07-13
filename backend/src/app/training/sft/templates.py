"""Default instruction and formatting templates for SFT."""

from app.prompts.config_loader import get_sft_instruction

DEFAULT_INSTRUCTION = get_sft_instruction()

QLORA_PROMPT_TEMPLATE = (
    "### Instruction:\n{instruction}\n\n"
    "### Input:\n{input}\n\n"
    "### Response:\n{output}"
)

HISTORY_HEADER = "Conversation history:"
