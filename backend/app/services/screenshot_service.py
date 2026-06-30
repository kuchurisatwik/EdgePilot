"""Screenshot upload/list/delete (local storage in MVP)."""

import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationError
from app.models.screenshot import Screenshot, ScreenshotSlot
from app.models.trade import Trade
from app.repositories import screenshot_repo
from app.services.storage.backend import (
    ALLOWED_CONTENT_TYPES,
    MAX_SIZE_BYTES,
    get_storage_backend,
)


def upload(
    db: Session,
    trade: Trade,
    slot: ScreenshotSlot,
    *,
    content: bytes,
    content_type: str | None,
    original_filename: str | None,
) -> Screenshot:
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise ValidationError(
            "Only PNG, JPEG or WebP images are allowed.", code="bad_image_type"
        )
    if len(content) == 0:
        raise ValidationError("The uploaded file is empty.", code="empty_file")
    if len(content) > MAX_SIZE_BYTES:
        raise ValidationError("Image exceeds the 5 MB limit.", code="file_too_large")

    storage = get_storage_backend()
    stored = storage.save(
        trade.user_id, trade.id, slot.value, content=content, content_type=content_type
    )

    existing = screenshot_repo.get_for_slot(db, trade.id, slot)
    captured_at = datetime.now(UTC)
    if existing is not None:
        # Replace the file + row for this slot.
        if existing.file_path != stored.file_path:
            storage.delete(existing.file_path)
        existing.file_path = stored.file_path
        existing.original_filename = original_filename or stored.file_path
        existing.content_type = stored.content_type
        existing.size_bytes = stored.size_bytes
        existing.captured_at = captured_at
        db.flush()
        return existing

    screenshot = Screenshot(
        trade_id=trade.id,
        user_id=trade.user_id,
        slot=slot,
        file_path=stored.file_path,
        original_filename=original_filename or stored.file_path,
        content_type=stored.content_type,
        size_bytes=stored.size_bytes,
        captured_at=captured_at,
    )
    return screenshot_repo.add(db, screenshot)


def list_for_trade(db: Session, trade_id: uuid.UUID) -> list[Screenshot]:
    return screenshot_repo.list_for_trade(db, trade_id)


def get(db: Session, user_id: uuid.UUID, screenshot_id: uuid.UUID) -> Screenshot:
    screenshot = screenshot_repo.get(db, user_id, screenshot_id)
    if screenshot is None:
        raise NotFoundError("Screenshot not found.")
    return screenshot


def delete(db: Session, user_id: uuid.UUID, screenshot_id: uuid.UUID) -> None:
    screenshot = get(db, user_id, screenshot_id)
    get_storage_backend().delete(screenshot.file_path)
    screenshot_repo.delete(db, screenshot)
