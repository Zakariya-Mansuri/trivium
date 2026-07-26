from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.rate_limit import limiter
from app.db.base import utcnow
from app.db.session import get_db
from app.llm import get_llm
from app.llm.base import LLMError
from app.models import Message, Project, Session, User
from app.schemas.core import AgentChatRequest, AgentChatResponse

router = APIRouter(prefix="/agent", tags=["agent"])

AGENT_SYSTEM_PROMPT = (
    "[TASK:agent_chat] You are Trivium's native coding agent. Help the user write, debug and "
    "understand code. Be concrete and correct; show minimal working examples. When you make a "
    "non-obvious choice, briefly say why — those decisions become the user's learning material."
)


@router.post("/chat", response_model=AgentChatResponse)
@limiter.limit(settings.RATE_LIMIT_LLM)
def chat(
    request: Request,
    body: AgentChatRequest,
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """One native-agent turn. Both sides are persisted with authored_by set at
    generation time — the Layer 3 independence metrics depend on this being
    correct from the very first message."""
    if body.session_id is not None:
        session = db.get(Session, body.session_id)
        if session is None or session.user_id != user.id:
            raise HTTPException(status_code=404, detail="Session not found")
        if session.ended_at is not None:
            raise HTTPException(status_code=409, detail="Session has ended — start a new one")
    else:
        if body.project_id is not None:
            project = db.get(Project, body.project_id)
            if project is None or project.user_id != user.id or project.deleted_at is not None:
                raise HTTPException(status_code=404, detail="Project not found")
        session = Session(
            user_id=user.id,
            project_id=body.project_id,
            source_tool="native",
            source_fidelity="native",
            title=body.message[:80],
            started_at=utcnow(),
        )
        db.add(session)
        db.flush()

    history = db.scalars(
        select(Message).where(Message.session_id == session.id).order_by(Message.timestamp)
    ).all()

    user_msg = Message(
        session_id=session.id,
        role="user",
        content=body.message,
        authored_by="user",
        code_diff=body.code_context,
        timestamp=utcnow(),
    )
    db.add(user_msg)

    llm_messages = [{"role": "system", "content": AGENT_SYSTEM_PROMPT}]
    for m in history[-20:]:
        llm_messages.append({"role": "user" if m.role == "user" else "assistant", "content": m.content})
    llm_messages.append({"role": "user", "content": body.message})

    try:
        reply = get_llm().complete(llm_messages)
    except LLMError:
        # Provider down after retries — discard the uncommitted turn; the global
        # LLMError handler turns this into a friendly 503 with Retry-After.
        db.rollback()
        raise

    assistant_msg = Message(
        session_id=session.id,
        role="assistant",
        content=reply,
        authored_by="ai",
        code_diff=None,
        timestamp=utcnow(),
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(user_msg)
    db.refresh(assistant_msg)
    return AgentChatResponse(session_id=session.id, user_message=user_msg, assistant_message=assistant_msg)
