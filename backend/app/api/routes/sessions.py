from datetime import timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession, selectinload

from app.api.deps import get_current_user
from app.db.base import utcnow
from app.db.session import get_db
from app.models import Message, Project, Session, User
from app.schemas.core import (
    MessageIn,
    MessageOut,
    SessionCreate,
    SessionDetailOut,
    SessionImport,
    SessionOut,
)
from app.services.extraction import run_extraction

router = APIRouter(prefix="/sessions", tags=["sessions"])


def _check_project(db: DBSession, user: User, project_id: str | None) -> None:
    if project_id is None:
        return
    project = db.get(Project, project_id)
    if project is None or project.user_id != user.id or project.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Project not found")


def _get_owned_session(db: DBSession, user: User, session_id: str, *, with_messages: bool = False) -> Session:
    stmt = select(Session).where(Session.id == session_id)
    if with_messages:
        stmt = stmt.options(selectinload(Session.messages))
    session = db.scalar(stmt)
    if session is None or session.user_id != user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.post("", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
def create_session(body: SessionCreate, db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    """Start a native-agent session."""
    _check_project(db, user, body.project_id)
    session = Session(
        user_id=user.id,
        project_id=body.project_id,
        source_tool="native",
        source_fidelity="native",
        title=body.title,
        started_at=utcnow(),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.post("/import", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
def import_session(
    body: SessionImport,
    background_tasks: BackgroundTasks,
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Paste/import an external tool's session — tagged 'wrapped' fidelity, honestly."""
    _check_project(db, user, body.project_id)
    now = utcnow()
    session = Session(
        user_id=user.id,
        project_id=body.project_id,
        source_tool=body.source_tool,
        source_fidelity="wrapped",
        title=body.title or f"Imported {body.source_tool} session",
        started_at=now - timedelta(minutes=len(body.messages)),
        ended_at=now,
        raw_log_ref=body.raw_text[:500_000] if body.raw_text else None,
    )
    db.add(session)
    db.flush()
    base_time = session.started_at
    for i, m in enumerate(body.messages):
        # Imported transcripts: assistant output is AI-authored, user input user-authored.
        authored_by = m.authored_by or ("ai" if m.role == "assistant" else "user")
        db.add(
            Message(
                session_id=session.id,
                role=m.role,
                content=m.content,
                authored_by=authored_by,
                code_diff=m.code_diff,
                timestamp=m.timestamp or (base_time + timedelta(minutes=i)),
            )
        )
    db.commit()
    db.refresh(session)
    background_tasks.add_task(run_extraction, session.id)
    return session


@router.get("", response_model=list[SessionOut])
def list_sessions(
    project_id: str | None = None,
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    stmt = select(Session).where(Session.user_id == user.id).order_by(Session.started_at.desc())
    if project_id is not None:
        stmt = stmt.where(Session.project_id == project_id)
    return db.scalars(stmt).all()


@router.get("/{session_id}", response_model=SessionDetailOut)
def get_session(session_id: str, db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    return _get_owned_session(db, user, session_id, with_messages=True)


@router.post("/{session_id}/messages", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
def add_message(
    session_id: str,
    body: MessageIn,
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Append a message to a session (manual capture path)."""
    session = _get_owned_session(db, user, session_id)
    message = Message(
        session_id=session.id,
        role=body.role,
        content=body.content,
        authored_by=body.authored_by or ("ai" if body.role == "assistant" else "user"),
        code_diff=body.code_diff,
        timestamp=body.timestamp or utcnow(),
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


@router.post("/{session_id}/end", response_model=SessionOut)
def end_session(
    session_id: str,
    background_tasks: BackgroundTasks,
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """End a session and kick off background extraction."""
    session = _get_owned_session(db, user, session_id)
    if session.ended_at is None:
        session.ended_at = utcnow()
        db.commit()
        db.refresh(session)
    if session.extraction_status == "pending":
        background_tasks.add_task(run_extraction, session.id)
    return session


@router.post("/{session_id}/extract", response_model=SessionOut)
def trigger_extraction(
    session_id: str,
    background_tasks: BackgroundTasks,
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Manually (re)run extraction for a session."""
    session = _get_owned_session(db, user, session_id)
    if session.extraction_status == "running":
        raise HTTPException(status_code=409, detail="Extraction already running for this session")
    background_tasks.add_task(run_extraction, session.id)
    session.extraction_status = "pending"
    db.commit()
    db.refresh(session)
    return session
