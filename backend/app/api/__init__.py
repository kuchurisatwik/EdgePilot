"""Aggregate API router. Domain routers are mounted here per phase."""

from fastapi import APIRouter

from app.api.auth.routes import router as auth_router
from app.api.health.routes import router as health_router
from app.api.settings.routes import router as settings_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])  # M1
api_router.include_router(settings_router, tags=["settings"])  # M1

# Mounted in later phases:
# api_router.include_router(strategy_router, prefix="/strategies", ...)      # M2
# ...
