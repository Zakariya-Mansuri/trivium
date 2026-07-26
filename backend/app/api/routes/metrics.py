from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session as DBSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import User
from app.services import metrics as metrics_service

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/engagement")
def engagement(db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    """Layer 1 — engagement proxies."""
    return metrics_service.engagement_summary(db, user.id)


@router.get("/retention")
def retention(db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    """Layer 2 — retention curve over review history (day_offset x performance)."""
    return metrics_service.retention_curve(db, user.id)


@router.get("/activity")
def activity(
    days: int = Query(default=90, ge=7, le=365),
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Daily review activity for the contribution-style graph."""
    return metrics_service.review_activity(db, user.id, days)


@router.get("/independence")
def independence(
    window_days: int = Query(default=30, ge=7, le=365),
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Layer 3 (early) — AI-assist ratio derived from messages.authored_by."""
    return metrics_service.ai_assist_ratio(db, user.id, window_days)
