from sqlalchemy import ForeignKey, Index, Integer, Numeric, String, Text, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, GUID, UTCDateTime, new_uuid, utcnow


class LearningArtifact(Base):
    __tablename__ = "learning_artifacts"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(GUID, ForeignKey("users.id"), nullable=False)
    scope_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'message' | 'chat' | 'project' | 'time_range'
    scope_ref: Mapped[dict] = mapped_column(JSON, nullable=False)
    format: Mapped[str] = mapped_column(String(30), nullable=False)
    content: Mapped[dict] = mapped_column(JSON, nullable=False)
    generated_at: Mapped[object] = mapped_column(UTCDateTime, nullable=False, default=utcnow)
    triggered_by: Mapped[str] = mapped_column(String(30), nullable=False)  # 'user_action' | 'scheduled_review'
    completed_at: Mapped[object | None] = mapped_column(UTCDateTime, nullable=True)

    __table_args__ = (Index("idx_artifacts_user", "user_id", "generated_at"),)


class LearningArtifactUnit(Base):
    __tablename__ = "learning_artifact_units"

    artifact_id: Mapped[str] = mapped_column(
        GUID, ForeignKey("learning_artifacts.id"), primary_key=True
    )
    unit_id: Mapped[str] = mapped_column(GUID, ForeignKey("knowledge_units.id"), primary_key=True)


class ReviewState(Base):
    __tablename__ = "review_state"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(GUID, ForeignKey("users.id"), nullable=False)
    unit_id: Mapped[str] = mapped_column(GUID, ForeignKey("knowledge_units.id"), nullable=False)
    next_review_at: Mapped[object] = mapped_column(UTCDateTime, nullable=False)
    interval_days: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False, default=1)
    ease_factor: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False, default=2.5)  # SM-2 style
    consecutive_correct: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    first_review_at: Mapped[object | None] = mapped_column(UTCDateTime, nullable=True)  # diffuse-mode delay gate
    mastery_status: Mapped[str] = mapped_column(String(20), nullable=False, default="new")
    # 'new' | 'learning' | 'consolidated' | 'stale'
    updated_at: Mapped[object] = mapped_column(UTCDateTime, nullable=False, default=utcnow, onupdate=utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "unit_id", name="uq_review_state_user_unit"),
        Index("idx_review_state_due", "user_id", "next_review_at"),
    )


class ReviewHistory(Base):
    __tablename__ = "review_history"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(GUID, ForeignKey("users.id"), nullable=False)
    unit_id: Mapped[str] = mapped_column(GUID, ForeignKey("knowledge_units.id"), nullable=False)
    artifact_id: Mapped[str | None] = mapped_column(GUID, ForeignKey("learning_artifacts.id"), nullable=True)
    performance: Mapped[str] = mapped_column(String(20), nullable=False)  # 'correct' | 'partial' | 'incorrect'
    # AI-suggested grade for the same attempt (user may override) — calibration signal.
    ai_performance: Mapped[str | None] = mapped_column(String(20), nullable=True)
    response_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    day_offset: Mapped[int] = mapped_column(Integer, nullable=False)
    reviewed_at: Mapped[object] = mapped_column(UTCDateTime, nullable=False, default=utcnow)

    __table_args__ = (Index("idx_review_history_unit_offset", "unit_id", "day_offset"),)
