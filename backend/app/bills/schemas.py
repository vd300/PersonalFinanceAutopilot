from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class BillCreate(BaseModel):
    name: str
    expected_amount: Decimal
    due_day: int = Field(ge=1, le=31)
    next_due_date: date
    frequency: str = "monthly"


class BillUpdate(BaseModel):
    name: str | None = None
    expected_amount: Decimal | None = None
    due_day: int | None = Field(default=None, ge=1, le=31)
    next_due_date: date | None = None
    frequency: str | None = None
    status: str | None = None


class BillResponse(BaseModel):
    id: str
    name: str
    expected_amount: float
    due_day: int
    next_due_date: str
    frequency: str
    is_auto_detected: bool
    status: str

