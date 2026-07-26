"""Declarative base and portable column types (SQLite dev <-> Postgres prod)."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import CHAR, DateTime, TypeDecorator
from sqlalchemy.orm import DeclarativeBase


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class GUID(TypeDecorator):
    """Stores UUIDs as CHAR(36) strings — portable between SQLite and Postgres."""

    impl = CHAR(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return str(value)

    def process_result_value(self, value, dialect):
        return value


class UTCDateTime(TypeDecorator):
    """Timezone-aware datetimes; SQLite drops tzinfo so we re-attach UTC on read."""

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None and value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value

    def process_result_value(self, value, dialect):
        if value is not None and value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value


def new_uuid() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass
