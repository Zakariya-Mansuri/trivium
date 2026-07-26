"""Real LLM providers over HTTP (OpenAI-compatible APIs and Anthropic)."""
import httpx

from app.core.config import settings
from app.llm.base import LLMError, LLMProvider

OPENAI_COMPAT_BASE_URLS = {
    "openai": "https://api.openai.com/v1",
    "groq": "https://api.groq.com/openai/v1",
    "sarvam": "https://api.sarvam.ai/v1",
}

DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "groq": "llama-3.3-70b-versatile",
    "anthropic": "claude-sonnet-5",
    "sarvam": "sarvam-m",
}


class OpenAICompatProvider(LLMProvider):
    """Works for OpenAI, Groq, Sarvam and any other OpenAI-compatible endpoint."""

    def __init__(self, provider: str):
        self.name = provider
        self.base_url = OPENAI_COMPAT_BASE_URLS[provider]
        self.model = settings.LLM_MODEL or DEFAULT_MODELS[provider]
        self.api_key = settings.LLM_API_KEY

    def complete(self, messages: list[dict], *, json_mode: bool = False, max_tokens: int = 2048) -> str:
        body: dict = {"model": self.model, "messages": messages, "max_tokens": max_tokens}
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        try:
            resp = httpx.post(
                f"{self.base_url}/chat/completions",
                json=body,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=settings.LLM_TIMEOUT_SECONDS,
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except (httpx.HTTPError, KeyError, IndexError) as exc:
            raise LLMError(f"{self.name} completion failed: {exc}") from exc


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self):
        self.model = settings.LLM_MODEL or DEFAULT_MODELS["anthropic"]
        self.api_key = settings.LLM_API_KEY

    def complete(self, messages: list[dict], *, json_mode: bool = False, max_tokens: int = 2048) -> str:
        system = "\n".join(m["content"] for m in messages if m["role"] == "system")
        chat = [m for m in messages if m["role"] != "system"]
        if json_mode:
            system += "\nRespond with a single valid JSON object and nothing else."
        try:
            resp = httpx.post(
                "https://api.anthropic.com/v1/messages",
                json={"model": self.model, "system": system, "messages": chat, "max_tokens": max_tokens},
                headers={"x-api-key": self.api_key, "anthropic-version": "2023-06-01"},
                timeout=settings.LLM_TIMEOUT_SECONDS,
            )
            resp.raise_for_status()
            return resp.json()["content"][0]["text"]
        except (httpx.HTTPError, KeyError, IndexError) as exc:
            raise LLMError(f"anthropic completion failed: {exc}") from exc
