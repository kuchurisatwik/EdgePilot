"""User + settings response/update schemas."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    name: str
    created_at: datetime


class UserSettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_size: Decimal
    default_risk_pct: Decimal
    quote_currency: str
    timezone: str


class UserSettingsUpdate(BaseModel):
    account_size: Decimal | None = Field(default=None, ge=0)
    default_risk_pct: Decimal | None = Field(default=None, gt=0, le=100)
    quote_currency: str | None = Field(default=None, min_length=2, max_length=10)
    timezone: str | None = Field(default=None, min_length=1, max_length=64)


class ProfileUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
