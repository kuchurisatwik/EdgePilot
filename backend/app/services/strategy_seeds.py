"""Default strategy definitions seeded per user (DRD Phase 2)."""

from app.models.strategy import RiskAppetite

DEFAULT_STRATEGIES: list[dict[str, object]] = [
    {
        "name": "Breakout",
        "description": "Enter as price breaks a defined level on expanding range/volume.",
        "risk_appetite": RiskAppetite.aggressive,
    },
    {
        "name": "Pullback",
        "description": "Buy/sell a retracement into a prevailing trend.",
        "risk_appetite": RiskAppetite.moderate,
    },
    {
        "name": "Reversal",
        "description": "Counter-trend entry at exhaustion / structure shift.",
        "risk_appetite": RiskAppetite.aggressive,
    },
    {
        "name": "Trend Following",
        "description": "Ride an established directional move; cut against the trend.",
        "risk_appetite": RiskAppetite.moderate,
    },
    {
        "name": "Scalping",
        "description": "Short-duration trades capturing small, frequent moves.",
        "risk_appetite": RiskAppetite.conservative,
    },
    {
        "name": "Range Trading",
        "description": "Fade the edges of a defined range until it breaks.",
        "risk_appetite": RiskAppetite.conservative,
    },
]
