"""Data-sufficiency policy (SOC §10).

AI may only speak when there is enough history. Otherwise the caller returns the
canonical insufficient-data string and never fabricates confidence.
"""

from datetime import UTC, datetime

from app.core.config import settings
from app.models.user import User

INSUFFICIENT_DATA = "Not enough historical data available for a reliable recommendation."


def days_active(user: User) -> int:
    created = user.created_at
    if created.tzinfo is None:
        created = created.replace(tzinfo=UTC)
    return (datetime.now(UTC) - created).days


def has_sufficient_data(user: User, closed_trade_count: int) -> bool:
    return (
        days_active(user) >= settings.ai_sufficient_days
        or closed_trade_count >= settings.ai_min_strategy_trades
    )
