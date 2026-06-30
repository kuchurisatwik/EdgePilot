"""Health / readiness endpoint."""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import get_db

router = APIRouter()
logger = logging.getLogger("app.health")


@router.get("/health")
def health(db: Session = Depends(get_db)) -> dict[str, str]:
    db_ok = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001 - report degraded rather than 500
        db_ok = False
        logger.warning("health_db_check_failed")
    return {
        "status": "ok" if db_ok else "degraded",
        "db": "ok" if db_ok else "down",
    }
