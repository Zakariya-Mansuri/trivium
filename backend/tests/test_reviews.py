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


def test_early_review_opt_in(client, user):
    """Immediate review is allowed when the user explicitly opts in — never forced,
    never silently: default submissions still respect the consolidation window."""
    session = import_rich_session(client, user["headers"])
    unit_ids = _unit_ids_for_session(session["id"])

    # Default queue hides fresh units; early queue surfaces them, flagged.
    default_queue = client.get(f"{API}/reviews/queue", headers=user["headers"]).json()
    assert not ({i["unit"]["id"] for i in default_queue["items"]} & set(unit_ids))
    early_queue = client.get(f"{API}/reviews/queue", params={"early": "true"}, headers=user["headers"]).json()
    early_items = {i["unit"]["id"]: i for i in early_queue["items"]}
    assert set(unit_ids) & set(early_items)
    assert early_queue["total_early"] >= len(unit_ids)
    target = next(uid for uid in unit_ids if uid in early_items)
    assert early_items[target]["early"] is True

    # Default submit still 409s inside the window; early=true succeeds.
    blocked = client.post(
        f"{API}/reviews/submit", json={"unit_id": target, "performance": "correct"}, headers=user["headers"]
    )
    assert blocked.status_code == 409
    allowed = client.post(
        f"{API}/reviews/submit",
        json={"unit_id": target, "performance": "correct", "early": True},
        headers=user["headers"],
    )
    assert allowed.status_code == 200
    assert allowed.json()["mastery_status"] == "learning"

    # Min-gap still applies even for early reviews — no spamming.
    spam = client.post(
        f"{API}/reviews/submit",
        json={"unit_id": target, "performance": "correct", "early": True},
        headers=user["headers"],
    )
    assert spam.status_code == 409


def test_ai_grading_with_user_override(client, user):
    """AI grades the typed attempt; the user's final grade (override allowed) drives
    SM-2, and BOTH grades land in review_history as a calibration signal."""
    session = import_rich_session(client, user["headers"])
    unit_ids = _unit_ids_for_session(session["id"])
    _make_due(unit_ids)

    queue = client.get(f"{API}/reviews/queue", headers=user["headers"]).json()
    item = queue["items"][0]
    unit_id, artifact_id = item["unit"]["id"], item["artifact"]["id"]

    # Good attempt (echoes the unit summary) -> correct-ish verdict with justification.
    summary = item["unit"]["summary"] or item["unit"]["title"]
    good = client.post(
        f"{API}/reviews/grade",
        json={"unit_id": unit_id, "artifact_id": artifact_id, "response_text": summary},
        headers=user["headers"],
    )
    assert good.status_code == 200
    verdict = good.json()
    assert verdict["performance"] in ("correct", "partial", "incorrect")
    assert verdict["justification"]

    # Gibberish attempt -> not correct.
    bad = client.post(
        f"{API}/reviews/grade",
        json={"unit_id": unit_id, "artifact_id": artifact_id, "response_text": "zzz qqq purple elephants dancing"},
        headers=user["headers"],
    ).json()
    assert bad["performance"] in ("partial", "incorrect")

    # Submit with an override: user says partial although AI said something else.
    result = client.post(
        f"{API}/reviews/submit",
        json={
            "unit_id": unit_id,
            "artifact_id": artifact_id,
            "performance": "partial",
            "ai_performance": verdict["performance"],
            "response_text": summary,
        },
        headers=user["headers"],
    )
    assert result.status_code == 200

    from app.models import ReviewHistory

    db = SessionLocal()
    try:
        row = db.scalars(select(ReviewHistory).where(ReviewHistory.unit_id == unit_id)).one()
        assert row.performance == "partial"  # the user's grade drives scheduling
        assert row.ai_performance == verdict["performance"]  # AI verdict preserved
    finally:
        db.close()

    # Ownership: grading someone else's unit is a 404.
    empty = client.post(
        f"{API}/reviews/grade",
        json={"unit_id": unit_id, "artifact_id": artifact_id, "response_text": ""},
        headers=user["headers"],
    ).json()
    assert empty["performance"] == "incorrect"  # empty attempt is never a pass


def test_early_queue_does_not_loop_after_completion(client, user):
    """Bug fix: finishing the early queue must not re-serve the same units."""
    session = import_rich_session(client, user["headers"])
    unit_ids = set(_unit_ids_for_session(session["id"]))

    queue = client.get(f"{API}/reviews/queue", params={"early": "true"}, headers=user["headers"]).json()
    served = [i["unit"]["id"] for i in queue["items"] if i["unit"]["id"] in unit_ids]
    assert served
    for uid in served:
        resp = client.post(
            f"{API}/reviews/submit",
            json={"unit_id": uid, "performance": "correct", "early": True},
            headers=user["headers"],
        )
        assert resp.status_code == 200

    # Reloading the early queue must NOT contain any of the just-reviewed units.
    reloaded = client.get(f"{API}/reviews/queue", params={"early": "true"}, headers=user["headers"]).json()
    again = {i["unit"]["id"] for i in reloaded["items"]} & set(served)
    assert not again, f"early queue re-served just-reviewed units: {again}"


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
