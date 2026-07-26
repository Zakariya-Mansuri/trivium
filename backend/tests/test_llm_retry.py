"""Provider retry behavior: 429/5xx backoff, Retry-After respected, then LLMError."""
import httpx
import pytest

from app.llm import remote
from app.llm.base import LLMError


class FakeResponse:
    def __init__(self, status_code: int, headers: dict | None = None, payload: dict | None = None):
        self.status_code = status_code
        self.headers = headers or {}
        self._payload = payload or {}

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(f"{self.status_code}", request=None, response=None)


def _provider():
    p = remote.OpenAICompatProvider.__new__(remote.OpenAICompatProvider)
    p.name = "groq"
    p.base_url = "https://api.groq.com/openai/v1"
    p.model = "test-model"
    p.api_key = "test-key"
    return p


def test_429_is_retried_then_succeeds(monkeypatch):
    calls = {"n": 0}
    sleeps: list[float] = []

    def fake_post(url, json=None, headers=None, timeout=None):
        calls["n"] += 1
        if calls["n"] < 3:
            return FakeResponse(429, headers={"retry-after": "2"})
        return FakeResponse(200, payload={"choices": [{"message": {"content": "recovered"}}]})

    monkeypatch.setattr(remote.httpx, "post", fake_post)
    monkeypatch.setattr(remote.time, "sleep", sleeps.append)

    result = _provider().complete([{"role": "user", "content": "hi"}])
    assert result == "recovered"
    assert calls["n"] == 3
    assert sleeps == [2.0, 2.0]  # Retry-After honored


def test_retry_after_is_capped(monkeypatch):
    sleeps: list[float] = []
    responses = iter([FakeResponse(429, headers={"retry-after": "3600"}),
                      FakeResponse(200, payload={"choices": [{"message": {"content": "ok"}}]})])
    monkeypatch.setattr(remote.httpx, "post", lambda *a, **k: next(responses))
    monkeypatch.setattr(remote.time, "sleep", sleeps.append)

    assert _provider().complete([{"role": "user", "content": "hi"}]) == "ok"
    assert sleeps == [remote.MAX_RETRY_DELAY_SECONDS]  # capped at 5s, not an hour


def test_persistent_429_raises_llmerror_after_max_attempts(monkeypatch):
    calls = {"n": 0}

    def always_429(url, json=None, headers=None, timeout=None):
        calls["n"] += 1
        return FakeResponse(429)

    monkeypatch.setattr(remote.httpx, "post", always_429)
    monkeypatch.setattr(remote.time, "sleep", lambda _s: None)

    with pytest.raises(LLMError, match="429"):
        _provider().complete([{"role": "user", "content": "hi"}])
    assert calls["n"] == remote.MAX_ATTEMPTS


def test_server_errors_and_timeouts_retry(monkeypatch):
    responses = iter([
        FakeResponse(500),
        FakeResponse(200, payload={"choices": [{"message": {"content": "ok"}}]}),
    ])
    monkeypatch.setattr(remote.httpx, "post", lambda *a, **k: next(responses))
    monkeypatch.setattr(remote.time, "sleep", lambda _s: None)
    assert _provider().complete([{"role": "user", "content": "hi"}]) == "ok"

    calls = {"n": 0}

    def flaky_then_ok(url, json=None, headers=None, timeout=None):
        calls["n"] += 1
        if calls["n"] == 1:
            raise httpx.ConnectTimeout("timed out")
        return FakeResponse(200, payload={"choices": [{"message": {"content": "ok"}}]})

    monkeypatch.setattr(remote.httpx, "post", flaky_then_ok)
    assert _provider().complete([{"role": "user", "content": "hi"}]) == "ok"
    assert calls["n"] == 2
