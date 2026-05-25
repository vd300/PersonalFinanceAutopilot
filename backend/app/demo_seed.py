from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.schemas import SignupRequest
from app.auth.service import signup
from app.categorization.service import categorize, ensure_default_categories
from app.deduplication.fingerprint import build_fingerprint
from app.models import Bill, Transaction, User


DEMO_EMAIL = "demo@example.com"
DEMO_PASSWORD = "demo1234"


def seed_demo_data(db: Session) -> None:
    ensure_default_categories(db)
    user = db.scalar(select(User).where(User.email == DEMO_EMAIL))
    if not user:
        user, _ = signup(
            db,
            SignupRequest(name="Demo User", email=DEMO_EMAIL, password=DEMO_PASSWORD),
        )
    existing = db.scalar(select(Transaction).where(Transaction.user_id == user.id))
    if existing:
        return

    today = date.today()
    first = date(today.year, today.month, 1)
    rows = [
        (first, "ACME Payroll Salary", "ACME Payroll", 120000, "income", "bank_transfer", "bank_statement"),
        (first + timedelta(days=1), "Rent to Landlord", "Landlord", 30000, "expense", "bank_transfer", "bank_statement"),
        (first + timedelta(days=2), "Paid to Swiggy dinner", "Swiggy", 820, "expense", "upi", "google_pay"),
        (first + timedelta(days=3), "Zomato order", "Zomato", 650, "expense", "upi", "phonepe"),
        (first + timedelta(days=4), "Amazon Pay headphones", "Amazon", 4200, "expense", "wallet", "amazon_pay"),
        (first + timedelta(days=4), "UPI/29382/AMAZON PAY", "Amazon Pay", 4200, "expense", "bank_transfer", "bank_statement"),
        (first + timedelta(days=5), "Netflix monthly", "Netflix", 649, "expense", "credit_card", "onecard"),
        (first + timedelta(days=6), "Spotify Premium", "Spotify", 119, "expense", "credit_card", "onecard"),
        (first + timedelta(days=7), "Uber ride", "Uber", 340, "expense", "upi", "google_pay"),
        (first + timedelta(days=8), "Blinkit groceries", "Blinkit", 2300, "expense", "upi", "phonepe"),
        (first + timedelta(days=10), "OneCard payment", "OneCard", 12000, "transfer", "bank_transfer", "bank_statement"),
        (first + timedelta(days=11), "Myntra shopping", "Myntra", 18500, "expense", "credit_card", "onecard"),
        (first + timedelta(days=13), "Airtel broadband", "Airtel", 999, "expense", "upi", "phonepe"),
        (first + timedelta(days=15), "Disney Hotstar subscription", "Disney+ Hotstar", 299, "expense", "credit_card", "onecard"),
    ]
    # Add recurring subscription history across prior months.
    for months_back in [1, 2, 3]:
        base = first - timedelta(days=30 * months_back)
        rows.extend(
            [
                (base + timedelta(days=5), "Netflix monthly", "Netflix", 649, "expense", "credit_card", "onecard"),
                (base + timedelta(days=6), "Spotify Premium", "Spotify", 119, "expense", "credit_card", "onecard"),
                (base + timedelta(days=15), "Disney Hotstar subscription", "Disney+ Hotstar", 299, "expense", "credit_card", "onecard"),
            ]
        )

    seen = set()
    for tx_date, raw, merchant, amount, tx_type, method, source in rows:
        category = categorize(db, user.id, merchant, raw, tx_type)
        fingerprint = build_fingerprint(user.id, tx_date, Decimal(amount), tx_type, merchant)
        is_duplicate = fingerprint in seen
        seen.add(fingerprint)
        transaction = Transaction(
            user_id=user.id,
            transaction_date=tx_date,
            raw_description=raw,
            description=raw,
            merchant_name=merchant,
            display_name=merchant,
            amount=Decimal(amount),
            transaction_type=tx_type,
            payment_method=method,
            source_type=source,
            category_id=category.id,
            balance_after_transaction=Decimal(150000 - amount) if tx_date == first + timedelta(days=1) else None,
            fingerprint=fingerprint,
            is_duplicate=is_duplicate,
        )
        db.add(transaction)

    db.add_all(
        [
            Bill(
                user_id=user.id,
                name="Rent",
                expected_amount=Decimal("30000"),
                due_day=1,
                next_due_date=first + timedelta(days=31),
                frequency="monthly",
                is_auto_detected=False,
            ),
            Bill(
                user_id=user.id,
                name="Airtel broadband",
                expected_amount=Decimal("999"),
                due_day=13,
                next_due_date=first + timedelta(days=43),
                frequency="monthly",
                is_auto_detected=True,
            ),
        ]
    )
    from app.insights.orchestrator import refresh_insights

    refresh_insights(db, user.id)
    db.commit()

