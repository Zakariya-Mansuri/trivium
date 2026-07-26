"""Sessions, import, messages, extraction pipeline."""
from tests.conftest import import_rich_session

API = "/api/v1"


def test_native_session_lifecycle(client, user):
    created = client.post(f"{API}/sessions", json={"title": "hands-on"}, headers=user["headers"])
    assert created.status_code == 201
    body = created.json()
    assert body["source_tool"] == "native" and body["source_fidelity"] == "native"
    sid = body["id"]

    msg = client.post(
        f"{API}/sessions/{sid}/messages",
        json={"role": "user", "content": "How do decorators work in python?"},
        headers=user["headers"],
    )
    assert msg.status_code == 201
    assert msg.json()["authored_by"] == "user"  # authored_by inferred at write time

    detail = client.get(f"{API}/sessions/{sid}", headers=user["headers"])
    assert detail.status_code == 200 and len(detail.json()["messages"]) == 1

    ended = client.post(f"{API}/sessions/{sid}/end", headers=user["headers"])
    assert ended.status_code == 200 and ended.json()["ended_at"] is not None


def test_import_session_extracts_knowledge_units(client, user):
    session = import_rich_session(client, user["headers"])
    assert session["source_fidelity"] == "wrapped"  # fidelity honesty
    assert session["source_tool"] == "claude_code"

    detail = client.get(f"{API}/sessions/{session['id']}", headers=user["headers"]).json()
    assert detail["extraction_status"] == "completed"
    # Imported assistant messages are AI-authored, user messages user-authored.
    for m in detail["messages"]:
        expected = "ai" if m["role"] == "assistant" else "user"
        assert m["authored_by"] == expected

    units = client.get(
        f"{API}/knowledge-units", params={"session_id": session["id"]}, headers=user["headers"]
    ).json()
    assert len(units) >= 2
    types = {u["unit_type"] for u in units}
    assert types <= {"concept", "decision", "bug_fix", "pattern"}
    # The rich transcript contains decision + bug signals — both should be found.
    assert "decision" in types
    assert "bug_fix" in types
    assert all(u["source_fidelity"] == "wrapped" for u in units)


def test_import_from_extension_tools(client, user):
    """The Companion extension imports with source_tool 'claude'/'chatgpt'."""
    for tool in ("claude", "chatgpt", "gemini"):
        resp = client.post(
            f"{API}/sessions/import",
            json={
                "source_tool": tool,
                "title": f"{tool} conversation",
                "messages": [
                    {"role": "user", "content": "How do I fix this jwt bug?", "authored_by": "user"},
                    {"role": "assistant", "content": "The secret mismatch causes the error in fastapi.", "authored_by": "ai"},
                ],
            },
            headers=user["headers"],
        )
        assert resp.status_code == 201, resp.text
        assert resp.json()["source_tool"] == tool
        assert resp.json()["source_fidelity"] == "wrapped"


def test_import_with_too_few_messages_is_insufficient(client, user):
    resp = client.post(
        f"{API}/sessions/import",
        json={"source_tool": "other", "messages": [{"role": "user", "content": "hi"}]},
        headers=user["headers"],
    )
    assert resp.status_code == 201
    detail = client.get(f"{API}/sessions/{resp.json()['id']}", headers=user["headers"]).json()
    assert detail["extraction_status"] == "insufficient_content"


def test_session_cross_user_isolation(client, user, other_user):
    session = import_rich_session(client, user["headers"])
    sid = session["id"]
    assert client.get(f"{API}/sessions/{sid}", headers=other_user["headers"]).status_code == 404
    assert (
        client.post(
            f"{API}/sessions/{sid}/messages",
            json={"role": "user", "content": "intrusion attempt"},
            headers=other_user["headers"],
        ).status_code
        == 404
    )
    assert client.post(f"{API}/sessions/{sid}/extract", headers=other_user["headers"]).status_code == 404
    # Other user's session list must not contain it.
    assert all(s["id"] != sid for s in client.get(f"{API}/sessions", headers=other_user["headers"]).json())


def test_import_into_foreign_project_denied(client, user, other_user):
    pid = client.post(f"{API}/projects", json={"name": "Theirs"}, headers=other_user["headers"]).json()["id"]
    resp = client.post(
        f"{API}/sessions/import",
        json={"project_id": pid, "source_tool": "cursor", "messages": [{"role": "user", "content": "x"}]},
        headers=user["headers"],
    )
    assert resp.status_code == 404
