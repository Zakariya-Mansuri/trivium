from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.learning import (
    ArtifactOut,
    KnowledgeUnitOut,
    ReviewQueueItem,
    ReviewQueueOut,
    ReviewResultOut,
    ReviewSubmission,
)
from app.services import review as review_service

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/queue", response_model=ReviewQueueOut)
def get_queue(db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    """Due reviews, interleaved across projects, diffuse-mode delay respected."""
    data = review_service.build_queue(db, user)
    return ReviewQueueOut(
        items=[
            ReviewQueueItem(
                unit=KnowledgeUnitOut.model_validate(item["unit"]),
                artifact=ArtifactOut.model_validate(item["artifact"]),
                review_state_id=item["state"].id,
                mastery_status=item["state"].mastery_status,
                next_review_at=item["state"].next_review_at,
            )
            for item in data["items"]
        ],
        total_due=data["total_due"],
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
