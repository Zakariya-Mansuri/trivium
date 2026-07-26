"""Real LLM providers over HTTP (OpenAI-compatible APIs and Anthropic)."""
import logging
import time

import httpx

from app.core.config import settings
from app.llm.base import LLMError, LLMProvider

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 3
MAX_RETRY_DELAY_SECONDS = 5.0


def _retry_delay(resp: httpx.Response, attempt: int) -> float:
    retry_after = resp.headers.get("retry-after")
    try:
        delay = float(retry_after) if retry_after else 1.5 * (attempt + 1)
    except ValueError:
        delay = 1.5 * (attempt + 1)
    return min(delay, MAX_RETRY_DELAY_SECONDS)


def _post_with_retries(name: str, url: str, *, json_body: dict, headers: dict) -> httpx.Response:
    """POST with backoff on 429/5xx/timeouts. Runs in a threadpool, so sleeping is fine."""
    last_exc: Exception | None = None
    for attempt in range(MAX_ATTEMPTS):
        try:
            resp = httpx.post(url, json=json_body, headers=headers, timeout=settings.LLM_TIMEOUT_SECONDS)
        except httpx.HTTPError as exc:
            last_exc = exc
            if attempt < MAX_ATTEMPTS - 1:
                time.sleep(1.5 * (attempt + 1))
                continue
            raise LLMError(f"{name} request failed: {exc}") from exc
        if resp.status_code == 429 or resp.status_code >= 500:
            if attempt < MAX_ATTEMPTS - 1:
                delay = _retry_delay(resp, attempt)
                logger.warning("%s returned %s — retrying in %.1fs", name, resp.status_code, delay)
                time.sleep(delay)
                continue
            raise LLMError(f"{name} unavailable after {MAX_ATTEMPTS} attempts (last status {resp.status_code})")
        return resp
    raise LLMError(f"{name} request failed: {last_exc}")

class OpenAICompatProvider(LLMProvider):
    """Any OpenAI-compatible endpoint (Groq, OpenRouter, Gemini, Cerebras, OpenAI, Sarvam...)."""

    def __init__(self, name: str, base_url: str, model: str, api_key: str):
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key

    def complete(self, messages: list[dict], *, json_mode: bool = False, max_tokens: int = 2048) -> str:
        body: dict = {"model": self.model, "messages": messages, "max_tokens": max_tokens}
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        resp = _post_with_retries(
            self.name,
            f"{self.base_url}/chat/completions",
            json_body=body,
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        try:
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except (httpx.HTTPError, KeyError, IndexError) as exc:
            raise LLMError(f"{self.name} completion failed: {exc}") from exc


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self, model: str, api_key: str):
        self.model = model
        self.api_key = api_key

    def complete(self, messages: list[dict], *, json_mode: bool = False, max_tokens: int = 2048) -> str:
        system = "\n".join(m["content"] for m in messages if m["role"] == "system")
        chat = [m for m in messages if m["role"] != "system"]
        if json_mode:
            system += "\nRespond with a single valid JSON object and nothing else."
        resp = _post_with_retries(
            self.name,
            "https://api.anthropic.com/v1/messages",
            json_body={"model": self.model, "system": system, "messages": chat, "max_tokens": max_tokens},
            headers={"x-api-key": self.api_key, "anthropic-version": "2023-06-01"},
        )
        try:
            resp.raise_for_status()
            return resp.json()["content"][0]["text"]
        except (httpx.HTTPError, KeyError, IndexError) as exc:
            raise LLMError(f"anthropic completion failed: {exc}") from exc
