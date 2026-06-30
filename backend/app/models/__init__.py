"""SQLAlchemy models package.

Import every model module here so that ``Base.metadata`` is fully populated for
Alembic autogenerate and for ``create_all`` in tests. Models are added per phase
(M1: user, M2: strategy, M3: trade, ...).
"""

from app.models.base import Base  # noqa: F401

__all__ = ["Base"]
