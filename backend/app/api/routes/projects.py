from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.api.deps import get_current_user
from app.db.base import utcnow
from app.db.session import get_db
from app.models import Project, User
from app.schemas.core import ProjectCreate, ProjectOut, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])


def _get_owned_project(db: DBSession, user: User, project_id: str) -> Project:
    project = db.get(Project, project_id)
    # 404 (not 403) for other users' resources — don't leak existence.
    if project is None or project.user_id != user.id or project.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(body: ProjectCreate, db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    project = Project(user_id=user.id, name=body.name)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=list[ProjectOut])
def list_projects(db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    return db.scalars(
        select(Project)
        .where(Project.user_id == user.id, Project.deleted_at.is_(None))
        .order_by(Project.created_at.desc())
    ).all()


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: str, db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    return _get_owned_project(db, user, project_id)


@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: str, body: ProjectUpdate, db: DBSession = Depends(get_db), user: User = Depends(get_current_user)
):
    project = _get_owned_project(db, user, project_id)
    project.name = body.name
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: str, db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    project = _get_owned_project(db, user, project_id)
    project.deleted_at = utcnow()  # soft delete — longitudinal data is the moat
    db.commit()
