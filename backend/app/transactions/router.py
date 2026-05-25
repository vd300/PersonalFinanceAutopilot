from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.models import User
from app.transactions.schemas import TransactionResponse, TransactionUpdate
from app.transactions.service import delete_transaction, list_transactions, update_transaction

router = APIRouter(prefix="/transactions", tags=["transactions"])


def _to_response(transaction) -> TransactionResponse:
    return TransactionResponse(
        id=transaction.id,
        transaction_date=transaction.transaction_date.isoformat(),
        raw_description=transaction.raw_description,
        merchant_name=transaction.merchant_name,
        display_name=transaction.display_name,
        amount=float(transaction.amount),
        transaction_type=transaction.transaction_type,
        payment_method=transaction.payment_method,
        source_type=transaction.source_type,
        category=transaction.category.name if transaction.category else None,
        is_unusual=transaction.is_unusual,
        is_duplicate=transaction.is_duplicate,
        duplicate_of_transaction_id=transaction.duplicate_of_transaction_id,
    )


@router.get("", response_model=list[TransactionResponse])
def list_route(
    month: str | None = None,
    category_id: str | None = None,
    source_type: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return [_to_response(tx) for tx in list_transactions(db, current_user.id, month, category_id, source_type, search)]


@router.patch("/{transaction_id}", response_model=TransactionResponse)
def patch_route(
    transaction_id: str,
    payload: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _to_response(update_transaction(db, current_user.id, transaction_id, payload))


@router.delete("/{transaction_id}")
def delete_route(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_transaction(db, current_user.id, transaction_id)
    return {"message": "Transaction deleted"}

