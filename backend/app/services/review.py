"""Spaced Review Engine.

Learning-science constraints implemented here (PRD §7 / tech doc §6):
- Adaptive SM-2-style intervals per unit, adjusted by performance.
- Diffuse-mode delay: a unit is never reviewable before review_state.first_review_at.
- Minimum gap: the same unit is never reviewed twice within MIN_REVIEW_GAP_HOURS.
- Interleaving: a review session pulls from >=2 distinct projects when available.
- Only recall-based completions write to review_state — passive viewing never does.
"""
from datetime import timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.core.config import settings
from app.db.base import utcnow
from app.llm import get_llm
from app.models import (
    KnowledgeUnit,
    LearningArtifact,
    LearningArtifactUnit,
    ReviewHistory,
    ReviewState,
    User,
)
from app.schemas.learning import ReviewSubmission
from app.services import format_selection
from app.services.artifacts import create_artifact
from app.services.metrics import log_event

EASE_MIN, EASE_MAX = 1.3, 3.0

GRADING_SYSTEM_PROMPT = """[TASK:grade_recall]
You grade a learner's recall attempt against reference material from their own past coding work.
Judge RECALL of the substance, not writing style: paraphrases and partial wording count.
- correct: the attempt captures the key point(s) of the reference
- partial: some of it, or vague/incomplete
- incorrect: wrong, empty of substance, or unrelated
The user message is JSON: {"question": "...", "reference": "...", "attempt": "..."}.
Respond ONLY with JSON: {"performance": "correct"|"partial"|"incorrect", "justification": "one short sentence"}"""


def _reference_text(artifact: LearningArtifact) -> tuple[str, str]:
    """Returns (question_text, reference_answer_text) for gradeable recall formats."""
    c = artifact.content or {}
    kind = c.get("type")
    if kind == "retrieval_practice":
        qs = c.get("questions", [])
        return (
            " / ".join(q.get("question", "") for q in qs),
            " / ".join(q.get("answer", "") for q in qs),
        )
    if kind == "qa":
        qs = c.get("questions", [])
        return (
            " / ".join(q.get("question", "") for q in qs),
            " / ".join(" ; ".join(q.get("expected_points", [])) for q in qs),
        )
    if kind == "self_explanation":
        ps = c.get("prompts", [])
        return (
            " / ".join(p.get("prompt", "") for p in ps),
            " / ".join(p.get("context", "") for p in ps),
        )
    if kind == "synthesis":
        return c.get("prompt", ""), ", ".join(c.get("related_titles", []))
    if kind == "flashcard":
        cards = c.get("cards", [])
        return (
            " / ".join(card.get("front", "") for card in cards),
            " / ".join(card.get("back", "") for card in cards),
        )
    return "", ""


def grade_recall(db: DBSession, user: User, unit_id: str, artifact_id: str, response_text: str) -> dict:
    """AI-suggested grade for a typed recall attempt. The user can override —
    both grades are stored, giving a calibration signal over time."""
    import json as _json

    unit = db.get(KnowledgeUnit, unit_id)
    if unit is None or unit.user_id != user.id or unit.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Knowledge unit not found")
    artifact = db.get(LearningArtifact, artifact_id)
    if artifact is None or artifact.user_id != user.id:
        raise HTTPException(status_code=404, detail="Artifact not found")

    question, reference = _reference_text(artifact)
    if not reference.strip():
        return {"performance": None, "justification": "No reference answer for this format — grade yourself."}
    if not response_text.strip():
        return {"performance": "incorrect", "justification": "No attempt was written."}

    payload = _json.dumps(
        {
            "question": question[:2000],
            "reference": f"{reference[:3000]}\nUnit: {unit.title}. {unit.summary or ''}"[:4000],
            "attempt": response_text[:4000],
        }
    )
    raw = get_llm(user).complete(
        [{"role": "system", "content": GRADING_SYSTEM_PROMPT}, {"role": "user", "content": payload}],
        json_mode=True,
        max_tokens=300,
    )
    try:
        verdict = _json.loads(raw)
        if verdict.get("performance") not in ("correct", "partial", "incorrect"):
            raise ValueError("bad performance value")
        return {"performance": verdict["performance"], "justification": str(verdict.get("justification", ""))[:500]}
    except (ValueError, TypeError, _json.JSONDecodeError):
        return {"performance": None, "justification": "The grader returned an unreadable verdict — grade yourself."}


