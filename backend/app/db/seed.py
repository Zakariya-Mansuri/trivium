"""Seed script — realistic demo data for local testing and demos.

Usage:  python -m app.db.seed
Creates demo user demo@trivium.dev / Demo1234! with projects, sessions,
extracted knowledge units, due reviews, and review history so every screen
(queue, profile, metrics) has meaningful data immediately.
"""
import random
from datetime import timedelta

from sqlalchemy import select

from app.core.security import hash_password
from app.db.base import Base, utcnow
from app.db.session import SessionLocal, engine
from app.models import (
    KnowledgeUnit,
    Message,
    Project,
    ReviewHistory,
    ReviewState,
    Session,
    User,
)
from app.services.extraction import run_extraction

DEMO_EMAIL = "demo@trivium.dev"
DEMO_PASSWORD = "Demo1234!"

AUTH_SESSION = [
    ("user", "user", "I need to add JWT authentication to my FastAPI app. Should I use sessions instead?"),
    ("assistant", "ai", "For an SPA + API split, JWT is the right call. We decided on JWT instead of server-side sessions because your React frontend on Vercel and FastAPI backend on Render are separate origins — cookie sessions get painful across domains. Tradeoff: JWTs can't be revoked server-side unless you add a refresh-token table.\n```python\nimport jwt\ntoken = jwt.encode({'sub': user_id, 'exp': expiry}, SECRET, algorithm='HS256')\n```"),
    ("user", "user", "Got an error: jwt.exceptions.InvalidSignatureError when verifying."),
    ("assistant", "ai", "That bug means the SECRET used to verify differs from the one used to sign. The fix: load SECRET_KEY from one config source, not os.environ in one place and a hardcoded default in another. This is a classic config-drift bug in FastAPI apps."),
    ("user", "user", "Fixed! Also added bcrypt hashing for passwords like we did in the last project."),
    ("assistant", "ai", "Good — that's the same pattern as before: hash with bcrypt at signup, verify at login, never store plaintext. Recurring pattern across your projects: authentication hardening (bcrypt + JWT + rate limiting)."),
]

REVIEW_APP_SESSION = [
    ("user", "user", "Designing the architecture for my spaced repetition service. Components: scheduler, review queue API, and a React frontend layer."),
    ("assistant", "ai", "Your architecture has three components: the scheduler service computes next_review_at with SM-2, the queue API layer serves due items, and the frontend module renders recall prompts. Data flows scheduler -> queue -> UI. Keep the scheduler pure (no I/O) so it's testable."),
    ("user", "user", "Should I use PostgreSQL or MongoDB for the review state?"),
    ("assistant", "ai", "PostgreSQL, instead of MongoDB — review state is relational by nature (users x units x history), and you'll want indexed queries on (user_id, next_review_at). The tradeoff is less schema flexibility, but your schema is stable. Decision: Postgres with a composite index."),
    ("user", "user", "The queue query is slow, seems like an N+1 problem when loading units."),
    ("assistant", "ai", "Classic N+1 bug — you fetch review states then query each unit separately. The fix is a single JOIN with selectinload. After the fix the queue endpoint drops from 40 queries to 2."),
]

