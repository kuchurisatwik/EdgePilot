"""Analytics service — loads trades and delegates to the pure engine."""

import uuid
from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.trade import Trade
from app.repositories import trade_repo, user_repo
from app.schemas.analytics import (
    AnalyticsSummary,
    DashboardSummary,
    EquityCurveResponse,
    EquityPointOut,
    GroupPerformanceOut,
)
from app.services import analytics_engine
from app.services.analytics_engine import StatsSummary, TradeStat

_SESSION_LABELS = {"asia": "Asia", "london": "London", "newyork": "New York"}


def _settings(db: Session, user_id: uuid.UUID):
    settings = user_repo.get_settings(db, user_id)
    if settings is None:
        raise NotFoundError("Settings not found.")
    return settings


def _to_stat(t: Trade) -> TradeStat:
    when = t.opened_at or t.closed_at or t.created_at
    return TradeStat(
        pnl=t.pnl if t.pnl is not None else Decimal(0),
        r_multiple=t.r_multiple,
        closed_at=t.closed_at or t.created_at,
        strategy_id=str(t.strategy_id),
        strategy_name=t.strategy.name,
        risk_amount=t.risk_amount,
        session=analytics_engine.derive_session(when),
    )


def _closed_stats(db: Session, user_id: uuid.UUID) -> list[TradeStat]:
    return [_to_stat(t) for t in trade_repo.list_closed(db, user_id)]


def _start_of_day(now: datetime) -> datetime:
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


def _group_out(key: str, label: str, s: StatsSummary) -> GroupPerformanceOut:
    return GroupPerformanceOut(
        key=key,
        label=label,
        trade_count=s.trade_count,
        win_rate=s.win_rate,
        profit_factor=s.profit_factor,
        expectancy=s.expectancy,
        average_r=s.average_r,
        net_pnl=s.net_pnl,
    )


def get_summary(db: Session, user_id: uuid.UUID) -> AnalyticsSummary:
    stats = _closed_stats(db, user_id)
    summary = analytics_engine.summarize(stats)
    points = analytics_engine.equity_curve(stats, _settings(db, user_id).account_size)
    max_dd = analytics_engine.max_drawdown(points)

    pcts = [
        p.drawdown / (p.equity + p.drawdown) * Decimal(100)
        for p in points
        if (p.equity + p.drawdown) > 0
    ]
    max_dd_pct = max(pcts).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if pcts else None

    return AnalyticsSummary(
        trade_count=summary.trade_count,
        win_rate=summary.win_rate,
        profit_factor=summary.profit_factor,
        expectancy=summary.expectancy,
        average_r=summary.average_r,
        net_pnl=summary.net_pnl,
        gross_profit=summary.gross_profit,
        gross_loss=summary.gross_loss,
        max_drawdown=max_dd,
        max_drawdown_pct=max_dd_pct,
    )


def get_equity_curve(db: Session, user_id: uuid.UUID) -> EquityCurveResponse:
    account = _settings(db, user_id).account_size
    points = analytics_engine.equity_curve(_closed_stats(db, user_id), account)
    return EquityCurveResponse(
        starting_balance=account,
        points=[
            EquityPointOut(date=p.date, equity=p.equity, drawdown=p.drawdown) for p in points
        ],
    )


def get_strategy_performance(db: Session, user_id: uuid.UUID) -> list[GroupPerformanceOut]:
    stats = _closed_stats(db, user_id)
    names = {s.strategy_id: s.strategy_name for s in stats}
    groups = analytics_engine.group_performance(stats, key_fn=lambda s: s.strategy_id)
    return [_group_out(key, names.get(key, key), summary) for key, summary in groups]


def get_session_performance(db: Session, user_id: uuid.UUID) -> list[GroupPerformanceOut]:
    stats = _closed_stats(db, user_id)
    groups = analytics_engine.group_performance(stats, key_fn=lambda s: s.session)
    return [_group_out(key, _SESSION_LABELS.get(key, key), summary) for key, summary in groups]


def get_period_performance(
    db: Session, user_id: uuid.UUID, period: str
) -> list[GroupPerformanceOut]:
    stats = _closed_stats(db, user_id)
    if period == "weekly":
        groups = analytics_engine.group_performance(
            stats,
            key_fn=lambda s: f"{s.closed_at.isocalendar()[0]}-W{s.closed_at.isocalendar()[1]:02d}",
        )
    else:
        groups = analytics_engine.group_performance(
            stats, key_fn=lambda s: s.closed_at.strftime("%Y-%m")
        )
    groups.sort(key=lambda kv: kv[0])
    return [_group_out(key, key, summary) for key, summary in groups]


def get_dashboard(db: Session, user_id: uuid.UUID) -> DashboardSummary:
    settings = _settings(db, user_id)
    closed = trade_repo.list_closed(db, user_id)
    open_trades = trade_repo.list_open(db, user_id)
    stats = [_to_stat(t) for t in closed]

    realized = sum((s.pnl for s in stats), Decimal(0))
    today = trade_repo.realized_pnl_since(db, user_id, _start_of_day(datetime.now(UTC)))
    risk_exposure = sum((t.risk_amount for t in open_trades), Decimal(0))
    points = analytics_engine.equity_curve(stats, settings.account_size)

    latest = trade_repo.latest(db, user_id)
    score = (
        analytics_engine.trade_score(
            rr_ratio=latest.rr_ratio,
            risk_pct=latest.risk_pct,
            default_risk_pct=settings.default_risk_pct,
            rule_overridden=latest.rule_overridden,
        )
        if latest is not None
        else None
    )

    return DashboardSummary(
        quote_currency=settings.quote_currency,
        account_size=settings.account_size,
        account_balance=settings.account_size + realized,
        realized_pnl=realized,
        today_pnl=today,
        risk_exposure=risk_exposure,
        current_drawdown=analytics_engine.current_drawdown(points),
        trade_score=score,
        open_trades=len(open_trades),
        closed_trades=len(closed),
    )
