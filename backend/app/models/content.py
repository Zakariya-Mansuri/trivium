from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, GUID, UTCDateTime, new_uuid, utcnow


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(GUID, ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[object] = mapped_column(UTCDateTime, nullable=False, default=utcnow)
    deleted_at: Mapped[object | None] = mapped_column(UTCDateTime, nullable=True)

    __table_args__ = (Index("idx_projects_user", "user_id"),)


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(GUID, ForeignKey("users.id"), nullable=False)
    project_id: Mapped[str | None] = mapped_column(GUID, ForeignKey("projects.id"), nullable=True)
    source_tool: Mapped[str] = mapped_column(String(50), nullable=False)  # 'native' | 'claude_code' | 'cursor' | ...
    source_fidelity: Mapped[str] = mapped_column(String(20), nullable=False)  # 'native' | 'wrapped'
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[object] = mapped_column(UTCDateTime, nullable=False)
    ended_at: Mapped[object | None] = mapped_column(UTCDateTime, nullable=True)
    raw_log_ref: Mapped[str | None] = mapped_column(Text, nullable=True)
    extraction_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    # 'pending' | 'running' | 'completed' | 'failed' | 'insufficient_content'
    created_at: Mapped[object] = mapped_column(UTCDateTime, nullable=False, default=utcnow)

    messages: Mapped[list["Message"]] = relationship(
        back_populates="session", cascade="all, delete-orphan", order_by="Message.timestamp"
    )

    __table_args__ = (Index("idx_sessions_user_project", "user_id", "project_id"),)


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=new_uuid)
    session_id: Mapped[str] = mapped_column(GUID, ForeignKey("sessions.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # 'user' | 'assistant' | 'tool'
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # 'ai' | 'user' — MUST be set at generation time; Layer 3 metrics depend on it.
    authored_by: Mapped[str | None] = mapped_column(String(10), nullable=True)
    code_diff: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[object] = mapped_column(UTCDateTime, nullable=False)
    created_at: Mapped[object] = mapped_column(UTCDateTime, nullable=False, default=utcnow)

    session: Mapped[Session] = relationship(back_populates="messages")

    __table_args__ = (Index("idx_messages_session", "session_id", "timestamp"),)
