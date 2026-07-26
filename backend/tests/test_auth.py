"""Auth + JWT security tests."""
from datetime import datetime, timedelta, timezone

import jwt as pyjwt

from tests.conftest import make_user

API = "/api/v1"


def test_signup_returns_tokens_and_me_works(client):
    u = make_user(client, "signup")
    assert u["tokens"]["access_token"] and u["tokens"]["refresh_token"]
    me = client.get(f"{API}/auth/me", headers=u["headers"])
    assert me.status_code == 200
    assert me.json()["email"] == u["email"]
    assert "hashed_password" not in me.json()


def test_duplicate_signup_conflict(client, user):
    resp = client.post(f"{API}/auth/signup", json={"email": user["email"], "password": "Another123"})
    assert resp.status_code == 409


def test_weak_passwords_rejected(client):
    for bad in ["short1A", "alllettersonly", "12345678901"]:
        resp = client.post(f"{API}/auth/signup", json={"email": "weak@test.dev", "password": bad})
        assert resp.status_code == 422, f"{bad} should be rejected"


def test_login_ok_and_wrong_password_401(client, user):
    ok = client.post(f"{API}/auth/login", json={"email": user["email"], "password": user["password"]})
    assert ok.status_code == 200
    bad = client.post(f"{API}/auth/login", json={"email": user["email"], "password": "WrongPass123"})
    assert bad.status_code == 401
    unknown = client.post(f"{API}/auth/login", json={"email": "ghost@test.dev", "password": "WrongPass123"})
    assert unknown.status_code == 401
    # Same message for unknown email vs wrong password — no account enumeration.
    assert bad.json()["detail"] == unknown.json()["detail"]


def test_protected_routes_require_valid_token(client):
    assert client.get(f"{API}/auth/me").status_code == 401
    assert client.get(f"{API}/projects").status_code == 401
    assert client.get(f"{API}/auth/me", headers={"Authorization": "Bearer not-a-jwt"}).status_code == 401
    assert client.get(f"{API}/auth/me", headers={"Authorization": "Basic abc"}).status_code == 401


def test_expired_and_forged_tokens_rejected(client, user):
    me = client.get(f"{API}/auth/me", headers=user["headers"])
    user_id = me.json()["id"]
    now = datetime.now(timezone.utc)

    expired = pyjwt.encode(
        {"sub": user_id, "type": "access", "iat": now - timedelta(hours=2), "exp": now - timedelta(hours=1)},
        "test-secret-key-for-tests-only",
        algorithm="HS256",
    )
    assert client.get(f"{API}/auth/me", headers={"Authorization": f"Bearer {expired}"}).status_code == 401

    forged = pyjwt.encode(
        {"sub": user_id, "type": "access", "iat": now, "exp": now + timedelta(hours=1)},
        "attacker-secret",
        algorithm="HS256",
    )
    assert client.get(f"{API}/auth/me", headers={"Authorization": f"Bearer {forged}"}).status_code == 401

    # A refresh-type token must not work as an access token.
    wrong_type = pyjwt.encode(
        {"sub": user_id, "type": "refresh", "iat": now, "exp": now + timedelta(hours=1)},
        "test-secret-key-for-tests-only",
        algorithm="HS256",
    )
    assert client.get(f"{API}/auth/me", headers={"Authorization": f"Bearer {wrong_type}"}).status_code == 401


def test_refresh_rotation_and_reuse_detection(client):
    u = make_user(client, "rotate")
    first = client.post(f"{API}/auth/refresh", json={"refresh_token": u["tokens"]["refresh_token"]})
    assert first.status_code == 200
    new_tokens = first.json()
    assert new_tokens["refresh_token"] != u["tokens"]["refresh_token"]
    # The old refresh token is single-use — reuse must fail.
    reuse = client.post(f"{API}/auth/refresh", json={"refresh_token": u["tokens"]["refresh_token"]})
    assert reuse.status_code == 401
    # The new one still works.
    second = client.post(f"{API}/auth/refresh", json={"refresh_token": new_tokens["refresh_token"]})
    assert second.status_code == 200


def test_logout_revokes_refresh_token(client):
    u = make_user(client, "logout")
    resp = client.post(
        f"{API}/auth/logout", json={"refresh_token": u["tokens"]["refresh_token"]}, headers=u["headers"]
    )
    assert resp.status_code == 204
    reuse = client.post(f"{API}/auth/refresh", json={"refresh_token": u["tokens"]["refresh_token"]})
    assert reuse.status_code == 401


def test_change_password_revokes_all_refresh_tokens(client):
    u = make_user(client, "chpass")
    resp = client.post(
        f"{API}/auth/change-password",
        json={"current_password": u["password"], "new_password": "NewStr0ngPass9"},
        headers=u["headers"],
    )
    assert resp.status_code == 204
    assert client.post(f"{API}/auth/refresh", json={"refresh_token": u["tokens"]["refresh_token"]}).status_code == 401
    assert client.post(f"{API}/auth/login", json={"email": u["email"], "password": u["password"]}).status_code == 401
    assert client.post(f"{API}/auth/login", json={"email": u["email"], "password": "NewStr0ngPass9"}).status_code == 200
    # Wrong current password is rejected.
    wrong = client.post(
        f"{API}/auth/change-password",
        json={"current_password": "Nope12345", "new_password": "Whatever123"},
        headers=u["headers"],
    )
    assert wrong.status_code == 403


def test_update_profile_settings(client, user):
    resp = client.patch(
        f"{API}/auth/me",
        json={"display_name": "New Name", "learning_intensity": "intense"},
        headers=user["headers"],
    )
    assert resp.status_code == 200
    assert resp.json()["display_name"] == "New Name"
    assert resp.json()["learning_intensity"] == "intense"
    bad = client.patch(f"{API}/auth/me", json={"learning_intensity": "turbo"}, headers=user["headers"])
    assert bad.status_code == 422
