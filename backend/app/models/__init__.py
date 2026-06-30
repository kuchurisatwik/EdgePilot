"""SQLAlchemy models package.

Import every model module here so that ``Base.metadata`` is fully populated for
Alembic autogenerate and for ``create_all`` in tests. Models are added per phase
(M1: user, M2: strategy, M3: trade, ...).
"""

from app.models.base import Base  # noqa: F401
from app.models.market_context import (  # noqa: F401
    MarketContext,
    MarketDataSource,
    MarketSession,
    MarketTrend,
    VolatilityRegime,
)
from app.models.rule import RiskRule, RuleSeverity, RuleStatus, RuleType  # noqa: F401
from app.models.strategy import RiskAppetite, Strategy  # noqa: F401
from app.models.trade import (  # noqa: F401
    OrderType,
    Trade,
    TradeDirection,
    TradeResult,
    TradeStatus,
)
from app.models.user import RefreshToken, User, UserSettings  # noqa: F401

__all__ = [
    "Base",
    "User",
    "UserSettings",
    "RefreshToken",
    "Strategy",
    "RiskAppetite",
    "RiskRule",
    "RuleType",
    "RuleSeverity",
    "RuleStatus",
    "Trade",
    "TradeDirection",
    "OrderType",
    "TradeStatus",
    "TradeResult",
    "MarketContext",
    "MarketTrend",
    "MarketSession",
    "VolatilityRegime",
    "MarketDataSource",
]
