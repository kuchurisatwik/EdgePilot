"""User settings + profile endpoints (per-user scoped via get_current_user)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.user import (
    ProfileUpdate,
    UserResponse,
    UserSettingsResponse,
    UserSettingsUpdate,
)
from app.services import settings_service

router = APIRouter()


@router.get("/settings", response_model=UserSettingsResponse)
def get_settings(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> UserSettingsResponse:
    settings = settings_service.get_settings(db, current_user.id)
    return UserSettingsResponse.model_validate(settings)


@router.put("/settings", response_model=UserSettingsResponse)
def update_settings(
    payload: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserSettingsResponse:
    settings = settings_service.update_settings(db, current_user.id, payload)
    return UserSettingsResponse.model_validate(settings)


@router.put("/profile", response_model=UserResponse)
def update_profile(
    payload: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    user = settings_service.update_profile(db, current_user, payload)
    return UserResponse.model_validate(user)
