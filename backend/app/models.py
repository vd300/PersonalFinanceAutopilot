import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def new_uuid() -> str:
    return str(uuid.uuid4())


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    preferred_currency: Mapped[str] = mapped_column(String(8), default="INR", nullable=False)
    monthly_income_day: Mapped[int] = mapped_column(default=1, nullable=False)
    savings_goal_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("5000"))
    minimum_buffer_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("5000"))

    transactions: Mapped[list["Transaction"]] = relationship(back_populates="user")


class Category(Base, TimestampMixin):
    __tablename__ = "categories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class TransactionSource(Base, TimestampMixin):
    __tablename__ = "transaction_sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    account_identifier: Mapped[str | None] = mapped_column(String(120), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Upload(Base, TimestampMixin):
    __tablename__ = "uploads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    total_rows: Mapped[int] = mapped_column(default=0, nullable=False)
    imported_rows: Mapped[int] = mapped_column(default=0, nullable=False)
    duplicate_rows: Mapped[int] = mapped_column(default=0, nullable=False)
    failed_rows: Mapped[int] = mapped_column(default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    preview_json: Mapped[str | None] = mapped_column(Text, nullable=True)


class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    upload_id: Mapped[str | None] = mapped_column(ForeignKey("uploads.id"), nullable=True)
    transaction_source_id: Mapped[str | None] = mapped_column(ForeignKey("transaction_sources.id"), nullable=True)
    transaction_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    raw_description: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    merchant_name: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    payment_method: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    source_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    source_account_label: Mapped[str | None] = mapped_column(String(120), nullable=True)
    category_id: Mapped[str | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    balance_after_transaction: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    reference_id: Mapped[str | None] = mapped_column(String(160), index=True, nullable=True)
    card_last_four: Mapped[str | None] = mapped_column(String(4), nullable=True)
    is_recurring_candidate: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_unusual: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_duplicate: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    duplicate_of_transaction_id: Mapped[str | None] = mapped_column(ForeignKey("transactions.id"), nullable=True)
    user_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    fingerprint: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    confidence_score: Mapped[int] = mapped_column(default=80, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user: Mapped[User] = relationship(back_populates="transactions")
    category: Mapped[Category | None] = relationship()


Index("ix_transactions_user_month", Transaction.user_id, Transaction.transaction_date)


class UserCategoryRule(Base, TimestampMixin):
    __tablename__ = "user_category_rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    keyword_or_merchant: Mapped[str] = mapped_column(String(255), nullable=False)
    category_id: Mapped[str] = mapped_column(ForeignKey("categories.id"), nullable=False)
    created_from_transaction_id: Mapped[str | None] = mapped_column(ForeignKey("transactions.id"), nullable=True)


class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    merchant_name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    frequency: Mapped[str] = mapped_column(String(32), default="unknown", nullable=False)
    last_payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    next_expected_payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    category_id: Mapped[str | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="detected", nullable=False)
    confidence_score: Mapped[int] = mapped_column(default=70, nullable=False)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)


class Bill(Base, TimestampMixin):
    __tablename__ = "bills"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    expected_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    due_day: Mapped[int] = mapped_column(nullable=False)
    next_due_date: Mapped[date] = mapped_column(Date, nullable=False)
    frequency: Mapped[str] = mapped_column(String(32), default="monthly", nullable=False)
    category_id: Mapped[str | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    is_auto_detected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)


class Alert(Base, TimestampMixin):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    alert_type: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(32), default="medium", nullable=False)
    related_transaction_id: Mapped[str | None] = mapped_column(ForeignKey("transactions.id"), nullable=True)
    related_subscription_id: Mapped[str | None] = mapped_column(ForeignKey("subscriptions.id"), nullable=True)
    related_bill_id: Mapped[str | None] = mapped_column(ForeignKey("bills.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)


class TransactionMergeLink(Base, TimestampMixin):
    __tablename__ = "transaction_merge_links"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    primary_transaction_id: Mapped[str] = mapped_column(ForeignKey("transactions.id"), nullable=False)
    duplicate_transaction_id: Mapped[str] = mapped_column(ForeignKey("transactions.id"), nullable=False)
    merge_reason: Mapped[str] = mapped_column(String(255), nullable=False)
    confidence_score: Mapped[int] = mapped_column(default=90, nullable=False)

