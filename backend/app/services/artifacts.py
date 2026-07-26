"""Learning Artifact Generator + the "Learn" action scope resolver.

Learn is user-initiated at any granularity (message / chat / project / time_range),
never auto-triggered. Insufficient content is communicated clearly instead of
generating a low-quality artifact (PRD 6.1).
"""
import json
import logging
import re

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.db.base import utcnow
from app.llm import get_llm
from app.models import (
    KnowledgeUnit,
    LearningArtifact,
    LearningArtifactUnit,
    Message,
    Session,
    User,
)
from app.schemas.learning import LearnRequest
from app.services import format_selection
from app.services.extraction import build_transcript, extract_units_from_text
from app.services.metrics import log_event

logger = logging.getLogger(__name__)

ARTIFACT_SYSTEM_PROMPT = """[TASK:artifact]
You generate a learning artifact from knowledge units extracted from the user's own coding work.
Hard rules (learning science):
- qa/retrieval/self-explanation formats use active recall (open response).
- Self-explanation prompts must ask WHY an approach worked and where it would fail.
- Diagrams are Mermaid flowcharts derived from the user's actual work.
- MCQ distractors must be plausible misconceptions, not jokes; exactly one correct choice.
Mermaid syntax rules (CRITICAL — invalid syntax breaks rendering):
- Start with: flowchart TD
- ALWAYS double-quote node labels: A["Label text"] — never bare labels.
- Never use parentheses, brackets, braces or quotes INSIDE a label; rephrase instead
  (e.g. use 'ngrok / Cloudflare' not '(ngrok, Cloudflare)').
- Only simple edges: A --> B or A -->|"label"| B. No subgraphs, no classes, no styling.
The user message is JSON: {"format": "...", "units": [{"title","summary","unit_type"}]}.
Respond with a single JSON object for the requested format:
flashcard: {"type":"flashcard","cards":[{"front","back"}]}
qa: {"type":"qa","questions":[{"question","expected_points":[],"kind":"recall"}]}
self_explanation: {"type":"self_explanation","prompts":[{"prompt","context"}]}
retrieval_practice: {"type":"retrieval_practice","questions":[{"question","answer"}]}
synthesis: {"type":"synthesis","prompt":"...","related_titles":[]}
diagram: {"type":"diagram","mermaid":"...","explanation":"...","recall_prompt":"..."}
mcq: {"type":"mcq","questions":[{"question","choices":["...","...","...","..."],"correct_index":0,"explanation":"..."}]}"""

# Node labels containing special characters must be quoted or mermaid fails to parse
# (e.g. `H2[Tunneling service (ngrok, Cloudflare)]` is invalid).
_MERMAID_NODE_RE = re.compile(r'(\b[A-Za-z0-9_]+)\[(?!")([^\]]*)\]')


def sanitize_mermaid(spec: str) -> str:
    """Best-effort repair of common LLM mermaid mistakes so diagrams render."""
    spec = spec.strip()
    # Strip markdown fences the model sometimes wraps the spec in.
    fence = re.match(r"^```(?:mermaid)?\s*\n(.*?)\n?```$", spec, re.DOTALL)
    if fence:
        spec = fence.group(1).strip()
    if not spec.startswith(("flowchart", "graph")):
        spec = "flowchart TD\n" + spec

    def quote_label(m: re.Match) -> str:
        label = m.group(2).replace('"', "'").strip()
        return f'{m.group(1)}["{label}"]'

    return _MERMAID_NODE_RE.sub(quote_label, spec)


def generate_artifact_content(fmt: str, units: list[KnowledgeUnit], user: User | None = None) -> dict:
    payload = json.dumps(
        {
            "format": fmt,
            "units": [{"title": u.title, "summary": u.summary or "", "unit_type": u.unit_type} for u in units],
        }
    )
    raw = get_llm(user).complete(
        [{"role": "system", "content": ARTIFACT_SYSTEM_PROMPT}, {"role": "user", "content": payload}],
        json_mode=True,
    )
    try:
        content = json.loads(raw)
        if not isinstance(content, dict) or "type" not in content:
            raise ValueError("missing type")
        if content.get("type") == "diagram" and isinstance(content.get("mermaid"), str):
            content["mermaid"] = sanitize_mermaid(content["mermaid"])
        return content
    except (json.JSONDecodeError, ValueError):
        logger.warning("Artifact generation returned invalid JSON for format %s; using recall fallback", fmt)
        return {
            "type": "qa",
            "questions": [
                {
                    "question": f"From memory, explain: {u.title}",
                    "expected_points": [],
                    "kind": "recall",
                }
                for u in units
            ],
        }


def create_artifact(
    db: DBSession,
    user: User,
    scope_type: str,
    scope_ref: dict,
    fmt: str,
    units: list[KnowledgeUnit],
    triggered_by: str,
) -> LearningArtifact:
    artifact = LearningArtifact(
        user_id=user.id,
        scope_type=scope_type,
        scope_ref=scope_ref,
        format=fmt,
        content=generate_artifact_content(fmt, units, user),
        triggered_by=triggered_by,
    )
    db.add(artifact)
    db.flush()
    for u in units:
        db.add(LearningArtifactUnit(artifact_id=artifact.id, unit_id=u.id))
    return artifact


