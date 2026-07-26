"""Learn action, format selection rules, artifact generation."""
from tests.conftest import import_rich_session

API = "/api/v1"


def test_learn_chat_scope_generates_recall_artifacts(client, user):
    session = import_rich_session(client, user["headers"])
    resp = client.post(
        f"{API}/learn", json={"scope_type": "chat", "session_id": session["id"]}, headers=user["headers"]
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["units_covered"] >= 2
    assert len(body["artifacts"]) >= 1
    formats = {a["format"] for a in body["artifacts"]}
    # Rule table: bug_fix -> retrieval_practice; decision -> qa/self_explanation.
    assert "retrieval_practice" in formats
    assert formats & {"qa", "self_explanation"}
    for a in body["artifacts"]:
        assert a["triggered_by"] == "user_action"
        assert a["scope_type"] == "chat"
        content = a["content"]
        # Recall-first: choices exist ONLY in the explicit MCQ supplement.
        if a["format"] != "mcq":
            assert "choices" not in str(content)
        if content["type"] == "qa":
            assert all(q["kind"] == "recall" for q in content["questions"])


def test_learn_insufficient_content_is_communicated(client, user):
    empty = client.post(f"{API}/sessions", json={"title": "empty"}, headers=user["headers"]).json()
    resp = client.post(
        f"{API}/learn", json={"scope_type": "chat", "session_id": empty["id"]}, headers=user["headers"]
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["artifacts"] == []
    assert body["units_covered"] == 0
    assert body["message"] is not None and "enough" in body["message"].lower()


def test_learn_project_and_time_range_scopes(client, user):
    pid = client.post(f"{API}/projects", json={"name": "ScopeProj"}, headers=user["headers"]).json()["id"]
    import_rich_session(client, user["headers"], project_id=pid)

    proj = client.post(
        f"{API}/learn", json={"scope_type": "project", "project_id": pid}, headers=user["headers"]
    )
    assert proj.status_code == 200 and proj.json()["units_covered"] >= 2

    time_range = client.post(
        f"{API}/learn",
        json={"scope_type": "time_range", "time_start": "2000-01-01T00:00:00Z", "time_end": "2100-01-01T00:00:00Z"},
        headers=user["headers"],
    )
    assert time_range.status_code == 200 and time_range.json()["units_covered"] >= 2

    inverted = client.post(
        f"{API}/learn",
        json={"scope_type": "time_range", "time_start": "2100-01-01T00:00:00Z", "time_end": "2000-01-01T00:00:00Z"},
        headers=user["headers"],
    )
    assert inverted.status_code == 422


def test_learn_message_scope(client, user):
    session = import_rich_session(client, user["headers"])
    detail = client.get(f"{API}/sessions/{session['id']}", headers=user["headers"]).json()
    message_id = detail["messages"][1]["id"]  # rich assistant message
    resp = client.post(
        f"{API}/learn", json={"scope_type": "message", "message_id": message_id}, headers=user["headers"]
    )
    assert resp.status_code == 200
    assert resp.json()["units_covered"] >= 1


def test_learn_scope_validation_and_isolation(client, user, other_user):
    assert client.post(f"{API}/learn", json={"scope_type": "chat"}, headers=user["headers"]).status_code == 422
    session = import_rich_session(client, user["headers"])
    foreign = client.post(
        f"{API}/learn", json={"scope_type": "chat", "session_id": session["id"]}, headers=other_user["headers"]
    )
    assert foreign.status_code == 404


def test_artifact_listing_get_and_isolation(client, user, other_user):
    session = import_rich_session(client, user["headers"])
    learn = client.post(
        f"{API}/learn", json={"scope_type": "chat", "session_id": session["id"]}, headers=user["headers"]
    ).json()
    artifact_id = learn["artifacts"][0]["id"]
    assert client.get(f"{API}/artifacts/{artifact_id}", headers=user["headers"]).status_code == 200
    assert client.get(f"{API}/artifacts/{artifact_id}", headers=other_user["headers"]).status_code == 404
    mine = client.get(f"{API}/artifacts", headers=user["headers"]).json()
    assert any(a["id"] == artifact_id for a in mine)


def test_completing_artifact_never_updates_mastery(client, user):
    """Illusions-of-competence guard: passive completion must not touch review state."""
    session = import_rich_session(client, user["headers"])
    learn = client.post(
        f"{API}/learn", json={"scope_type": "chat", "session_id": session["id"]}, headers=user["headers"]
    ).json()
    artifact_id = learn["artifacts"][0]["id"]

    before = client.get(f"{API}/profile", headers=user["headers"]).json()
    statuses_before = {e["unit"]["id"]: e["mastery_status"] for e in before["entries"]}
    assert all(s == "new" for s in statuses_before.values() if s)

    done = client.post(f"{API}/artifacts/{artifact_id}/complete", headers=user["headers"])
    assert done.status_code == 200 and done.json()["completed_at"] is not None

    after = client.get(f"{API}/profile", headers=user["headers"]).json()
    statuses_after = {e["unit"]["id"]: e["mastery_status"] for e in after["entries"]}
    assert statuses_before == statuses_after  # unchanged — only recall submissions move mastery


def test_learn_includes_mcq_supplement(client, user):
    """Every Learn produces an additional MCQ quiz (recognition supplement) with
    exactly one correct choice per question."""
    session = import_rich_session(client, user["headers"])
    body = client.post(
        f"{API}/learn", json={"scope_type": "chat", "session_id": session["id"]}, headers=user["headers"]
    ).json()
    mcq = next((a for a in body["artifacts"] if a["format"] == "mcq"), None)
    assert mcq is not None
    questions = mcq["content"]["questions"]
    assert len(questions) >= 1
    for q in questions:
        assert len(q["choices"]) >= 3
        assert 0 <= q["correct_index"] < len(q["choices"])
        assert q["explanation"]


def test_mermaid_sanitizer_repairs_llm_output():
    from app.services.artifacts import sanitize_mermaid

    raw = """```mermaid
flowchart TB
  A[Uvicorn Host Binding: default 127.0.0.1] --> B[Need network access]
  B --> H2[Tunneling service (ngrok, Cloudflare)]
```"""
    fixed = sanitize_mermaid(raw)
    assert "```" not in fixed
    assert 'A["Uvicorn Host Binding: default 127.0.0.1"]' in fixed
    assert 'H2["Tunneling service (ngrok, Cloudflare)"]' in fixed
    # Already-quoted labels and bare edges are left alone.
    ok = 'flowchart TD\n  A["Fine"] --> B["Also fine"]'
    assert sanitize_mermaid(ok) == ok
    # Missing header gets one.
    assert sanitize_mermaid("A --> B").startswith("flowchart TD")


def test_llm_outage_returns_503_not_500(client, user, monkeypatch):
    """When the provider is down/rate-limited after retries, Learn degrades to a
    clear retryable 503 — never a 500, never silent mock content."""
    from app.llm.base import LLMError, LLMProvider
    from app.services import artifacts as artifacts_service

    class DownProvider(LLMProvider):
        name = "down"

        def complete(self, messages, *, json_mode=False, max_tokens=2048):
            raise LLMError("rate limited (429) after retries")

    session = import_rich_session(client, user["headers"])  # extraction runs with the mock, fine
    monkeypatch.setattr(artifacts_service, "get_llm", lambda *a, **k: DownProvider())

    resp = client.post(
        f"{API}/learn", json={"scope_type": "chat", "session_id": session["id"]}, headers=user["headers"]
    )
    assert resp.status_code == 503
    assert "try again" in resp.json()["detail"].lower()
    assert resp.headers.get("retry-after") == "30"


def test_llm_outage_marks_extraction_failed_and_retryable(client, user, monkeypatch):
    from app.llm.base import LLMError, LLMProvider
    from app.services import extraction as extraction_service

    class DownProvider(LLMProvider):
        name = "down"

        def complete(self, messages, *, json_mode=False, max_tokens=2048):
            raise LLMError("rate limited (429) after retries")

    monkeypatch.setattr(extraction_service, "get_llm", lambda *a, **k: DownProvider())
    monkeypatch.setattr(extraction_service, "EXTRACTION_RETRY_DELAYS_SECONDS", (0.0,))

    session = import_rich_session(client, user["headers"])
    detail = client.get(f"{API}/sessions/{session['id']}", headers=user["headers"]).json()
    assert detail["extraction_status"] == "failed"

    # Manual re-extract works once the provider is back (monkeypatch undone via new provider).
    monkeypatch.setattr(extraction_service, "get_llm", lambda *a, **k: __import__("app.llm.mock", fromlist=["MockProvider"]).MockProvider())
    retry = client.post(f"{API}/sessions/{session['id']}/extract", headers=user["headers"])
    assert retry.status_code == 200
    detail = client.get(f"{API}/sessions/{session['id']}", headers=user["headers"]).json()
    assert detail["extraction_status"] == "completed"


def test_format_decisions_are_logged(client, user):
    """Every format choice must be auditable (PRD 6.2)."""
    from sqlalchemy import select

    from app.db.session import SessionLocal
    from app.models import FormatDecision, KnowledgeUnit

    session = import_rich_session(client, user["headers"])
    client.post(f"{API}/learn", json={"scope_type": "chat", "session_id": session["id"]}, headers=user["headers"])

    db = SessionLocal()
    try:
        unit_ids = db.scalars(
            select(KnowledgeUnit.id).where(KnowledgeUnit.session_id == session["id"])
        ).all()
        decisions = db.scalars(select(FormatDecision).where(FormatDecision.unit_id.in_(unit_ids))).all()
        assert len(decisions) >= len(unit_ids)
        for d in decisions:
            assert d.rule_version == "v1.0"
            assert d.signal  # the triggering signal is recorded
    finally:
        db.close()
