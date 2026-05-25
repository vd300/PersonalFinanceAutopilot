from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class FailedRow(BaseModel):
    row_number: int
    message: str
    raw: dict[str, str] = Field(default_factory=dict)


class ParsedTransaction(BaseModel):
    transaction_date: date
    amount: Decimal
    transaction_type: str
    payment_method: str
    source_type: str
    raw_description: str
    description: str | None = None
    merchant_name: str | None = None
    display_name: str | None = None
    reference_id: str | None = None
    balance_after_transaction: Decimal | None = None
    card_last_four: str | None = None
    source_account_label: str | None = None


class ParseResult(BaseModel):
    transactions: list[ParsedTransaction] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    failed_rows: list[FailedRow] = Field(default_factory=list)


class BaseTransactionParser:
    source_type = "generic_csv"

    def parse(self, filename: str, content: bytes, password: str | None = None) -> ParseResult:
        raise NotImplementedError
