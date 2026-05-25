from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Bill, Transaction, User
from app.shared.enums import TransactionType


def calculate_safe_to_spend(db: Session, user: User, month_start: date, month_end: date) -> dict:
    latest_balance = db.scalar(
        select(Transaction.balance_after_transaction)
        .where(
            Transaction.user_id == user.id,
            Transaction.balance_after_transaction.is_not(None),
            Transaction.deleted_at.is_(None),
        )
        .order_by(Transaction.transaction_date.desc())
    )
    income = sum(
        Decimal(tx.amount)
        for tx in db.scalars(
            select(Transaction).where(
                Transaction.user_id == user.id,
                Transaction.transaction_date.between(month_start, month_end),
                Transaction.transaction_type == TransactionType.INCOME,
                Transaction.deleted_at.is_(None),
            )
        )
    )
    expenses = sum(
        Decimal(tx.amount)
        for tx in db.scalars(
            select(Transaction).where(
                Transaction.user_id == user.id,
                Transaction.transaction_date.between(month_start, month_end),
                Transaction.transaction_type == TransactionType.EXPENSE,
                Transaction.is_duplicate.is_(False),
                Transaction.deleted_at.is_(None),
            )
        )
    )
    today = date.today()
    horizon = today + timedelta(days=30)
    upcoming_bills = sum(
        Decimal(bill.expected_amount)
        for bill in db.scalars(
            select(Bill).where(
                Bill.user_id == user.id,
                Bill.status == "active",
                Bill.next_due_date.between(today, horizon),
            )
        )
    )
    credit_card_dues = sum(
        Decimal(tx.amount)
        for tx in db.scalars(
            select(Transaction).where(
                Transaction.user_id == user.id,
                Transaction.transaction_date.between(month_start, month_end),
                Transaction.payment_method == "credit_card",
                Transaction.transaction_type == TransactionType.EXPENSE,
                Transaction.is_duplicate.is_(False),
                Transaction.deleted_at.is_(None),
            )
        )
    )
    available = Decimal(latest_balance) if latest_balance is not None else income - expenses
    savings_remaining = max(Decimal("0"), Decimal(user.savings_goal_amount) - max(Decimal("0"), income - expenses))
    calculated = available - upcoming_bills - credit_card_dues - savings_remaining - Decimal(user.minimum_buffer_amount)
    safe_amount = max(Decimal("0"), calculated)
    return {
        "amount": float(safe_amount),
        "available_basis": "latest balance" if latest_balance is not None else "income minus expenses so far",
        "deductions": {
            "upcoming_bills": float(upcoming_bills),
            "credit_card_dues": float(credit_card_dues),
            "savings_goal_remaining": float(savings_remaining),
            "minimum_buffer": float(user.minimum_buffer_amount),
        },
        "explanation": (
            "Estimated safe-to-spend is calculated after setting aside upcoming bills, credit card dues, "
            "your remaining savings goal, and minimum buffer. It is a planning estimate, not a guarantee."
        ),
    }

