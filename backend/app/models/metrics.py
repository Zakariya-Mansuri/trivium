from sqlalchemy import ForeignKey, Index, Numeric, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, GUID, UTCDateTime, new_uuid, utcnow


class KnowledgeProfileEntry(Base):
    __tablename__ = "knowledge_profile_entries"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(GUID, ForeignKey("users.id"), nullable=False)
    unit_id: Mapped[str] = mapped_column(GUID, ForeignKey("knowledge_units.id"), nullable=False)
    mastery_status: Mapped[str] = mapped_column(String(20), nullable=False)
    retention_trend: Mapped[str | None] = mapped_column(String(20), nullable=True)  # 'improving' | 'stable' | 'declining'
    visibility: Mapped[str] = mapped_column(String(10), nullable=False, default="private")  # 'private' | 'shared'
    last_computed_at: Mapped[object] = mapped_column(UTCDateTime, nullable=False, default=utcnow, onupdate=utcnow)

    __table_args__ = (Index("idx_profile_entries_user", "user_id"),)


class MetricsEvent(Base):
    __tablename__ = "metrics_events"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(GUID, ForeignKey("users.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(40), nullable=False)
    # 'learn_triggered' | 'artifact_completed' | 'queue_cleared' | ...
    event_metadata: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    occurred_at: Mapped[object] = mapped_column(UTCDateTime, nullable=False, default=utcnow)

    __table_args__ = (Index("idx_metrics_events_user", "user_id", "occurred_at"),)


class IndependenceMetric(Base):
    __tablename__ = "independence_metrics"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(GUID, ForeignKey("users.id"), nullable=False)
    unit_id: Mapped[str | None] = mapped_column(GUID, ForeignKey("knowledge_units.id"), nullable=True)
    metric_type: Mapped[str] = mapped_column(String(30), nullable=False)  # 'ai_assist_ratio' | 'error_repeat_rate'
    value: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    window_start: Mapped[object] = mapped_column(UTCDateTime, nullable=False)
    window_end: Mapped[object] = mapped_column(UTCDateTime, nullable=False)
    computed_at: Mapped[object] = mapped_column(UTCDateTime, nullable=False, default=utcnow)
