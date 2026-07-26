"""Provider factory — config-driven selection with safe fallback to mock."""
from functools import lru_cache

from app.core.config import settings
from app.llm.base import LLMProvider
from app.llm.mock import MockProvider


@lru_cache
def get_llm() -> LLMProvider:
    provider = settings.LLM_PROVIDER.lower()
    if provider in ("openai", "groq", "sarvam") and settings.LLM_API_KEY:
        from app.llm.remote import OpenAICompatProvider

        return OpenAICompatProvider(provider)
    if provider == "anthropic" and settings.LLM_API_KEY:
        from app.llm.remote import AnthropicProvider

        return AnthropicProvider()
    return MockProvider()
