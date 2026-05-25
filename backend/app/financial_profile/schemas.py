from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.shared.enums import FinancialMode


class FinancialProfileUpdate(BaseModel):
    financial_mode: FinancialMode | None = None
    available_balance: Decimal | None = Field(default=None, ge=0)
    monthly_income_amount: Decimal | None = Field(default=None, ge=0)
    monthly_income_day: int | None = Field(default=None, ge=1, le=31)
    expected_income_amount: Decimal | None = Field(default=None, ge=0)
    expected_income_date: date | None = None
    monthly_essential_expense_estimate: Decimal | None = Field(default=None, ge=0)
    monthly_non_essential_expense_estimate: Decimal | None = Field(default=None, ge=0)
    minimum_emergency_buffer: Decimal | None = Field(default=None, ge=0)
    savings_goal_amount: Decimal | None = Field(default=None, ge=0)
    credit_card_due_amount: Decimal | None = Field(default=None, ge=0)
    credit_card_due_date: date | None = None


class FinancialProfileResponse(BaseModel):
    id: str
    user_id: str
    financial_mode: FinancialMode
    available_balance: Decimal
    monthly_income_amount: Decimal | None
    monthly_income_day: int | None
    expected_income_amount: Decimal | None
    expected_income_date: date | None
    monthly_essential_expense_estimate: Decimal
    monthly_non_essential_expense_estimate: Decimal | None
    minimum_emergency_buffer: Decimal
    savings_goal_amount: Decimal
    credit_card_due_amount: Decimal | None
    credit_card_due_date: date | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
