"""Spaced review engine — SM-2, diffuse-mode delay, interleaving, min gap."""
from datetime import timedelta

from sqlalchemy import select, update

from app.db.base import utcnow
from app.db.session import SessionLocal
from app.models import KnowledgeUnit, ReviewHistory, ReviewState
from tests.conftest import import_rich_session

API = "/api/v1"


def _unit_ids_for_session(session_id: str) -> list[str]:
    db = SessionLocal()
    try:
        return list(db.scalars(select(KnowledgeUnit.id).where(KnowledgeUnit.session_id == session_id)).all())
    finally:
        db.close()


def _make_due(unit_ids: list[str], hours_ago: int = 2) -> None:
    """Simulates time passing: moves next/first review into the past."""
    db = SessionLocal()
    try:
        past = utcnow() - timedelta(hours=hours_ago)
        db.execute(
            update(ReviewState)
            .where(ReviewState.unit_id.in_(unit_ids))
            .values(next_review_at=past, first_review_at=past)
        )
        db.commit()
    finally:
        db.close()


def test_diffuse_mode_delay_blocks_immediate_review(client, user):
    session = import_rich_session(client, user["headers"])
    unit_ids = _unit_ids_for_session(session["id"])
    assert unit_ids

    # Freshly extracted units must NOT appear in the queue (first review is delayed).
    queue = client.get(f"{API}/reviews/queue", headers=user["headers"]).json()
    queued_units = {item["unit"]["id"] for item in queue["items"]}
    assert not (queued_units & set(unit_ids))

    # Submitting a review early is rejected too.
    early = client.post(
        f"{API}/reviews/submit",
        json={"unit_id": unit_ids[0], "performance": "correct"},
        headers=user["headers"],
    )
    assert early.status_code == 409
    assert "diffuse" in early.json()["detail"].lower() or "not yet" in early.json()["detail"].lower()


def test_due_units_appear_and_sm2_updates_on_correct(client, user):
    session = import_rich_session(client, user["headers"])
    unit_ids = _unit_ids_for_session(session["id"])
    _make_due(unit_ids)

    queue = client.get(f"{API}/reviews/queue", headers=user["headers"]).json()
    queued = {item["unit"]["id"] for item in queue["items"]}
    assert set(unit_ids) <= queued or len(queued) > 0
    item = next(i for i in queue["items"] if i["unit"]["id"] in unit_ids)
    assert item["artifact"]["content"]  # each queue item carries a recall artifact

    result = client.post(
        f"{API}/reviews/submit",
        json={"unit_id": item["unit"]["id"], "artifact_id": item["artifact"]["id"],
              "performance": "correct", "response_text": "my recall answer"},
        headers=user["headers"],
    )
    assert result.status_code == 200
    body = result.json()
    assert body["mastery_status"] == "learning"
    assert body["interval_days"] == 1.0  # first correct -> 1 day
    assert body["ease_factor"] > 2.5  # ease rises on success

    # History row was written with day_offset.
    db = SessionLocal()
    try:
        h = db.scalars(select(ReviewHistory).where(ReviewHistory.unit_id == item["unit"]["id"])).all()
        assert len(h) == 1 and h[0].performance == "correct" and h[0].day_offset >= 0
    finally:
        db.close()


def test_min_gap_blocks_double_review(client, user):
    session = import_rich_session(client, user["headers"])
    unit_ids = _unit_ids_for_session(session["id"])
    _make_due(unit_ids)
    first = client.post(
        f"{API}/reviews/submit", json={"unit_id": unit_ids[0], "performance": "correct"}, headers=user["headers"]
    )
    assert first.status_code == 200
    again = client.post(
        f"{API}/reviews/submit", json={"unit_id": unit_ids[0], "performance": "correct"}, headers=user["headers"]
    )
    assert again.status_code == 409  # never twice within the minimum gap


def test_incorrect_resets_and_partial_softens(client, user):
    session = import_rich_session(client, user["headers"])
    unit_ids = _unit_ids_for_session(session["id"])
    _make_due(unit_ids)

    wrong = client.post(
        f"{API}/reviews/submit", json={"unit_id": unit_ids[0], "performance": "incorrect"}, headers=user["headers"]
    ).json()
    assert wrong["interval_days"] == 1.0 and wrong["ease_factor"] == 2.2  # 2.5 - 0.3

    if len(unit_ids) > 1:
        partial = client.post(
            f"{API}/reviews/submit", json={"unit_id": unit_ids[1], "performance": "partial"}, headers=user["headers"]
        ).json()
        assert partial["ease_factor"] == 2.35  # 2.5 - 0.15
        assert partial["interval_days"] >= 1.0


def test_interleaving_across_projects(client, user):
    p1 = client.post(f"{API}/projects", json={"name": "Interleave A"}, headers=user["headers"]).json()["id"]
    p2 = client.post(f"{API}/projects", json={"name": "Interleave B"}, headers=user["headers"]).json()["id"]
    s1 = import_rich_session(client, user["headers"], project_id=p1)
    s2 = import_rich_session(client, user["headers"], project_id=p2, tool="cursor")
    _make_due(_unit_ids_for_session(s1["id"]) + _unit_ids_for_session(s2["id"]))

    queue = client.get(f"{API}/reviews/queue", headers=user["headers"]).json()
    projects_in_queue = {item["unit"]["project_id"] for item in queue["items"]}
    assert {p1, p2} <= projects_in_queue  # session mixes >= 2 projects
    assert queue["projects_in_session"] >= 2


def test_review_isolation_and_unknown_unit(client, user, other_user):
    session = import_rich_session(client, user["headers"])
    unit_ids = _unit_ids_for_session(session["id"])
    _make_due(unit_ids)
    foreign = client.post(
        f"{API}/reviews/submit", json={"unit_id": unit_ids[0], "performance": "correct"}, headers=other_user["headers"]
    )
    assert foreign.status_code == 404
    ghost = client.post(
        f"{API}/reviews/submit",
        json={"unit_id": "00000000-0000-0000-0000-000000000000", "performance": "correct"},
        headers=user["headers"],
    )
    assert ghost.status_code == 404
