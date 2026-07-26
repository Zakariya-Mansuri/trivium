"""Language/prompting skill reports + gap recommendations."""
from datetime import timedelta

from sqlalchemy import select, update

from app.data.resources import CATALOG
from app.db.base import utcnow
from app.db.session import SessionLocal
from app.models import KnowledgeUnit, ReviewState
from tests.conftest import import_rich_session

API = "/api/v1"

CATALOG_URLS = {entry["url"] for entry in CATALOG}


def test_insufficient_data_is_communicated(client, user):
    resp = client.get(f"{API}/skills/language", headers=user["headers"])
    assert resp.status_code == 200
    body = resp.json()
    assert body["insufficient"] is True
    assert "messages" in body["message"].lower()


def _seed_messages(client, headers):
    # Two imports -> 6 user-authored messages, enough for analysis.
    import_rich_session(client, headers)
    import_rich_session(client, headers, tool="cursor")


def test_language_report_structure_and_caching(client, user):
    _seed_messages(client, user["headers"])
    first = client.get(f"{API}/skills/language", headers=user["headers"]).json()
    assert first["report_type"] == "language"
    content = first["content"]
    assert content["metrics"]["messages_analyzed"] >= 5
    analysis = content["analysis"]
    assert 0 <= analysis["overall_score"] <= 100
    assert set(analysis["sub_scores"]) == {"clarity", "grammar", "vocabulary", "structure", "tone"}
    assert analysis["weaknesses"] and all("tip" in w for w in analysis["weaknesses"])
    # Resources come only from the curated credible catalog, language-skill only.
    assert content["resources"]
    for r in content["resources"]:
        assert r["url"] in CATALOG_URLS
        assert r["skill"] == "language"

    # Cached on second call; refresh recomputes.
    second = client.get(f"{API}/skills/language", headers=user["headers"]).json()
    assert second["computed_at"] == first["computed_at"]
    refreshed = client.get(f"{API}/skills/language", params={"refresh": "true"}, headers=user["headers"]).json()
    assert refreshed["computed_at"] >= first["computed_at"]


def test_prompting_report_is_separate_component(client, user):
    _seed_messages(client, user["headers"])
    lang = client.get(f"{API}/skills/language", headers=user["headers"]).json()
    prompting = client.get(f"{API}/skills/prompting", headers=user["headers"]).json()
    assert prompting["report_type"] == "prompting"
    assert set(prompting["content"]["analysis"]["sub_scores"]) == {
        "context", "specificity", "constraints", "output_format", "iteration",
    }
    # Different dimensions and resource pools than the language report.
    assert prompting["content"]["analysis"]["sub_scores"] != lang["content"]["analysis"]["sub_scores"]
    for r in prompting["content"]["resources"]:
        assert r["skill"] == "prompting"
        assert r["url"] in CATALOG_URLS


def test_gap_recommendations_from_weak_areas(client, user):
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
    # Fail a recall -> that unit becomes a documented gap.
    client.post(
        f"{API}/reviews/submit", json={"unit_id": unit_ids[0], "performance": "incorrect"}, headers=user["headers"]
    )
    gaps = client.get(f"{API}/skills/recommendations", headers=user["headers"]).json()["gaps"]
    assert gaps
    failed = next((g for g in gaps if "last recall failed" in g["reasons"]), None)
    assert failed is not None
    assert failed["resources"] and all(r["url"] in CATALOG_URLS and r["skill"] == "coding" for r in failed["resources"])


def test_skills_are_per_user(client, user, other_user):
    _seed_messages(client, user["headers"])
    mine = client.get(f"{API}/skills/language", headers=user["headers"]).json()
    assert mine["content"]["metrics"]["messages_analyzed"] >= 5
    theirs = client.get(f"{API}/skills/language", headers=other_user["headers"]).json()
    assert theirs.get("insufficient") is True
