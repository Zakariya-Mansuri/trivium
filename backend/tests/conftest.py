import os
import uuid

import pytest

# Test environment must be configured before the app is imported.
TEST_DB = os.path.join(os.path.dirname(__file__), "test_trivium.db")
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
os.environ["ENVIRONMENT"] = "test"
os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ["SECRET_KEY"] = "test-secret-key-for-tests-only"
os.environ["LLM_PROVIDER"] = "mock"

from fastapi.testclient import TestClient  # noqa: E402

from app.db.base import Base  # noqa: E402
from app.db.session import engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


def make_user(client: TestClient, prefix: str = "user") -> dict:
    """Registers a fresh user; returns {'headers', 'email', 'password', 'tokens'}."""
    email = f"{prefix}-{uuid.uuid4().hex[:10]}@test.dev"
    password = "Str0ngPass123"
    resp = client.post(
        "/api/v1/auth/signup",
        json={"email": email, "password": password, "display_name": prefix.title()},
    )
    assert resp.status_code == 201, resp.text
    tokens = resp.json()
    return {
        "headers": {"Authorization": f"Bearer {tokens['access_token']}"},
        "email": email,
        "password": password,
        "tokens": tokens,
    }


@pytest.fixture()
def user(client):
    return make_user(client, "alice")


@pytest.fixture()
def other_user(client):
    return make_user(client, "mallory")


RICH_MESSAGES = [
    {"role": "user", "content": "I need JWT authentication in FastAPI. Should I use sessions instead?"},
    {
        "role": "assistant",
        "content": "We decided on JWT instead of server-side sessions because your SPA and API are on "
        "different origins. Tradeoff: revocation needs a refresh-token table.\n```python\nimport jwt\n```",
        "code_diff": "+ token = jwt.encode(payload, SECRET)",
    },
    {"role": "user", "content": "Got an error: InvalidSignatureError when verifying the jwt token."},
    {
        "role": "assistant",
        "content": "That bug means the signing secret differs from the verifying secret. Fix: load "
        "SECRET_KEY from a single config source. Classic config-drift issue in fastapi apps.",
    },
    {"role": "user", "content": "Fixed! Also added bcrypt hashing like the same pattern as before in my last project."},
    {
        "role": "assistant",
        "content": "Good — recurring pattern: authentication hardening with bcrypt hashing plus jwt plus "
        "rate limit protection across the middleware layer, service layer and component architecture.",
    },
]


def import_rich_session(client: TestClient, headers: dict, project_id: str | None = None, tool: str = "claude_code") -> dict:
    resp = client.post(
        "/api/v1/sessions/import",
        json={"project_id": project_id, "source_tool": tool, "title": "JWT debugging session", "messages": RICH_MESSAGES},
        headers=headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()
