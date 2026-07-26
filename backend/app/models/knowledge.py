from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, GUID, UTCDateTime, new_uuid, utcnow


class KnowledgeUnit(Base):
    __tablename__ = "knowledge_units"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(GUID, ForeignKey("users.id"), nullable=False)
    project_id: Mapped[str | None] = mapped_column(GUID, ForeignKey("projects.id"), nullable=True)
    session_id: Mapped[str | None] = mapped_column(GUID, ForeignKey("sessions.id"), nullable=True)
    source_fidelity: Mapped[str] = mapped_column(String(20), nullable=False)
    unit_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'concept' | 'decision' | 'bug_fix' | 'pattern'
    title: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str | None] = mapped_column(String(20), nullable=True)  # 'novice' | 'intermediate' | 'advanced'
    embedding_ref: Mapped[str | None] = mapped_column(Text, nullable=True)
    extracted_at: Mapped[object] = mapped_column(UTCDateTime, nullable=False, default=utcnow)
    deleted_at: Mapped[object | None] = mapped_column(UTCDateTime, nullable=True)

    __table_args__ = (
        Index("idx_knowledge_units_user_time", "user_id", "extracted_at"),
        Index("idx_knowledge_units_project", "project_id"),
    )


class KnowledgeUnitRelation(Base):
    __tablename__ = "knowledge_unit_relations"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=new_uuid)
    unit_id: Mapped[str] = mapped_column(GUID, ForeignKey("knowledge_units.id"), nullable=False)
    related_unit_id: Mapped[str] = mapped_column(GUID, ForeignKey("knowledge_units.id"), nullable=False)
    relation_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'recurs_as' | 'depends_on' | 'contrasts_with'
    created_at: Mapped[object] = mapped_column(UTCDateTime, nullable=False, default=utcnow)

    __table_args__ = (Index("idx_ku_relations_unit", "unit_id"),)


class FormatDecision(Base):
    __tablename__ = "format_decisions"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=new_uuid)
    unit_id: Mapped[str] = mapped_column(GUID, ForeignKey("knowledge_units.id"), nullable=False)
    detected_type: Mapped[str] = mapped_column(String(30), nullable=False)
    # 'flashcard' | 'qa' | 'diagram' | 'retrieval_practice' | 'synthesis' | 'self_explanation'
    chosen_format: Mapped[str] = mapped_column(String(30), nullable=False)
    rule_version: Mapped[str] = mapped_column(String(20), nullable=False)
    signal: Mapped[str | None] = mapped_column(Text, nullable=True)  # audit trail of what triggered the decision
    created_at: Mapped[object] = mapped_column(UTCDateTime, nullable=False, default=utcnow)
