from datetime import timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deduplication.fuzzy_matcher import similarity
from app.models import Transaction


def find_duplicate(db: Session, candidate: Transaction) -> tuple[Transaction | None, str, int]:
    exact = db.scalar(
        select(Transaction).where(
            Transaction.user_id == candidate.user_id,
            Transaction.fingerprint == candidate.fingerprint,
            Transaction.is_duplicate.is_(False),
            Transaction.deleted_at.is_(None),
        )
    )
    if exact:
        return exact, "Exact fingerprint match", 100

    start = candidate.transaction_date - timedelta(days=1)
    end = candidate.transaction_date + timedelta(days=1)
    nearby = db.scalars(
        select(Transaction).where(
            Transaction.user_id == candidate.user_id,
            Transaction.transaction_date.between(start, end),
            Transaction.transaction_type == candidate.transaction_type,
            Transaction.is_duplicate.is_(False),
            Transaction.deleted_at.is_(None),
        )
    ).all()

    for existing in nearby:
        if abs(Decimal(existing.amount) - Decimal(candidate.amount)) > Decimal("1"):
            continue
        if existing.reference_id and candidate.reference_id and existing.reference_id == candidate.reference_id:
            return existing, "Reference ID match within date window", 98
        score = max(
            similarity(existing.merchant_name, candidate.merchant_name),
            similarity(existing.raw_description, candidate.raw_description),
        )
        if score >= 82:
            return existing, "Fuzzy merchant/date/amount match", score
    return None, "", 0

