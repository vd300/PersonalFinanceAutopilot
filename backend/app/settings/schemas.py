from decimal import Decimal

from pydantic import BaseModel, Field


class SettingsUpdate(BaseModel):
    preferred_currency: str | None = None
    monthly_income_day: int | None = Field(default=None, ge=1, le=31)
    savings_goal_amount: Decimal | None = None
    minimum_buffer_amount: Decimal | None = None


class SettingsResponse(BaseModel):
    preferred_currency: str
    monthly_income_day: int
    savings_goal_amount: float
    minimum_buffer_amount: float

