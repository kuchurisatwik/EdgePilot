"""Screenshot model — chart images linked to a trade (future AI vision data)."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class ScreenshotSlot(enum.StrEnum):
    entry_trade_tf = "entry_trade_tf"
    entry_higher_tf = "entry_higher_tf"
    exit_trade_tf = "exit_trade_tf"
    exit_higher_tf = "exit_higher_tf"


class Screenshot(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "screenshots"
    __table_args__ = (UniqueConstraint("trade_id", "slot", name="uq_screenshot_trade_slot"),)

    trade_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("trades.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    slot: Mapped[ScreenshotSlot] = mapped_column(
        Enum(ScreenshotSlot, native_enum=False, length=20), nullable=False
    )
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(60), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
