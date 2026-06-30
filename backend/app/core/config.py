"""Application configuration via pydantic-settings.

All settings are read from environment variables (case-insensitive) and, for
local host development, from a `.env` file at the repo root or the backend dir.
In Docker the variables are injected directly by docker-compose.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Core
    env: str = "development"
    log_level: str = "INFO"

    # Database
    database_url: str = "postgresql+psycopg://trader:trader@localhost:5432/trader_copilot"

    # Auth / JWT
    jwt_secret: str = "dev-only-insecure-secret-change-me-0123456789abcdef"
    jwt_algorithm: str = "HS256"
    access_token_expire_min: int = 15
    refresh_token_expire_days: int = 7

    # Frontend origin (CORS)
    frontend_origin: str = "http://localhost:3000"

    # Refresh-token cookie (httpOnly). Set cookie_secure=true behind HTTPS.
    refresh_cookie_name: str = "tc_refresh"
    cookie_secure: bool = False
    cookie_samesite: str = "lax"
    cookie_path: str = "/api/auth"

    # Storage (local FS in MVP)
    screenshot_dir: str = "./storage/screenshots"

    # Market data provider (M7): "stub" in MVP
    market_data_provider: str = "stub"

    # AI (M9+)
    ai_model: str = "claude-opus-4-8"
    anthropic_api_key: str = ""
    # Data-sufficiency + similarity thresholds (sensible defaults; tune with data).
    ai_sufficient_days: int = 7
    ai_min_strategy_trades: int = 20
    ai_min_matches: int = 5
    ai_min_similarity: float = 0.6


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
