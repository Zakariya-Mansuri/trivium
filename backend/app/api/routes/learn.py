from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.models import KnowledgeUnit, LearningArtifact, User
from app.schemas.learning import ArtifactOut, KnowledgeUnitOut, LearnRequest, LearnResponse
from app.services import artifacts as artifact_service

router = APIRouter(tags=["learn"])


@router.post("/learn", response_model=LearnResponse)
@limiter.limit(settings.RATE_LIMIT_LLM)
def learn(
    request: Request,
    body: LearnRequest,
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """The core Learn primitive — any granularity, always user-initiated."""
    generated, units_covered, message = artifact_service.learn(db, user, body)
    return LearnResponse(
        artifacts=[ArtifactOut.model_validate(a) for a in generated],
        units_covered=units_covered,
        message=message,
    )


@router.get("/artifacts", response_model=list[ArtifactOut])
def list_artifacts(
    limit: int = 50,
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return db.scalars(
        select(LearningArtifact)
        .where(LearningArtifact.user_id == user.id)
        .order_by(LearningArtifact.generated_at.desc())
        .limit(min(limit, 200))
    ).all()


@router.get("/artifacts/{artifact_id}", response_model=ArtifactOut)
def get_artifact(artifact_id: str, db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    artifact = db.get(LearningArtifact, artifact_id)
    if artifact is None or artifact.user_id != user.id:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return artifact


@router.post("/artifacts/{artifact_id}/complete", response_model=ArtifactOut)
def complete_artifact(artifact_id: str, db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    """Marks engagement with an artifact (Layer 1). Does NOT touch review/mastery state —
    only recall submissions via /reviews do that."""
    return artifact_service.mark_artifact_completed(db, user, artifact_id)


@router.get("/knowledge-units", response_model=list[KnowledgeUnitOut])
def list_knowledge_units(
    project_id: str | None = None,
    session_id: str | None = None,
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    stmt = (
        select(KnowledgeUnit)
        .where(KnowledgeUnit.user_id == user.id, KnowledgeUnit.deleted_at.is_(None))
        .order_by(KnowledgeUnit.extracted_at.desc())
    )
    if project_id:
        stmt = stmt.where(KnowledgeUnit.project_id == project_id)
    if session_id:
        stmt = stmt.where(KnowledgeUnit.session_id == session_id)
    return db.scalars(stmt.limit(500)).all()
