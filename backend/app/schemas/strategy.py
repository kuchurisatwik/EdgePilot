"""Strategy request/response schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.strategy import RiskAppetite


class StrategyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    risk_appetite: RiskAppetite = RiskAppetite.moderate
    notes: str | None = Field(default=None, max_length=4000)


class StrategyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    risk_appetite: RiskAppetite | None = None
    notes: str | None = Field(default=None, max_length=4000)
    is_active: bool | None = None


class StrategyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    risk_appetite: RiskAppetite
    notes: str | None
    is_default: bool
    is_active: bool
    created_at: datetime
