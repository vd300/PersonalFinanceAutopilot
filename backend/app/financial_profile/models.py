import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.shared.enums import FinancialMode


def new_uuid() -> str:
    return str(uuid.uuid4())


class FinancialProfile(Base):
    __tablename__ = "financial_profiles"
    __table_args__ = (UniqueConstraint("user_id", name="uq_financial_profiles_user_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    financial_mode: Mapped[str] = mapped_column(
        String(32), default=FinancialMode.SALARIED.value, nullable=False
    )
    available_balance: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=Decimal("0"), nullable=False
    )
    monthly_income_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    monthly_income_day: Mapped[int | None] = mapped_column(nullable=True)
    expected_income_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    expected_income_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    monthly_essential_expense_estimate: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=Decimal("0"), nullable=False
    )
    monthly_non_essential_expense_estimate: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2), nullable=True
    )
    minimum_emergency_buffer: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=Decimal("0"), nullable=False
    )
    savings_goal_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=Decimal("0"), nullable=False
    )
    credit_card_due_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    credit_card_due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
