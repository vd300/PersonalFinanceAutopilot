from calendar import monthrange
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Transaction
from app.shared.enums import TransactionType


def month_bounds(month: str | None = None) -> tuple[date, date]:
    if month:
        year, month_number = [int(part) for part in month.split("-")]
    else:
        today = date.today()
        year, month_number = today.year, today.month
    last_day = monthrange(year, month_number)[1]
    return date(year, month_number, 1), date(year, month_number, last_day)


def calculate_cashflow(db: Session, user_id: str, month_start: date, month_end: date) -> dict:
    today = date.today()
    elapsed_days = max(1, min((today - month_start).days + 1, (month_end - month_start).days + 1))
    total_days = (month_end - month_start).days + 1
    remaining_days = max(0, total_days - elapsed_days)
    transactions = db.scalars(
        select(Transaction).where(
            Transaction.user_id == user_id,
            Transaction.transaction_date.between(month_start, month_end),
            Transaction.is_duplicate.is_(False),
            Transaction.deleted_at.is_(None),
        )
    ).all()
    income = sum(Decimal(tx.amount) for tx in transactions if tx.transaction_type == TransactionType.INCOME)
    expenses = sum(Decimal(tx.amount) for tx in transactions if tx.transaction_type == TransactionType.EXPENSE)
    daily_spend = expenses / Decimal(elapsed_days)
    projected_variable = daily_spend * Decimal(remaining_days)
    projected_expenses = expenses + projected_variable
    projected_savings = income - projected_expenses
    return {
        "projected_expenses": float(projected_expenses),
        "projected_savings": float(projected_savings),
        "average_daily_spend": float(daily_spend),
        "remaining_days": remaining_days,
        "confidence": "medium" if len(transactions) >= 10 else "low",
        "explanation": "Projection uses current month spending rate and remaining days in the month.",
    }

