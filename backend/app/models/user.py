from sqlalchemy import Boolean, ForeignKey, Index, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, GUID, UTCDateTime, new_uuid, utcnow


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=new_uuid)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    display_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    hashed_password: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[object] = mapped_column(UTCDateTime, nullable=False, default=utcnow)
    notification_prefs: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    learning_intensity: Mapped[str] = mapped_column(String(20), nullable=False, default="balanced")
    deleted_at: Mapped[object | None] = mapped_column(UTCDateTime, nullable=True)


class RefreshToken(Base):
    """Server-side refresh token record — enables rotation and revocation."""

    __tablename__ = "refresh_tokens"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(GUID, ForeignKey("users.id"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    expires_at: Mapped[object] = mapped_column(UTCDateTime, nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[object] = mapped_column(UTCDateTime, nullable=False, default=utcnow)

    __table_args__ = (Index("idx_refresh_tokens_user", "user_id"),)
