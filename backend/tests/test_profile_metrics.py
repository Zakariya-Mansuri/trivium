"""Knowledge profile (evidence-based, visibility at generation) + metrics layers."""
from datetime import timedelta

from sqlalchemy import select, update

from app.db.base import utcnow
from app.db.session import SessionLocal
from app.models import KnowledgeUnit, ReviewState
from tests.conftest import import_rich_session

API = "/api/v1"


def _prepare_reviewed_user(client, user) -> list[str]:
    session = import_rich_session(client, user["headers"])
    db = SessionLocal()
    try:
        unit_ids = list(db.scalars(select(KnowledgeUnit.id).where(KnowledgeUnit.session_id == session["id"])).all())
        past = utcnow() - timedelta(hours=3)
        db.execute(
            update(ReviewState).where(ReviewState.unit_id.in_(unit_ids)).values(next_review_at=past, first_review_at=past)
        )
        db.commit()
    finally:
        db.close()
    client.post(
        f"{API}/reviews/submit", json={"unit_id": unit_ids[0], "performance": "correct"}, headers=user["headers"]
    )
    return unit_ids


def test_profile_reflects_review_evidence(client, user):
    unit_ids = _prepare_reviewed_user(client, user)
    profile = client.get(f"{API}/profile", headers=user["headers"]).json()
    by_unit = {e["unit"]["id"]: e for e in profile["entries"]}
    assert by_unit[unit_ids[0]]["mastery_status"] == "learning"  # evidence moved it
    others = [by_unit[u]["mastery_status"] for u in unit_ids[1:] if u in by_unit]
    assert all(s == "new" for s in others)  # unreviewed units stay 'new'
    assert profile["counts"].get("learning", 0) >= 1
    assert all(e["visibility"] == "private" for e in profile["entries"])  # private by default


def test_visibility_toggle_and_shared_export_enforced_at_generation(client, user):
    _prepare_reviewed_user(client, user)
    profile = client.get(f"{API}/profile", headers=user["headers"]).json()
    entries = profile["entries"]
    shared_entry = entries[0]

    toggled = client.patch(
        f"{API}/profile/entries/{shared_entry['entry_id']}/visibility",
        json={"visibility": "shared"},
        headers=user["headers"],
    )
    assert toggled.status_code == 200 and toggled.json()["visibility"] == "shared"

    private_md = client.get(f"{API}/profile/export", headers=user["headers"]).text
    shared_md = client.get(f"{API}/profile/export", params={"audience": "shared"}, headers=user["headers"]).text

    assert shared_entry["unit"]["title"] in private_md
    assert shared_entry["unit"]["title"] in shared_md
    # Private entries never enter the shared export.
    for e in entries[1:]:
        assert e["unit"]["title"] not in shared_md
    assert "evidence-based" in private_md


def test_visibility_isolation(client, user, other_user):
    _prepare_reviewed_user(client, user)
    entry_id = client.get(f"{API}/profile", headers=user["headers"]).json()["entries"][0]["entry_id"]
    foreign = client.patch(
        f"{API}/profile/entries/{entry_id}/visibility", json={"visibility": "shared"}, headers=other_user["headers"]
    )
    assert foreign.status_code == 404


def test_metrics_layers(client, user):
    unit_ids = _prepare_reviewed_user(client, user)
    session_id_resp = client.post(
        f"{API}/learn",
        json={"scope_type": "time_range", "time_start": "2000-01-01T00:00:00Z", "time_end": "2100-01-01T00:00:00Z"},
        headers=user["headers"],
    )
    assert session_id_resp.status_code == 200

    # Layer 1 — engagement events recorded.
    engagement = client.get(f"{API}/metrics/engagement", headers=user["headers"]).json()
    assert engagement["event_counts"].get("learn_triggered", 0) >= 1
    assert engagement["event_counts"].get("artifact_completed", 0) >= 1
    assert engagement["total_sessions"] >= 1

    # Layer 2 — retention curve over review history.
    retention = client.get(f"{API}/metrics/retention", headers=user["headers"]).json()
    assert retention["total_reviews"] >= 1
    day1 = next(b for b in retention["curve"] if b["bucket"] == "day_1")
    assert day1["reviews"] >= 1 and day1["accuracy"] is not None

    activity = client.get(f"{API}/metrics/activity", headers=user["headers"]).json()
    assert isinstance(activity, list) and len(activity) >= 1

    # Layer 3 (early) — AI-assist ratio from authored_by on code-bearing messages.
    independence = client.get(f"{API}/metrics/independence", headers=user["headers"]).json()
    assert "ai_assist_ratio" in independence


def test_metrics_are_per_user(client, user, other_user):
    _prepare_reviewed_user(client, user)
    other = client.get(f"{API}/metrics/retention", headers=other_user["headers"]).json()
    assert other["total_reviews"] == 0
