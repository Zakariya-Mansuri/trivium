"""E2E helper: simulate time passing for a user so their reviews become due.

Usage: python make_due.py <email>   (run with the backend venv against trivium.db)
"""
import sys
from datetime import timedelta

sys.path.insert(0, "../backend")

from sqlalchemy import select, update  # noqa: E402

from app.db.base import utcnow  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.models import KnowledgeUnit, ReviewState, User  # noqa: E402

email = sys.argv[1]
db = SessionLocal()
user = db.scalar(select(User).where(User.email == email))
assert user is not None, f"no user {email}"
past = utcnow() - timedelta(hours=3)
unit_ids = db.scalars(select(KnowledgeUnit.id).where(KnowledgeUnit.user_id == user.id)).all()
db.execute(
    update(ReviewState)
    .where(ReviewState.user_id == user.id)
    .values(next_review_at=past, first_review_at=past)
)
db.commit()
print(f"made {len(unit_ids)} units due for {email}")
db.close()
