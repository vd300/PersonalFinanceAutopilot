from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Alert, Category, Transaction
from app.shared.enums import AlertType, TransactionType


def detect_overspending(db: Session, user_id: str) -> None:
    categories = db.scalars(select(Category)).all()
    for category in categories:
        spend = sum(
            Decimal(tx.amount)
            for tx in db.scalars(
                select(Transaction).where(
                    Transaction.user_id == user_id,
                    Transaction.category_id == category.id,
                    Transaction.transaction_type == TransactionType.EXPENSE,
                    Transaction.is_duplicate.is_(False),
                    Transaction.deleted_at.is_(None),
                )
            )
        )
        if spend > Decimal("10000") and category.name in {"Food & Dining", "Shopping", "Entertainment"}:
            exists = db.scalar(
                select(Alert).where(
                    Alert.user_id == user_id,
                    Alert.alert_type == AlertType.OVERSPENDING,
                    Alert.title == f"{category.name} spend is high",
                    Alert.status == "active",
                )
            )
            if not exists:
                db.add(
                    Alert(
                        user_id=user_id,
                        alert_type=AlertType.OVERSPENDING,
                        title=f"{category.name} spend is high",
                        message=f"You have spent INR {float(spend):,.0f} on {category.name}. Review this category before the next large purchase.",
                        severity="medium",
                    )
                )