def _due_states(db: DBSession, user_id: str) -> list[tuple[ReviewState, KnowledgeUnit]]:
    now = utcnow()
    rows = db.execute(
        select(ReviewState, KnowledgeUnit)
        .join(KnowledgeUnit, KnowledgeUnit.id == ReviewState.unit_id)
        .where(
            ReviewState.user_id == user_id,
            ReviewState.next_review_at <= now,
            ReviewState.first_review_at <= now,  # diffuse-mode gate
            KnowledgeUnit.deleted_at.is_(None),
        )
        .order_by(ReviewState.next_review_at)
    ).all()
    return [(state, unit) for state, unit in rows]


def _early_states(db: DBSession, user_id: str) -> list[tuple[ReviewState, KnowledgeUnit]]:
    """Units NOT yet due (still scheduled ahead or inside the consolidation window).
    Units reviewed within the minimum gap are excluded — otherwise a just-graded
    unit becomes "upcoming" again and the early queue loops forever."""
    now = utcnow()
    gap_cutoff = now - timedelta(hours=settings.MIN_REVIEW_GAP_HOURS)
    recently_reviewed = (
        select(ReviewHistory.unit_id)
        .where(ReviewHistory.user_id == user_id, ReviewHistory.reviewed_at > gap_cutoff)
        .scalar_subquery()
    )
    rows = db.execute(
        select(ReviewState, KnowledgeUnit)
        .join(KnowledgeUnit, KnowledgeUnit.id == ReviewState.unit_id)
        .where(
            ReviewState.user_id == user_id,
            (ReviewState.next_review_at > now) | (ReviewState.first_review_at > now),
            ReviewState.unit_id.notin_(recently_reviewed),
            KnowledgeUnit.deleted_at.is_(None),
        )
        .order_by(ReviewState.next_review_at)
    ).all()
    return [(state, unit) for state, unit in rows]


def _interleave(pairs: list[tuple[ReviewState, KnowledgeUnit]], limit: int) -> list[tuple[ReviewState, KnowledgeUnit]]:
    """Round-robin across projects so a session mixes >=2 projects where available."""
    by_project: dict[str | None, list] = {}
    for pair in pairs:
        by_project.setdefault(pair[1].project_id, []).append(pair)
    buckets = list(by_project.values())
    result, i = [], 0
    while len(result) < limit and any(buckets):
        bucket = buckets[i % len(buckets)]
        if bucket:
            result.append(bucket.pop(0))
        i += 1
        if i > limit * max(len(buckets), 1) * 2:
            break
    return result


def _artifact_for_unit(db: DBSession, user: User, unit: KnowledgeUnit) -> LearningArtifact:
    """Reuse the latest RECALL artifact covering this unit, else generate one.
    The scope-level mcq/diagram supplements are excluded — reviews are recall-first
    (testing effect); recognition checks live in the Learn flow."""
    existing = db.execute(
        select(LearningArtifact)
        .join(LearningArtifactUnit, LearningArtifactUnit.artifact_id == LearningArtifact.id)
        .where(
            LearningArtifactUnit.unit_id == unit.id,
            LearningArtifact.user_id == user.id,
            LearningArtifact.format.notin_(("mcq", "diagram")),
        )
        .order_by(LearningArtifact.generated_at.desc())
        .limit(1)
    ).scalar_one_or_none()
    if existing is not None:
        return existing
    fmt = format_selection.choose_format(db, unit)
    return create_artifact(
        db, user, "chat", {"session_id": unit.session_id}, fmt, [unit], "scheduled_review"
    )


def build_queue(db: DBSession, user: User, include_early: bool = False) -> dict:
    """Due items first (interleaved). With include_early=True — an explicit user
    choice — remaining slots are filled with not-yet-due units so the user can
    review immediately after learning if they want to."""
    due = _due_states(db, user.id)
    early = _early_states(db, user.id)
    selected = [(s, u, False) for s, u in _interleave(due, settings.REVIEW_SESSION_SIZE)]
    if include_early and len(selected) < settings.REVIEW_SESSION_SIZE:
        room = settings.REVIEW_SESSION_SIZE - len(selected)
        selected += [(s, u, True) for s, u in _interleave(early, room)]
    items = []
    for state, unit, is_early in selected:
        artifact = _artifact_for_unit(db, user, unit)
        items.append({"state": state, "unit": unit, "artifact": artifact, "early": is_early})
    db.commit()

    next_due = db.scalar(
        select(ReviewState.next_review_at)
        .join(KnowledgeUnit, KnowledgeUnit.id == ReviewState.unit_id)
        .where(
            ReviewState.user_id == user.id,
            ReviewState.next_review_at > utcnow(),
            KnowledgeUnit.deleted_at.is_(None),
        )
        .order_by(ReviewState.next_review_at)
        .limit(1)
    )
    projects = {unit.project_id for _, unit, _ in selected}
    return {
        "items": items,
        "total_due": len(due),
        "total_early": len(early),
        "projects_in_session": len(projects),
        "next_due_at": next_due,
    }