REACT_SESSION = [
    ("user", "user", "My React state management is getting messy with prop drilling through five components."),
    ("assistant", "ai", "For your case a lightweight approach beats Redux: lift shared state into a context provider and use a reducer hook. The tradeoff versus Redux is fewer devtools, but far less boilerplate for an app this size."),
    ("user", "user", "TypeError: Cannot read properties of undefined (reading 'map') on first render."),
    ("assistant", "ai", "That error is the async-data-on-first-render bug: state starts undefined and .map runs before the fetch resolves. Fix: initialize state to an empty array, or guard with optional chaining. This is the same pattern as the loading-state issue you hit last week."),
]


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.scalar(select(User).where(User.email == DEMO_EMAIL)) is not None:
            print(f"Seed user {DEMO_EMAIL} already exists — skipping. Delete trivium.db to reseed.")
            return

        user = User(
            email=DEMO_EMAIL,
            display_name="Demo Developer",
            hashed_password=hash_password(DEMO_PASSWORD),
        )
        db.add(user)
        db.flush()

        auth_project = Project(user_id=user.id, name="SaaS Auth Service")
        learn_project = Project(user_id=user.id, name="Spaced Repetition App")
        db.add_all([auth_project, learn_project])
        db.flush()

        now = utcnow()
        specs = [
            (auth_project, "native", "native", "JWT auth implementation", AUTH_SESSION, 21),
            (learn_project, "claude_code", "wrapped", "Review service architecture", REVIEW_APP_SESSION, 14),
            (learn_project, "cursor", "wrapped", "React state cleanup", REACT_SESSION, 7),
        ]
        sessions = []
        for project, tool, fidelity, title, transcript, days_ago in specs:
            started = now - timedelta(days=days_ago)
            session = Session(
                user_id=user.id,
                project_id=project.id,
                source_tool=tool,
                source_fidelity=fidelity,
                title=title,
                started_at=started,
                ended_at=started + timedelta(minutes=len(transcript) * 4),
            )
            db.add(session)
            db.flush()
            for i, (role, authored_by, content) in enumerate(transcript):
                db.add(
                    Message(
                        session_id=session.id,
                        role=role,
                        content=content,
                        authored_by=authored_by,
                        code_diff="--- a/auth.py\n+++ b/auth.py" if "```" in content else None,
                        timestamp=started + timedelta(minutes=i * 4),
                    )
                )
            sessions.append((session, days_ago))
        db.commit()

        for session, _ in sessions:
            run_extraction(session.id)

        # Backdate learning so the demo has due reviews + retention history.
        units = db.scalars(select(KnowledgeUnit).where(KnowledgeUnit.user_id == user.id)).all()
        rng = random.Random(42)
        for i, unit in enumerate(units):
            state = db.scalar(select(ReviewState).where(ReviewState.unit_id == unit.id))
            if state is None:
                continue
            session_age_days = next((d for s, d in sessions if s.id == unit.session_id), 7)
            unit.extracted_at = now - timedelta(days=session_age_days)
            state.first_review_at = unit.extracted_at + timedelta(hours=12)
            # Simulate past reviews for two-thirds of units.
            if i % 3 != 2:
                reviews = min(session_age_days // 3, 4)
                interval, ease, consecutive = 1.0, 2.5, 0
                for r in range(reviews):
                    reviewed_at = unit.extracted_at + timedelta(days=1 + r * 3)
                    perf = rng.choices(["correct", "partial", "incorrect"], weights=[6, 2, 1])[0]
                    db.add(
                        ReviewHistory(
                            user_id=user.id,
                            unit_id=unit.id,
                            performance=perf,
                            response_text="(seeded recall attempt)",
                            day_offset=max(0, (reviewed_at - unit.extracted_at).days),
                            reviewed_at=reviewed_at,
                        )
                    )
                    if perf == "correct":
                        consecutive += 1
                        interval = 1.0 if consecutive == 1 else 6.0 if consecutive == 2 else interval * ease
                        ease = min(3.0, ease + 0.05)
                    elif perf == "partial":
                        interval = max(1.0, interval * 0.5)
                        ease = max(1.3, ease - 0.15)
                    else:
                        consecutive, interval, ease = 0, 1.0, max(1.3, ease - 0.3)
                state.consecutive_correct = consecutive
                state.interval_days = round(interval, 2)
                state.ease_factor = round(ease, 2)
                state.mastery_status = "consolidated" if consecutive >= 3 and interval >= 21 else "learning"
                state.next_review_at = now - timedelta(hours=rng.randint(1, 48))  # due now
            else:
                state.next_review_at = now - timedelta(hours=1)
                state.first_review_at = now - timedelta(hours=2)
        db.commit()
        print(f"Seeded {DEMO_EMAIL} / {DEMO_PASSWORD}: 2 projects, 3 sessions, {len(units)} knowledge units.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
