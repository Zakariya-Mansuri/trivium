"""User-attached LLM providers (BYOK): encryption, masking, resolution, isolation."""
from sqlalchemy import select

from app.core.crypto import decrypt_secret, encrypt_secret
from app.db.session import SessionLocal
from app.llm import build_provider, get_llm
from app.llm.mock import MockProvider
from app.models import User

API = "/api/v1"
FAKE_KEY = "gsk_test_1234567890abcd"


def test_encryption_roundtrip_and_tamper_safety():
    token = encrypt_secret(FAKE_KEY)
    assert token != FAKE_KEY and FAKE_KEY not in token
    assert decrypt_secret(token) == FAKE_KEY
    assert decrypt_secret("garbage-token") is None


def test_set_get_clear_provider_config(client, user):
    # Default: server fallback (mock in tests).
    initial = client.get(f"{API}/auth/me/llm", headers=user["headers"]).json()
    assert initial["source"] == "server_default"

    # Attach own Groq key.
    saved = client.put(
        f"{API}/auth/me/llm",
        json={"provider": "groq", "model": "openai/gpt-oss-20b", "api_key": FAKE_KEY},
        headers=user["headers"],
    )
    assert saved.status_code == 200
    body = saved.json()
    assert body["source"] == "user"
    assert body["provider"] == "groq"
    assert body["model"] == "openai/gpt-oss-20b"
    assert body["key_hint"] == "••••abcd"  # masked — never the full key
    assert FAKE_KEY not in saved.text

    # Stored encrypted, not plaintext.
    db = SessionLocal()
    try:
        row = db.scalar(select(User).where(User.email == user["email"]))
        assert row.llm_api_key_enc and FAKE_KEY not in row.llm_api_key_enc
        assert decrypt_secret(row.llm_api_key_enc) == FAKE_KEY
        # Resolution: get_llm(user) returns THEIR provider.
        provider = get_llm(row)
        assert provider.name == "groq" and provider.model == "openai/gpt-oss-20b"
        assert provider.api_key == FAKE_KEY
    finally:
        db.close()

    # /auth/me must not leak the key material.
    me = client.get(f"{API}/auth/me", headers=user["headers"])
    assert FAKE_KEY not in me.text and "llm_api_key" not in me.text

    # Clear -> back to server default.
    cleared = client.delete(f"{API}/auth/me/llm", headers=user["headers"]).json()
    assert cleared["source"] == "server_default" and cleared["key_hint"] is None


def test_unknown_provider_rejected_and_catalog_served(client, user):
    bad = client.put(
        f"{API}/auth/me/llm",
        json={"provider": "notreal", "api_key": FAKE_KEY},
        headers=user["headers"],
    )
    assert bad.status_code == 422

    catalog = client.get(f"{API}/auth/me/llm/providers", headers=user["headers"]).json()["providers"]
    names = {p["name"] for p in catalog}
    assert {"groq", "openrouter", "gemini", "openai", "anthropic"} <= names
    for p in catalog:
        assert p["label"] and p["default_model"] and p["keys_url"]


def test_provider_configs_are_per_user(client, user, other_user):
    client.put(
        f"{API}/auth/me/llm",
        json={"provider": "openrouter", "api_key": FAKE_KEY},
        headers=user["headers"],
    )
    theirs = client.get(f"{API}/auth/me/llm", headers=other_user["headers"]).json()
    assert theirs["source"] == "server_default"
    mine = client.get(f"{API}/auth/me/llm", headers=user["headers"]).json()
    assert mine["provider"] == "openrouter"
    # Default model filled from the registry when not specified.
    assert mine["model"] == "meta-llama/llama-3.3-70b-instruct:free"


def test_resolution_fallback_chain():
    # No user config + mock env (tests) -> MockProvider.
    assert isinstance(get_llm(None), MockProvider)
    # build_provider with unknown name or empty key -> None.
    assert build_provider("notreal", None, "key") is None
    assert build_provider("groq", None, "") is None
    # Anthropic uses its own protocol class.
    anthropic = build_provider("anthropic", None, FAKE_KEY)
    assert anthropic.name == "anthropic" and anthropic.model == "claude-sonnet-5"


def test_test_endpoint_reports_mock_when_no_key(client, user):
    resp = client.post(f"{API}/auth/me/llm/test", headers=user["headers"])
    assert resp.status_code == 200
    assert resp.json()["ok"] is True
    assert resp.json()["provider"] == "mock"
