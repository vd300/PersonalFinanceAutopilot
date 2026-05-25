from enum import StrEnum


class TransactionType(StrEnum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class PaymentMethod(StrEnum):
    UPI = "upi"
    WALLET = "wallet"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    CASH = "cash"
    UNKNOWN = "unknown"


class SourceType(StrEnum):
    GOOGLE_PAY = "google_pay"
    PHONEPE = "phonepe"
    AMAZON_PAY = "amazon_pay"
    PAYTM = "paytm"
    ONECARD = "onecard"
    CREDIT_CARD = "credit_card"
    BANK_STATEMENT = "bank_statement"
    GENERIC_CSV = "generic_csv"
    MANUAL = "manual"
    OTHER = "other"


class UploadStatus(StrEnum):
    PENDING = "pending"
    PROCESSED = "processed"
    FAILED = "failed"


class Frequency(StrEnum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    UNKNOWN = "unknown"


class AlertType(StrEnum):
    OVERSPENDING = "overspending"
    UNUSUAL_TRANSACTION = "unusual_transaction"
    UPCOMING_BILL = "upcoming_bill"
    LOW_SAFE_TO_SPEND = "low_safe_to_spend"
    SUBSCRIPTION_DETECTED = "subscription_detected"
    CREDIT_CARD_DUE = "credit_card_due"

