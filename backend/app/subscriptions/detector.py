from collections import defaultdict
from datetime import timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Alert, Subscription, Transaction
from app.shared.enums import AlertType, Frequency, TransactionType

SUBSCRIPTION_KEYWORDS = ["netflix", "spotify", "prime", "hotstar", "youtube", "icloud", "gym", "broadband"]


def detect_subscriptions(db: Session, user_id: str) -> None:
    transactions = db.scalars(
        select(Transaction).where(
            Transaction.user_id == user_id,
            Transaction.transaction_type == TransactionType.EXPENSE,
            Transaction.is_duplicate.is_(False),
            Transaction.deleted_at.is_(None),
        )
    ).all()
    grouped: dict[str, list[Transaction]] = defaultdict(list)
    for transaction in transactions:
        grouped[(transaction.merchant_name or transaction.display_name or "Unknown").lower()].append(transaction)

    for merchant_key, group in grouped.items():
        keyword_hit = any(keyword in merchant_key for keyword in SUBSCRIPTION_KEYWORDS)
        if len(group) < 2 and not keyword_hit:
            continue
        group = sorted(group, key=lambda tx: tx.transaction_date)
        amounts = [Decimal(tx.amount) for tx in group]
        average = sum(amounts) / Decimal(len(amounts))
        similar_amounts = all(abs(amount - average) <= max(Decimal("50"), average * Decimal("0.15")) for amount in amounts)
        if not similar_amounts and not keyword_hit:
            continue
        last = group[-1]
        frequency = Frequency.MONTHLY
        next_date = last.transaction_date + timedelta(days=30)
        merchant_name = last.merchant_name or last.display_name or merchant_key.title()
        existing = db.scalar(
            select(Subscription).where(Subscription.user_id == user_id, Subscription.merchant_name == merchant_name)
        )
        if existing:
            existing.amount = average
            existing.last_payment_date = last.transaction_date
            existing.next_expected_payment_date = next_date
        else:
            subscription = Subscription(
                user_id=user_id,
                merchant_name=merchant_name,
                amount=average,
                frequency=frequency,
                last_payment_date=last.transaction_date,
                next_expected_payment_date=next_date,
                category_id=last.category_id,
                confidence_score=85 if keyword_hit else 70,
                source_type=last.source_type,
            )
            db.add(subscription)
            db.flush()
            db.add(
                Alert(
                    user_id=user_id,
                    alert_type=AlertType.SUBSCRIPTION_DETECTED,
                    title=f"{merchant_name} looks recurring",
                    message=f"We detected a likely {frequency} payment of INR {float(average):,.0f}.",
                    severity="low",
                    related_subscription_id=subscription.id,
                )
            )