def _resolve_scope_units(db: DBSession, user: User, req: LearnRequest) -> tuple[list[KnowledgeUnit], dict]:
    """Resolves the Learn scope to knowledge units, running extraction on demand where needed."""
    base = select(KnowledgeUnit).where(
        KnowledgeUnit.user_id == user.id, KnowledgeUnit.deleted_at.is_(None)
    )

    if req.scope_type == "message":
        if not req.message_id:
            raise HTTPException(status_code=422, detail="message_id is required for message scope")
        msg = db.get(Message, req.message_id)
        session = db.get(Session, msg.session_id) if msg else None
        if msg is None or session is None or session.user_id != user.id:
            raise HTTPException(status_code=404, detail="Message not found")
        # Extract from just this message span, then use its units.
        created = extract_units_from_text(db, session, build_transcript([msg]))
        units = created or db.scalars(base.where(KnowledgeUnit.session_id == session.id)).all()
        return list(units), {"message_id": req.message_id, "session_id": session.id}

    if req.scope_type == "chat":
        if not req.session_id:
            raise HTTPException(status_code=422, detail="session_id is required for chat scope")
        session = db.get(Session, req.session_id)
        if session is None or session.user_id != user.id:
            raise HTTPException(status_code=404, detail="Session not found")
        units = db.scalars(base.where(KnowledgeUnit.session_id == session.id)).all()
        if not units and session.extraction_status in ("pending", "failed"):
            # Learn was asked for before background extraction ran — do it now, synchronously.
            messages = db.scalars(
                select(Message).where(Message.session_id == session.id).order_by(Message.timestamp)
            ).all()
            if messages:
                units = extract_units_from_text(db, session, build_transcript(messages))
                session.extraction_status = "completed" if units else "insufficient_content"
        return list(units), {"session_id": req.session_id}

    if req.scope_type == "project":
        if not req.project_id:
            raise HTTPException(status_code=422, detail="project_id is required for project scope")
        from app.models import Project

        project = db.get(Project, req.project_id)
        if project is None or project.user_id != user.id or project.deleted_at is not None:
            raise HTTPException(status_code=404, detail="Project not found")
        units = db.scalars(base.where(KnowledgeUnit.project_id == req.project_id)).all()
        return list(units), {"project_id": req.project_id}

    # time_range
    if not req.time_start or not req.time_end:
        raise HTTPException(status_code=422, detail="time_start and time_end are required for time_range scope")
    if req.time_start >= req.time_end:
        raise HTTPException(status_code=422, detail="time_start must be before time_end")
    units = db.scalars(
        base.where(KnowledgeUnit.extracted_at >= req.time_start, KnowledgeUnit.extracted_at <= req.time_end)
    ).all()
    return list(units), {
        "time_start": req.time_start.isoformat(),
        "time_end": req.time_end.isoformat(),
    }


def learn(db: DBSession, user: User, req: LearnRequest) -> tuple[list[LearningArtifact], int, str | None]:
    """The core "Learn" primitive. Returns (artifacts, units_covered, info_message)."""
    units, scope_ref = _resolve_scope_units(db, user, req)
    log_event(db, user.id, "learn_triggered", {"scope_type": req.scope_type, **scope_ref})

    if not units:
        db.commit()
        return [], 0, (
            "Not enough extractable content in this span to build a quality learning artifact. "
            "Try a larger scope, or add a session with more substantive coding discussion."
        )

    # Group units by their selected format; one artifact per format keeps sessions focused.
    by_format: dict[str, list[KnowledgeUnit]] = {}
    for unit in units:
        fmt = format_selection.choose_format(db, unit)
        by_format.setdefault(fmt, []).append(unit)

    artifacts = [
        create_artifact(db, user, req.scope_type, scope_ref, fmt, fmt_units, "user_action")
        for fmt, fmt_units in by_format.items()
    ]

    # Additive scope-level rule: multi-component architecture -> diagram.
    if format_selection.scope_needs_diagram(db, units):
        artifacts.append(
            create_artifact(db, user, req.scope_type, scope_ref, "diagram", units, "user_action")
        )

    # Additive recognition check: an MCQ quiz over the scope's units. Recall stays
    # the default (PRD testing-effect rule); this supplements it, never replaces it.
    mcq_units = units[:8]
    format_selection.log_supplement(db, mcq_units, "mcq", "scope-level recognition-check supplement")
    artifacts.append(
        create_artifact(db, user, req.scope_type, scope_ref, "mcq", mcq_units, "user_action")
    )

    db.commit()
    for a in artifacts:
        db.refresh(a)
    return artifacts, len(units), None


def mark_artifact_completed(db: DBSession, user: User, artifact_id: str) -> LearningArtifact:
    artifact = db.get(LearningArtifact, artifact_id)
    if artifact is None or artifact.user_id != user.id:
        raise HTTPException(status_code=404, detail="Artifact not found")
    if artifact.completed_at is None:
        artifact.completed_at = utcnow()
        log_event(db, user.id, "artifact_completed", {"artifact_id": artifact.id, "format": artifact.format})
        db.commit()
        db.refresh(artifact)
    return artifact

