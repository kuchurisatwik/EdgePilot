"""Screenshot response schema."""

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.screenshot import Screenshot, ScreenshotSlot


class ScreenshotResponse(BaseModel):
    id: uuid.UUID
    trade_id: uuid.UUID
    slot: ScreenshotSlot
    content_type: str
    size_bytes: int
    captured_at: datetime
    url: str  # authenticated stream endpoint

    @classmethod
    def from_model(cls, s: Screenshot) -> "ScreenshotResponse":
        return cls(
            id=s.id,
            trade_id=s.trade_id,
            slot=s.slot,
            content_type=s.content_type,
            size_bytes=s.size_bytes,
            captured_at=s.captured_at,
            url=f"/api/screenshots/{s.id}",
        )
