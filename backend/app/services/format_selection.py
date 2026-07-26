"""Format Selection Engine (rule-based v1).

Maps detected content type -> artifact format per PRD 6.2, logging every
decision (with the triggering signal) to format_decisions for auditability.

Rules (rule_version comes from settings.FORMAT_RULE_VERSION):
  concept                          -> flashcard   (first exposure / definition)
  decision with tradeoff language  -> self_explanation (distinct "why" format)
  decision otherwise               -> qa          (reasoning prompt)
  bug_fix                          -> retrieval_practice
  pattern / recurring unit         -> synthesis   (chunking question)
  >=3 units w/ architecture signal -> diagram     (scope-level, additive)
"""
from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.core.config import settings
from app.models import FormatDecision, KnowledgeUnit, KnowledgeUnitRelation

TRADEOFF_SIGNALS = ["instead of", "tradeoff", "trade-off", " vs ", "versus", "alternative", "chose", "opted"]
ARCH_SIGNALS = ["architecture", "component", "service", "layer", "pipeline", "flow", "module", "system"]


def _has_recurrence(db: DBSession, unit_id: str) -> bool:
    return (
        db.scalar(select(KnowledgeUnitRelation.id).where(KnowledgeUnitRelation.unit_id == unit_id).limit(1))
        is not None
    )


def choose_format(db: DBSession, unit: KnowledgeUnit) -> str:
    text = f"{unit.title} {unit.summary or ''}".lower()

    if unit.unit_type == "pattern" or _has_recurrence(db, unit.id):
        fmt, signal = "synthesis", "unit_type=pattern or recurs_as relation present"
    elif unit.unit_type == "bug_fix":
        fmt, signal = "retrieval_practice", "unit_type=bug_fix"
    elif unit.unit_type == "decision":
        matched = next((s for s in TRADEOFF_SIGNALS if s in text), None)
        if matched:
            fmt, signal = "self_explanation", f"decision with tradeoff signal: '{matched}'"
        else:
            fmt, signal = "qa", "unit_type=decision"
    else:
        fmt, signal = "flashcard", "unit_type=concept, first exposure"

    db.add(
        FormatDecision(
            unit_id=unit.id,
            detected_type=unit.unit_type,
            chosen_format=fmt,
            rule_version=settings.FORMAT_RULE_VERSION,
            signal=signal,
        )
    )
    return fmt


def log_supplement(db: DBSession, units: list[KnowledgeUnit], fmt: str, signal: str) -> None:
    """Audit-logs an additive scope-level format decision (diagram/mcq supplements)."""
    for u in units:
        db.add(
            FormatDecision(
                unit_id=u.id,
                detected_type=u.unit_type,
                chosen_format=fmt,
                rule_version=settings.FORMAT_RULE_VERSION,
                signal=signal,
            )
        )


def scope_needs_diagram(db: DBSession, units: list[KnowledgeUnit]) -> bool:
    """Scope-level rule: multi-component architecture -> diagram artifact (additive)."""
    if len(units) < 3:
        return False
    combined = " ".join(f"{u.title} {u.summary or ''}" for u in units).lower()
    matched = next((s for s in ARCH_SIGNALS if s in combined), None)
    if not matched:
        return False
    for u in units:
        db.add(
            FormatDecision(
                unit_id=u.id,
                detected_type="architecture",
                chosen_format="diagram",
                rule_version=settings.FORMAT_RULE_VERSION,
                signal=f"scope has {len(units)} units with architecture signal: '{matched}'",
            )
        )
    return True
