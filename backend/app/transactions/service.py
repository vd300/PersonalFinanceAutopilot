from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import extract, select
from sqlalchemy.orm import Session

from app.categorization.service import save_user_category_rule
from app.models import Transaction
from app.transactions.schemas import TransactionUpdate


def list_transactions(
    db: Session,
    user_id: str,
    month: str | None = None,
    category_id: str | None = None,
    source_type: str | None = None,
    search: str | None = None,
) -> list[Transaction]:
    query = select(Transaction).where(Transaction.user_id == user_id, Transaction.deleted_at.is_(None))
    if month:
        parsed = datetime.strptime(month, "%Y-%m")
        query = query.where(
            extract("year", Transaction.transaction_date) == parsed.year,
            extract("month", Transaction.transaction_date) == parsed.month,
        )
    if category_id:
        query = query.where(Transaction.category_id == category_id)
    if source_type:
        query = query.where(Transaction.source_type == source_type)
    if search:
        like = f"%{search}%"
        query = query.where((Transaction.merchant_name.ilike(like)) | (Transaction.raw_description.ilike(like)))
    return list(db.scalars(query.order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())))


def update_transaction(db: Session, user_id: str, transaction_id: str, payload: TransactionUpdate) -> Transaction:
    transaction = db.get(Transaction, transaction_id)
    if not transaction or transaction.user_id != user_id or transaction.deleted_at:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    old_category_id = transaction.category_id
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(transaction, field, value)
    if payload.category_id and payload.category_id != old_category_id:
        save_user_category_rule(
            db,
            user_id,
            transaction.merchant_name or transaction.display_name or transaction.raw_description,
            payload.category_id,
            transaction.id,
        )
    db.commit()
    return transaction


def delete_transaction(db: Session, user_id: str, transaction_id: str) -> None:
    transaction = db.get(Transaction, transaction_id)
    if not transaction or transaction.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    transaction.deleted_at = datetime.utcnow()
    db.commit()

