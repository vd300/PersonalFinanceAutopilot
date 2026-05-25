from collections import defaultdict
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Alert, Transaction
from app.shared.enums import AlertType, TransactionType


def detect_unusual_transactions(db: Session, user_id: str) -> None:
    transactions = db.scalars(
        select(Transaction).where(
            Transaction.user_id == user_id,
            Transaction.transaction_type == TransactionType.EXPENSE,
            Transaction.is_duplicate.is_(False),
            Transaction.deleted_at.is_(None),
        )
    ).all()
    by_category: dict[str, list[Transaction]] = defaultdict(list)
    for transaction in transactions:
        by_category[transaction.category_id or "uncategorized"].append(transaction)

    for group in by_category.values():
        if len(group) < 3:
            continue
        average = sum(Decimal(tx.amount) for tx in group) / Decimal(len(group))
        for transaction in group:
            if Decimal(transaction.amount) <= average * Decimal("2"):
                continue
            transaction.is_unusual = True
            exists = db.scalar(
                select(Alert).where(
                    Alert.user_id == user_id,
                    Alert.related_transaction_id == transaction.id,
                    Alert.alert_type == AlertType.UNUSUAL_TRANSACTION,
                )
            )
            if not exists:
                db.add(
                    Alert(
                        user_id=user_id,
                        alert_type=AlertType.UNUSUAL_TRANSACTION,
                        title="Unusual transaction detected",
                        message=f"{transaction.display_name or transaction.merchant_name} was higher than your usual spend in this category.",
                        severity="medium",
                        related_transaction_id=transaction.id,
                    )
                )

