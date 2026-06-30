"""Auth endpoints: register, login, refresh, logout, me."""

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import LoginRequest, MessageResponse, RegisterRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services import auth_service
from app.services.auth_service import AuthResult

router = APIRouter()


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,  # type: ignore[arg-type]
        path=settings.cookie_path,
        max_age=settings.refresh_token_expire_days * 86_400,
    )


def _token_response(response: Response, result: AuthResult) -> TokenResponse:
    _set_refresh_cookie(response, result.refresh_token)
    return TokenResponse(
        access_token=result.access_token,
        user=UserResponse.model_validate(result.user),
    )


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(
    payload: RegisterRequest, response: Response, db: Session = Depends(get_db)
) -> TokenResponse:
    return _token_response(response, auth_service.register(db, payload))


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest, response: Response, db: Session = Depends(get_db)
) -> TokenResponse:
    return _token_response(response, auth_service.login(db, payload))


@router.post("/refresh", response_model=TokenResponse)
def refresh(request: Request, response: Response, db: Session = Depends(get_db)) -> TokenResponse:
    raw = request.cookies.get(settings.refresh_cookie_name)
    return _token_response(response, auth_service.refresh(db, raw))


@router.post("/logout", response_model=MessageResponse)
def logout(
    request: Request, response: Response, db: Session = Depends(get_db)
) -> MessageResponse:
    raw = request.cookies.get(settings.refresh_cookie_name)
    auth_service.logout(db, raw)
    response.delete_cookie(settings.refresh_cookie_name, path=settings.cookie_path)
    return MessageResponse(message="Logged out.")


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)