def _apply_sm2(state: ReviewState, performance: str) -> None:
    interval = float(state.interval_days)
    ease = float(state.ease_factor)

    if performance == "correct":
        state.consecutive_correct += 1
        if state.consecutive_correct == 1:
            interval = 1.0
        elif state.consecutive_correct == 2:
            interval = 6.0
        else:
            interval = round(interval * ease, 2)
        ease = min(EASE_MAX, ease + 0.05)
    elif performance == "partial":
        interval = max(1.0, round(interval * 0.5, 2))
        ease = max(EASE_MIN, ease - 0.15)
    else:  # incorrect — relearn
        state.consecutive_correct = 0
        interval = 1.0
        ease = max(EASE_MIN, ease - 0.3)

    state.interval_days = interval
    state.ease_factor = round(ease, 2)
    gap = max(timedelta(days=interval), timedelta(hours=settings.MIN_REVIEW_GAP_HOURS))
    state.next_review_at = utcnow() + gap

    if state.consecutive_correct >= 3 and interval >= 21:
        state.mastery_status = "consolidated"
    elif state.consecutive_correct >= 1 or performance in ("partial", "incorrect"):
        state.mastery_status = "learning"


def submit_review(db: DBSession, user: User, submission: ReviewSubmission) -> ReviewState:
    unit = db.get(KnowledgeUnit, submission.unit_id)
    if unit is None or unit.user_id != user.id or unit.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Knowledge unit not found")
    state = db.execute(
        select(ReviewState).where(ReviewState.user_id == user.id, ReviewState.unit_id == unit.id)
    ).scalar_one_or_none()
    if state is None:
        raise HTTPException(status_code=404, detail="No review state for this unit")

    now = utcnow()
    if state.first_review_at is not None and now < state.first_review_at:
        if not submission.early:
            raise HTTPException(
                status_code=409,
                detail="This concept is in its consolidation window (diffuse-mode delay) and is not yet reviewable. "
                "Pass early=true to review it now anyway.",
            )
        # Explicit user choice — reviewing early is allowed, never forced (opt-in principle).
        state.first_review_at = now
    last = db.scalar(
        select(ReviewHistory.reviewed_at)
        .where(ReviewHistory.user_id == user.id, ReviewHistory.unit_id == unit.id)
        .order_by(ReviewHistory.reviewed_at.desc())
        .limit(1)
    )
    if last is not None and now - last < timedelta(hours=settings.MIN_REVIEW_GAP_HOURS):
        raise HTTPException(
            status_code=409,
            detail=f"This concept was reviewed within the last {settings.MIN_REVIEW_GAP_HOURS} hours — spacing matters.",
        )

    if submission.artifact_id is not None:
        artifact = db.get(LearningArtifact, submission.artifact_id)
        if artifact is None or artifact.user_id != user.id:
            raise HTTPException(status_code=404, detail="Artifact not found")
        artifact.completed_at = now

    day_offset = max(0, (now - unit.extracted_at).days)
    db.add(
        ReviewHistory(
            user_id=user.id,
            unit_id=unit.id,
            artifact_id=submission.artifact_id,
            performance=submission.performance,
            ai_performance=submission.ai_performance,
            response_text=submission.response_text,
            day_offset=day_offset,
        )
    )
    _apply_sm2(state, submission.performance)
    log_event(db, user.id, "artifact_completed", {"unit_id": unit.id, "performance": submission.performance})

    remaining = [s for s, _ in _due_states(db, user.id) if s.unit_id != unit.id]
    if not remaining:
        log_event(db, user.id, "queue_cleared", None)

    db.commit()
    db.refresh(state)
    return state
