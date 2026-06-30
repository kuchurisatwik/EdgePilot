"""Declarative base + shared mixins.

Every table uses a UUID primary key and created/updated timestamps. We use
SQLAlchemy's dialect-agnostic ``Uuid`` and ``DateTime`` types so the same models
run on PostgreSQL (production) and SQLite (fast unit/integration tests).
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Uuid, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class UUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


class TimestampMixin:
    # Python-side defaults guarantee values are populated right after flush on
    # every dialect; server_default keeps DB-level inserts (migrations) correct.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        server_default=func.now(),
        onupdate=_utcnow,
        nullable=False,
    )
