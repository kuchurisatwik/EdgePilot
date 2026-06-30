"""Shared API dependencies.

``get_db`` is available now; ``get_current_user`` (JWT -> User, per-user
isolation) is added in M1.
"""

from app.core.database import get_db

__all__ = ["get_db"]
