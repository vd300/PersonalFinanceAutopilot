from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class SubscriptionCreate(BaseModel):
    merchant_name: str
    amount: Decimal
    frequency: str = "monthly"
    last_payment_date: date
    next_expected_payment_date: date
    status: str = "confirmed"


class SubscriptionUpdate(BaseModel):
    status: str | None = None
    amount: Decimal | None = None
    frequency: str | None = None
    next_expected_payment_date: date | None = None


class SubscriptionResponse(BaseModel):
    id: str
    merchant_name: str
    amount: float
    frequency: str
    last_payment_date: str
    next_expected_payment_date: str
    status: str
    confidence_score: int

