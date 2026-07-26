from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session as DBSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.models import SkillReport, User
from app.services import skills as skills_service

router = APIRouter(prefix="/skills", tags=["skills"])


def _serialize(report: SkillReport | dict) -> dict:
    if isinstance(report, dict):  # insufficient-data case
        return report
    return {
        "report_type": report.report_type,
        "content": report.content,
        "message_count": report.message_count,
        "computed_at": report.computed_at.isoformat(),
    }


@router.get("/language")
@limiter.limit(settings.RATE_LIMIT_LLM)
def language_report(
    request: Request,
    refresh: bool = False,
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """How clearly and correctly the user writes — separate from prompting."""
    return _serialize(skills_service.compute_report(db, user, "language", refresh=refresh))


@router.get("/prompting")
@limiter.limit(settings.RATE_LIMIT_LLM)
def prompting_report(
    request: Request,
    refresh: bool = False,
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """How effectively the user instructs AI assistants — separate from language."""
    return _serialize(skills_service.compute_report(db, user, "prompting", refresh=refresh))


@router.get("/recommendations")
def recommendations(db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    """Credible courses/materials matched to the user's weakest knowledge areas."""
    return {"gaps": skills_service.gap_recommendations(db, user)}
