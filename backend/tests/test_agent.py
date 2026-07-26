"""Native agent chat — authored_by correctness is critical (Layer 3 depends on it)."""
API = "/api/v1"


def test_chat_creates_session_and_tags_authorship(client, user):
    resp = client.post(
        f"{API}/agent/chat",
        json={"message": "Help me fix a bug in my fastapi async endpoint"},
        headers=user["headers"],
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["user_message"]["authored_by"] == "user"
    assert body["assistant_message"]["authored_by"] == "ai"
    assert body["assistant_message"]["role"] == "assistant"
    assert len(body["assistant_message"]["content"]) > 20

    # Session was created as native fidelity.
    session = client.get(f"{API}/sessions/{body['session_id']}", headers=user["headers"]).json()
    assert session["source_tool"] == "native" and session["source_fidelity"] == "native"
    assert len(session["messages"]) == 2


def test_chat_continues_existing_session(client, user):
    first = client.post(f"{API}/agent/chat", json={"message": "Explain react hooks"}, headers=user["headers"]).json()
    sid = first["session_id"]
    second = client.post(
        f"{API}/agent/chat", json={"session_id": sid, "message": "And what about useEffect cleanup?"},
        headers=user["headers"],
    )
    assert second.status_code == 200
    session = client.get(f"{API}/sessions/{sid}", headers=user["headers"]).json()
    assert len(session["messages"]) == 4


def test_chat_rejects_foreign_and_ended_sessions(client, user, other_user):
    first = client.post(f"{API}/agent/chat", json={"message": "hello python"}, headers=user["headers"]).json()
    sid = first["session_id"]
    foreign = client.post(
        f"{API}/agent/chat", json={"session_id": sid, "message": "hijack"}, headers=other_user["headers"]
    )
    assert foreign.status_code == 404
    client.post(f"{API}/sessions/{sid}/end", headers=user["headers"])
    ended = client.post(
        f"{API}/agent/chat", json={"session_id": sid, "message": "more"}, headers=user["headers"]
    )
    assert ended.status_code == 409
