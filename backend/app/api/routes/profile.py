from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session as DBSession

from app.api.deps import get_current_user
from app.db.base import utcnow
from app.db.session import get_db
from app.models import KnowledgeProfileEntry, User
from app.schemas.learning import KnowledgeUnitOut, ProfileEntryOut, ProfileOut, VisibilityUpdate
from app.services import profile as profile_service

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileOut)
def get_profile(db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    entries = profile_service.compute_profile(db, user)
    counts: dict[str, int] = {}
    for entry, _ in entries:
        counts[entry.mastery_status] = counts.get(entry.mastery_status, 0) + 1
    return ProfileOut(
        entries=[
            ProfileEntryOut(
                unit=KnowledgeUnitOut.model_validate(unit),
                mastery_status=entry.mastery_status,
                retention_trend=entry.retention_trend,
                visibility=entry.visibility,
                entry_id=entry.id,
            )
            for entry, unit in entries
        ],
        counts=counts,
        generated_at=utcnow(),
    )


@router.get("/export", response_class=PlainTextResponse)
def export_profile(
    audience: str = "private",
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Markdown (skill.md) export. audience=shared applies visibility filtering
    at generation time — private entries never enter the output."""
    if audience not in ("private", "shared"):
        raise HTTPException(status_code=422, detail="audience must be 'private' or 'shared'")
    markdown = profile_service.export_markdown(db, user, audience)
    return PlainTextResponse(
        markdown,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="skill.md"'},
    )


@router.patch("/entries/{entry_id}/visibility", response_model=ProfileEntryOut)
def set_visibility(
    entry_id: str,
    body: VisibilityUpdate,
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    entry = db.get(KnowledgeProfileEntry, entry_id)
    if entry is None or entry.user_id != user.id:
        raise HTTPException(status_code=404, detail="Profile entry not found")
    entry.visibility = body.visibility
    db.commit()
    db.refresh(entry)
    from app.models import KnowledgeUnit

    unit = db.get(KnowledgeUnit, entry.unit_id)
    return ProfileEntryOut(
        unit=KnowledgeUnitOut.model_validate(unit),
        mastery_status=entry.mastery_status,
        retention_trend=entry.retention_trend,
        visibility=entry.visibility,
        entry_id=entry.id,
    )
