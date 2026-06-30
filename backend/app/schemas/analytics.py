"""Analytics response schemas."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class AnalyticsSummary(BaseModel):
    trade_count: int
    win_rate: Decimal | None
    profit_factor: Decimal | None
    expectancy: Decimal | None
    average_r: Decimal | None
    net_pnl: Decimal
    gross_profit: Decimal
    gross_loss: Decimal
    max_drawdown: Decimal
    max_drawdown_pct: Decimal | None


class EquityPointOut(BaseModel):
    date: datetime
    equity: Decimal
    drawdown: Decimal


class EquityCurveResponse(BaseModel):
    starting_balance: Decimal
    points: list[EquityPointOut]


class GroupPerformanceOut(BaseModel):
    key: str
    label: str
    trade_count: int
    win_rate: Decimal | None
    profit_factor: Decimal | None
    expectancy: Decimal | None
    average_r: Decimal | None
    net_pnl: Decimal


class DashboardSummary(BaseModel):
    quote_currency: str
    account_size: Decimal
    account_balance: Decimal
    realized_pnl: Decimal
    today_pnl: Decimal
    risk_exposure: Decimal
    current_drawdown: Decimal
    trade_score: int | None
    open_trades: int
    closed_trades: int
