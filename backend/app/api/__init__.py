"""Aggregate API router. Domain routers are mounted here per phase."""

from fastapi import APIRouter

from app.api.auth.routes import router as auth_router
from app.api.health.routes import router as health_router
from app.api.risk.routes import router as risk_router
from app.api.rules.routes import router as rules_router
from app.api.settings.routes import router as settings_router
from app.api.strategies.routes import router as strategy_router
from app.api.trades.routes import router as trade_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])  # M1
api_router.include_router(settings_router, tags=["settings"])  # M1
api_router.include_router(strategy_router, prefix="/strategies", tags=["strategies"])  # M2
api_router.include_router(risk_router, prefix="/risk", tags=["risk"])  # M3
api_router.include_router(trade_router, prefix="/trades", tags=["trades"])  # M3
api_router.include_router(rules_router, prefix="/rules", tags=["rules"])  # M4
