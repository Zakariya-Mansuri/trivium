"""App-level security posture: headers, CORS, health, rate limiter wiring."""
from app.core.config import settings
from app.main import app

API = "/api/v1"


def test_health_is_public(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_security_headers_present(client):
    resp = client.get("/health")
    assert resp.headers["X-Content-Type-Options"] == "nosniff"
    assert resp.headers["X-Frame-Options"] == "DENY"
    assert resp.headers["Referrer-Policy"] == "no-referrer"


def test_cors_is_allowlisted_not_wildcard(client):
    assert "*" not in settings.cors_origins_list
    preflight = client.options(
        f"{API}/auth/login",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )
    assert preflight.status_code == 200
    assert preflight.headers["access-control-allow-origin"] == "http://localhost:5173"
    evil = client.options(
        f"{API}/auth/login",
        headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"},
    )
    assert "access-control-allow-origin" not in {k.lower() for k in evil.headers.keys()} or evil.status_code == 400


def test_rate_limiter_is_wired(client):
    # Enabled=false in tests, but the limiter must be attached with real limits configured.
    assert app.state.limiter is not None
    assert settings.RATE_LIMIT_AUTH.endswith("/minute")


def test_oversized_and_malformed_payloads_rejected(client, user):
    too_long = client.post(
        f"{API}/agent/chat", json={"message": "x" * 60_000}, headers=user["headers"]
    )
    assert too_long.status_code == 422
    malformed = client.post(
        f"{API}/sessions/import",
        json={"source_tool": "not_a_tool", "messages": [{"role": "user", "content": "hi"}]},
        headers=user["headers"],
    )
    assert malformed.status_code == 422
    bad_role = client.post(
        f"{API}/sessions/import",
        json={"source_tool": "other", "messages": [{"role": "root", "content": "hi"}]},
        headers=user["headers"],
    )
    assert bad_role.status_code == 422
