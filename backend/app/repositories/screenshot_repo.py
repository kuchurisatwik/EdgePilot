"""Data access for screenshots. Scoped by user_id / trade_id."""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.screenshot import Screenshot, ScreenshotSlot


def get(db: Session, user_id: uuid.UUID, screenshot_id: uuid.UUID) -> Screenshot | None:
    return db.scalar(
        select(Screenshot).where(
            Screenshot.id == screenshot_id, Screenshot.user_id == user_id
        )
    )


def get_for_slot(db: Session, trade_id: uuid.UUID, slot: ScreenshotSlot) -> Screenshot | None:
    return db.scalar(
        select(Screenshot).where(Screenshot.trade_id == trade_id, Screenshot.slot == slot)
    )


def list_for_trade(db: Session, trade_id: uuid.UUID) -> list[Screenshot]:
    return list(
        db.scalars(
            select(Screenshot).where(Screenshot.trade_id == trade_id).order_by(Screenshot.slot)
        )
    )


def add(db: Session, screenshot: Screenshot) -> Screenshot:
    db.add(screenshot)
    db.flush()
    return screenshot


def delete(db: Session, screenshot: Screenshot) -> None:
    db.delete(screenshot)
    db.flush()
