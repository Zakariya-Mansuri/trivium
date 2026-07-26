"""LLM provider abstraction — one call signature across providers (LiteLLM-style).

The active provider is chosen by env config (LLM_PROVIDER / LLM_MODEL / LLM_API_KEY).
`mock` is the default and requires no key: it produces deterministic, content-aware
output so the entire product is runnable and testable offline. Swapping in LiteLLM
later only requires implementing one more subclass of LLMProvider.
"""
from abc import ABC, abstractmethod


class LLMError(Exception):
    pass


class LLMProvider(ABC):
    name: str = "base"

    @abstractmethod
    def complete(self, messages: list[dict], *, json_mode: bool = False, max_tokens: int = 2048) -> str:
        """messages: [{'role': 'system'|'user'|'assistant', 'content': str}] -> completion text."""
        raise NotImplementedError
