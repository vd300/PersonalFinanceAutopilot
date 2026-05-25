from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.insights.cashflow import calculate_cashflow, month_bounds
from app.insights.safe_to_spend import calculate_safe_to_spend
from app.models import Alert, Bill, Subscription, Transaction, User
from app.shared.enums import TransactionType


def monthly_dashboard(db: Session, user: User, month: str | None = None) -> dict:
    start, end = month_bounds(month)
    transactions = db.scalars(
        select(Transaction).where(
            Transaction.user_id == user.id,
            Transaction.transaction_date.between(start, end),
            Transaction.is_duplicate.is_(False),
            Transaction.deleted_at.is_(None),
        )
    ).all()
    income = sum(Decimal(tx.amount) for tx in transactions if tx.transaction_type == TransactionType.INCOME)
    expenses = sum(Decimal(tx.amount) for tx in transactions if tx.transaction_type == TransactionType.EXPENSE)
    transfers = sum(Decimal(tx.amount) for tx in transactions if tx.transaction_type == TransactionType.TRANSFER)

    by_category: dict[str, Decimal] = defaultdict(Decimal)
    by_source: dict[str, Decimal] = defaultdict(Decimal)
    by_method: dict[str, Decimal] = defaultdict(Decimal)
    for tx in transactions:
        if tx.transaction_type != TransactionType.EXPENSE:
            continue
        by_category[tx.category.name if tx.category else "Other"] += Decimal(tx.amount)
        by_source[tx.source_type] += Decimal(tx.amount)
        by_method[tx.payment_method] += Decimal(tx.amount)

    today = date.today()
    upcoming_bills = db.scalars(
        select(Bill).where(
            Bill.user_id == user.id,
            Bill.status == "active",
            Bill.next_due_date.between(today, today + timedelta(days=30)),
        )
    ).all()
    subscriptions = db.scalars(
        select(Subscription).where(Subscription.user_id == user.id, Subscription.status.in_(["detected", "confirmed"]))
    ).all()
    alerts = db.scalars(
        select(Alert).where(Alert.user_id == user.id, Alert.status == "active").order_by(Alert.created_at.desc())
    ).all()
    credit_card_due = sum(
        Decimal(tx.amount)
        for tx in transactions
        if tx.payment_method == "credit_card" and tx.transaction_type == TransactionType.EXPENSE
    )

    return {
        "month": start.strftime("%Y-%m"),
        "summary": {
            "income": float(income),
            "expenses": float(expenses),
            "net_savings": float(income - expenses),
            "transfers": float(transfers),
            "transaction_count": len(transactions),
            "average_daily_spend": float(expenses / Decimal(max(1, (min(date.today(), end) - start).days + 1))),
            "credit_card_due": float(credit_card_due),
        },
        "category_breakdown": [{"name": key, "amount": float(value)} for key, value in sorted(by_category.items())],
        "source_breakdown": [{"name": key, "amount": float(value)} for key, value in sorted(by_source.items())],
        "payment_method_breakdown": [{"name": key, "amount": float(value)} for key, value in sorted(by_method.items())],
        "largest_expenses": [
            {
                "id": tx.id,
                "date": tx.transaction_date.isoformat(),
                "merchant": tx.display_name or tx.merchant_name,
                "amount": float(tx.amount),
                "category": tx.category.name if tx.category else "Other",
            }
            for tx in sorted(
                [tx for tx in transactions if tx.transaction_type == TransactionType.EXPENSE],
                key=lambda item: item.amount,
                reverse=True,
            )[:5]
        ],
        "upcoming_bills": [
            {
                "id": bill.id,
                "name": bill.name,
                "expected_amount": float(bill.expected_amount),
                "next_due_date": bill.next_due_date.isoformat(),
                "is_auto_detected": bill.is_auto_detected,
            }
            for bill in upcoming_bills
        ],
        "subscriptions": [
            {
                "id": sub.id,
                "merchant_name": sub.merchant_name,
                "amount": float(sub.amount),
                "frequency": sub.frequency,
                "next_expected_payment_date": sub.next_expected_payment_date.isoformat(),
                "status": sub.status,
                "confidence_score": sub.confidence_score,
            }
            for sub in subscriptions
        ],
        "alerts": [
            {"id": alert.id, "title": alert.title, "message": alert.message, "severity": alert.severity}
            for alert in alerts[:6]
        ],
        "safe_to_spend": calculate_safe_to_spend(db, user, start, end),
        "cashflow_projection": calculate_cashflow(db, user.id, start, end),
    }

