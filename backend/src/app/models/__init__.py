"""Model layer — LLM inference adapters.

Abstracts Hugging Face Transformers and vLLM behind a common interface
(``domain.interfaces.LLMProvider``). Swap backends via configuration
without changing service-layer code.
"""
