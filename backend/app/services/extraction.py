"""Extraction & Indexing Engine.

Turns raw session messages into typed knowledge_units, creates review_state
rows (with the diffuse-mode delay applied to the first review), and links
recurring concepts across sessions via knowledge_unit_relations.

Runs in the background via FastAPI BackgroundTasks behind this plain function —
swapping in a Redis/arq worker later only means calling the same function
from a worker instead.
"""
import json
import logging
import re
import time
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.core.config import settings
from app.db.base import utcnow
from app.db.session import SessionLocal
from app.llm import get_llm
from app.llm.base import LLMError
from app.models import KnowledgeUnit, KnowledgeUnitRelation, Message, ReviewState, Session

logger = logging.getLogger(__name__)

# Extra waits between whole-extraction retries when the provider is rate-limited
# (on top of the per-request retries inside the provider). Background thread only.
EXTRACTION_RETRY_DELAYS_SECONDS: tuple[float, ...] = (20.0, 60.0)

VALID_UNIT_TYPES = {"concept", "decision", "bug_fix", "pattern"}
VALID_DIFFICULTIES = {"novice", "intermediate", "advanced"}

EXTRACTION_SYSTEM_PROMPT = """[TASK:extraction]
You analyze a coding-session transcript and extract discrete knowledge units.
Each unit is one of: concept (something learned/used), decision (a choice with tradeoffs),
bug_fix (a problem and its fix), pattern (something recurring across work).
Return JSON: {"units": [{"unit_type": "...", "title": "...", "summary": "...",
"difficulty": "novice|intermediate|advanced", "signal": "what triggered this classification",
"concepts": ["related", "terms"]}]}
Extract at most 8 high-quality units. Skip small talk. Titles must be specific, not generic."""


def build_transcript(messages: list[Message]) -> str:
    parts = []
    for m in messages:
        text = f"[{m.role}] {m.content}"
        if m.code_diff:
            text += f"\n(code diff)\n{m.code_diff[:2000]}"
        parts.append(text)
    return "\n".join(parts)


def normalize_title(title: str) -> str:
    """Reduce a title to its core term for cross-session recurrence matching."""
    t = title.lower()
    for prefix in ("understanding ", "decision: choosing an approach for ", "bug fix involving ", "recurring pattern: ", "decision: ", "bug fix: "):
        t = t.removeprefix(prefix)
    return re.sub(r"[^a-z0-9 ]", "", t).strip()


def extract_units_from_text(db: DBSession, session: Session, transcript: str) -> list[KnowledgeUnit]:
    """Runs LLM extraction over a transcript and persists units + review state + relations."""
    llm = get_llm()
    raw = llm.complete(
        [
            {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": transcript[:60_000]},
        ],
        json_mode=True,
    )
    try:
        data = json.loads(raw)
        parsed = data.get("units", [])
    except (json.JSONDecodeError, AttributeError):
        logger.warning("Extraction returned non-JSON output for session %s", session.id)
        parsed = []

    existing_titles = set(
        db.scalars(
            select(KnowledgeUnit.title).where(
                KnowledgeUnit.session_id == session.id, KnowledgeUnit.deleted_at.is_(None)
            )
        ).all()
    )

    created: list[KnowledgeUnit] = []
    now = utcnow()
    first_review = now + timedelta(hours=settings.DIFFUSE_MODE_DELAY_HOURS)
    for item in parsed:
        if not isinstance(item, dict):
            continue
        unit_type = item.get("unit_type")
        title = (item.get("title") or "").strip()[:300]
        if unit_type not in VALID_UNIT_TYPES or not title or title in existing_titles:
            continue
        existing_titles.add(title)
        difficulty = item.get("difficulty")
        unit = KnowledgeUnit(
            user_id=session.user_id,
            project_id=session.project_id,
            session_id=session.id,
            source_fidelity=session.source_fidelity,
            unit_type=unit_type,
            title=title,
            summary=(item.get("summary") or "")[:2000] or None,
            difficulty=difficulty if difficulty in VALID_DIFFICULTIES else "intermediate",
        )
        db.add(unit)
        db.flush()
        # Diffuse-mode principle: the first review is never available immediately.
        db.add(
            ReviewState(
                user_id=session.user_id,
                unit_id=unit.id,
                next_review_at=first_review,
                first_review_at=first_review,
                interval_days=1,
                ease_factor=2.5,
                mastery_status="new",
            )
        )
        created.append(unit)

    _link_recurrences(db, created)
    return created


def _link_recurrences(db: DBSession, new_units: list[KnowledgeUnit]) -> None:
    """Cross-session recurrence detection via normalized-title matching (v1)."""
    for unit in new_units:
        core = normalize_title(unit.title)
        if not core:
            continue
        candidates = db.scalars(
            select(KnowledgeUnit).where(
                KnowledgeUnit.user_id == unit.user_id,
                KnowledgeUnit.id != unit.id,
                KnowledgeUnit.deleted_at.is_(None),
            )
        ).all()
        for other in candidates:
            if other.session_id == unit.session_id:
                continue
            if normalize_title(other.title) == core:
                db.add(
                    KnowledgeUnitRelation(unit_id=unit.id, related_unit_id=other.id, relation_type="recurs_as")
                )
                break


def run_extraction(session_id: str) -> None:
    """Background entrypoint: owns its DB session, updates extraction_status."""
    db = SessionLocal()
    try:
        session = db.get(Session, session_id)
        if session is None:
            return
        session.extraction_status = "running"
        db.commit()

        messages = db.scalars(
            select(Message).where(Message.session_id == session_id).order_by(Message.timestamp)
        ).all()
        if len(messages) < settings.EXTRACTION_MIN_MESSAGES:
            session.extraction_status = "insufficient_content"
            db.commit()
            return

        transcript = build_transcript(messages)
        created = None
        for attempt, delay in enumerate((0.0, *EXTRACTION_RETRY_DELAYS_SECONDS)):
            if delay:
                logger.warning(
                    "Extraction for session %s waiting %.0fs before retry %d (provider rate-limited)",
                    session_id, delay, attempt,
                )
                time.sleep(delay)
            try:
                created = extract_units_from_text(db, session, transcript)
                break
            except LLMError as exc:
                db.rollback()
                logger.warning("Extraction attempt %d failed for session %s: %s", attempt + 1, session_id, exc)
        if created is None:
            # Provider stayed unavailable — leave it retryable via POST /sessions/{id}/extract.
            session = db.get(Session, session_id)
            session.extraction_status = "failed"
            db.commit()
            return
        session.extraction_status = "completed" if created else "insufficient_content"
        db.commit()
    except Exception:
        logger.exception("Extraction failed for session %s", session_id)
        db.rollback()
        try:
            session = db.get(Session, session_id)
            if session is not None:
                session.extraction_status = "failed"
                db.commit()
        except Exception:
            logger.exception("Could not mark session %s extraction as failed", session_id)
    finally:
        db.close()
