"""Screenshot endpoints (multipart upload + authenticated streaming)."""

import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.screenshot import ScreenshotSlot
from app.models.user import User
from app.schemas.screenshot import ScreenshotResponse
from app.services import screenshot_service, trade_service
from app.services.storage.backend import get_storage_backend

router = APIRouter()


@router.post(
    "/trades/{trade_id}/screenshots",
    response_model=ScreenshotResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_screenshot(
    trade_id: uuid.UUID,
    slot: ScreenshotSlot = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ScreenshotResponse:
    trade = trade_service.get_trade(db, current_user.id, trade_id)  # 404 if not the user's
    content = file.file.read()
    screenshot = screenshot_service.upload(
        db,
        trade,
        slot,
        content=content,
        content_type=file.content_type,
        original_filename=file.filename,
    )
    return ScreenshotResponse.from_model(screenshot)


@router.get("/trades/{trade_id}/screenshots", response_model=list[ScreenshotResponse])
def list_screenshots(
    trade_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ScreenshotResponse]:
    trade_service.get_trade(db, current_user.id, trade_id)  # ownership check
    return [
        ScreenshotResponse.from_model(s)
        for s in screenshot_service.list_for_trade(db, trade_id)
    ]


@router.get("/screenshots/{screenshot_id}")
def stream_screenshot(
    screenshot_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FileResponse:
    screenshot = screenshot_service.get(db, current_user.id, screenshot_id)
    path = get_storage_backend().full_path(screenshot.file_path)
    return FileResponse(path, media_type=screenshot.content_type)


@router.delete("/screenshots/{screenshot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_screenshot(
    screenshot_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    screenshot_service.delete(db, current_user.id, screenshot_id)
