"""Metrics & Analytics Layer.

Layer 1 (engagement): metrics_events written on key actions.
Layer 2 (retention): aggregations over review_history (day_offset x performance).
Layer 3 (independence): ai_assist_ratio computed on demand from messages.authored_by —
the underlying data is captured correctly from day one even though Layer 3 is
staged for later per the PRD.
"""
from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session as DBSession

from app.db.base import utcnow
from app.models import Message, MetricsEvent, ReviewHistory, Session

# Retention buckets approximating "accuracy at day 1 / 7 / 30".
RETENTION_BUCKETS = [
    ("day_1", 0, 2),
    ("day_7", 3, 10),
    ("day_30", 11, 45),
    ("day_90", 46, 3650),
]

PERFORMANCE_SCORE = {"correct": 1.0, "partial": 0.5, "incorrect": 0.0}


def log_event(db: DBSession, user_id: str, event_type: str, metadata: dict | None = None) -> None:
    db.add(MetricsEvent(user_id=user_id, event_type=event_type, event_metadata=metadata))


def engagement_summary(db: DBSession, user_id: str) -> dict:
    rows = db.execute(
        select(MetricsEvent.event_type, func.count())
        .where(MetricsEvent.user_id == user_id)
        .group_by(MetricsEvent.event_type)
    ).all()
    counts = {event_type: count for event_type, count in rows}
    total_sessions = db.scalar(select(func.count()).select_from(Session).where(Session.user_id == user_id)) or 0
    learn_triggers = counts.get("learn_triggered", 0)
    return {
        "event_counts": counts,
        "total_sessions": total_sessions,
        "learn_usage_rate": round(min(learn_triggers / total_sessions, 1.0), 3) if total_sessions else 0.0,
    }


def retention_curve(db: DBSession, user_id: str) -> dict:
    rows = db.execute(
        select(ReviewHistory.day_offset, ReviewHistory.performance).where(ReviewHistory.user_id == user_id)
    ).all()
    curve = []
    for label, lo, hi in RETENTION_BUCKETS:
        bucket = [PERFORMANCE_SCORE[p] for d, p in rows if lo <= d <= hi]
        curve.append(
            {
                "bucket": label,
                "reviews": len(bucket),
                "accuracy": round(sum(bucket) / len(bucket), 3) if bucket else None,
            }
        )
    total = [PERFORMANCE_SCORE[p] for _, p in rows]
    return {
        "curve": curve,
        "total_reviews": len(total),
        "overall_recall_rate": round(sum(total) / len(total), 3) if total else None,
    }


def review_activity(db: DBSession, user_id: str, days: int = 90) -> list[dict]:
    """Daily review counts for the contribution-style activity graph."""
    since = utcnow() - timedelta(days=days)
    rows = db.execute(
        select(ReviewHistory.reviewed_at, ReviewHistory.performance).where(
            ReviewHistory.user_id == user_id, ReviewHistory.reviewed_at >= since
        )
    ).all()
    by_day: dict[str, dict] = {}
    for reviewed_at, performance in rows:
        key = reviewed_at.date().isoformat()
        day = by_day.setdefault(key, {"date": key, "reviews": 0, "correct": 0})
        day["reviews"] += 1
        if performance == "correct":
            day["correct"] += 1
    return sorted(by_day.values(), key=lambda d: d["date"])


def ai_assist_ratio(db: DBSession, user_id: str, window_days: int = 30) -> dict:
    since = utcnow() - timedelta(days=window_days)
    rows = db.execute(
        select(Message.authored_by, func.count())
        .join(Session, Session.id == Message.session_id)
        .where(
            Session.user_id == user_id,
            Message.created_at >= since,
            Message.authored_by.is_not(None),
            Message.code_diff.is_not(None),
        )
        .group_by(Message.authored_by)
    ).all()
    counts = {authored_by: count for authored_by, count in rows}
    ai = counts.get("ai", 0)
    user_written = counts.get("user", 0)
    total = ai + user_written
    return {
        "window_days": window_days,
        "ai_authored": ai,
        "user_authored": user_written,
        "ai_assist_ratio": round(ai / total, 3) if total else None,
        "note": "Derived from messages.authored_by on code-bearing messages; trends downward as independence grows.",
    }
