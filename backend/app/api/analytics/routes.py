"""Analytics endpoints — pure statistics (no AI)."""

from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.analytics import (
    AnalyticsSummary,
    DashboardSummary,
    EquityCurveResponse,
    GroupPerformanceOut,
)
from app.services import analytics_service

router = APIRouter()


@router.get("/summary", response_model=AnalyticsSummary)
def summary(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> AnalyticsSummary:
    return analytics_service.get_summary(db, current_user.id)


@router.get("/equity-curve", response_model=EquityCurveResponse)
def equity_curve(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> EquityCurveResponse:
    return analytics_service.get_equity_curve(db, current_user.id)


@router.get("/strategy", response_model=list[GroupPerformanceOut])
def strategy_performance(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[GroupPerformanceOut]:
    return analytics_service.get_strategy_performance(db, current_user.id)


@router.get("/session", response_model=list[GroupPerformanceOut])
def session_performance(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[GroupPerformanceOut]:
    return analytics_service.get_session_performance(db, current_user.id)


@router.get("/period", response_model=list[GroupPerformanceOut])
def period_performance(
    period: Literal["weekly", "monthly"] = Query(default="weekly"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[GroupPerformanceOut]:
    return analytics_service.get_period_performance(db, current_user.id, period)


@router.get("/dashboard", response_model=DashboardSummary)
def dashboard(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> DashboardSummary:
    return analytics_service.get_dashboard(db, current_user.id)
