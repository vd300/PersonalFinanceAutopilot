from pydantic import BaseModel


class TransactionResponse(BaseModel):
    id: str
    transaction_date: str
    raw_description: str
    merchant_name: str | None
    display_name: str | None
    amount: float
    transaction_type: str
    payment_method: str
    source_type: str
    category: str | None
    is_unusual: bool
    is_duplicate: bool
    duplicate_of_transaction_id: str | None


class TransactionUpdate(BaseModel):
    merchant_name: str | None = None
    display_name: str | None = None
    category_id: str | None = None
    transaction_type: str | None = None
    payment_method: str | None = None
    user_notes: str | None = None

