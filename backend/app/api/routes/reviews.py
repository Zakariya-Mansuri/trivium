from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session as DBSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.models import User
from app.schemas.learning import (
    ArtifactOut,
    GradeRequest,
    GradeVerdict,
    KnowledgeUnitOut,
    ReviewQueueItem,
    ReviewQueueOut,
    ReviewResultOut,
    ReviewSubmission,
)
from app.services import review as review_service

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/grade", response_model=GradeVerdict)
@limiter.limit(settings.RATE_LIMIT_LLM)
def grade(
    request: Request,
    body: GradeRequest,
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """AI-suggested grade for a typed recall attempt (evidence over self-report).
    Advisory only — the user confirms or overrides via /submit; nothing is written here."""
    verdict = review_service.grade_recall(db, user, body.unit_id, body.artifact_id, body.response_text)
    return GradeVerdict(**verdict)


@router.get("/queue", response_model=ReviewQueueOut)
def get_queue(
    early: bool = False,
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Due reviews, interleaved across projects, diffuse-mode delay respected.
    With ?early=true (an explicit user choice) not-yet-due items fill spare slots."""
    data = review_service.build_queue(db, user, include_early=early)
    return ReviewQueueOut(
        items=[
            ReviewQueueItem(
                unit=KnowledgeUnitOut.model_validate(item["unit"]),
                artifact=ArtifactOut.model_validate(item["artifact"]),
                review_state_id=item["state"].id,
                mastery_status=item["state"].mastery_status,
                next_review_at=item["state"].next_review_at,
                early=item["early"],
            )
            for item in data["items"]
        ],
        total_due=data["total_due"],
        total_early=data["total_early"],
        projects_in_session=data["projects_in_session"],
        next_due_at=data["next_due_at"],
    )


@router.post("/submit", response_model=ReviewResultOut)
def submit(body: ReviewSubmission, db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    """Records a recall attempt — the ONLY write path into review/mastery state."""
    state = review_service.submit_review(db, user, body)
    return ReviewResultOut(
        unit_id=state.unit_id,
        mastery_status=state.mastery_status,
        next_review_at=state.next_review_at,
        interval_days=float(state.interval_days),
        ease_factor=float(state.ease_factor),
    )
