from sqlalchemy import select
from sqlalchemy.orm import Session

from app.categorization.rules import CATEGORY_KEYWORDS, DEFAULT_CATEGORIES, TRANSFER_KEYWORDS
from app.models import Category, UserCategoryRule
from app.shared.enums import TransactionType


def ensure_default_categories(db: Session, user_id: str | None = None) -> None:
    for name, category_type in DEFAULT_CATEGORIES:
        exists = db.scalar(
            select(Category).where(Category.name == name, Category.user_id.is_(None), Category.is_default.is_(True))
        )
        if not exists:
            db.add(Category(name=name, type=category_type, is_default=True))
    db.flush()


def get_category_by_name(db: Session, name: str, user_id: str | None = None) -> Category:
    category = db.scalar(
        select(Category)
        .where(Category.name == name)
        .where((Category.user_id == user_id) | (Category.user_id.is_(None)))
        .order_by(Category.user_id.desc().nullslast())
    )
    if category:
        return category
    fallback_type = "income" if name == "Salary / Income" else "expense"
    category = Category(user_id=user_id, name=name, type=fallback_type, is_default=False)
    db.add(category)
    db.flush()
    return category


def detect_transfer(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in TRANSFER_KEYWORDS)


def categorize(
    db: Session,
    user_id: str,
    merchant_name: str | None,
    description: str | None,
    transaction_type: str,
) -> Category:
    text = f"{merchant_name or ''} {description or ''}".lower()
    rule = db.scalar(select(UserCategoryRule).where(UserCategoryRule.user_id == user_id))
    if rule and rule.keyword_or_merchant.lower() in text:
        category = db.get(Category, rule.category_id)
        if category:
            return category

    if transaction_type == TransactionType.INCOME:
        return get_category_by_name(db, "Salary / Income", user_id)
    if detect_transfer(text):
        return get_category_by_name(db, "Transfers", user_id)

    for category_name, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return get_category_by_name(db, category_name, user_id)
    return get_category_by_name(db, "Other", user_id)


def save_user_category_rule(
    db: Session, user_id: str, keyword_or_merchant: str, category_id: str, transaction_id: str | None = None
) -> None:
    keyword = keyword_or_merchant.strip()
    if not keyword:
        return
    existing = db.scalar(
        select(UserCategoryRule).where(
            UserCategoryRule.user_id == user_id,
            UserCategoryRule.keyword_or_merchant == keyword,
        )
    )
    if existing:
        existing.category_id = category_id
    else:
        db.add(
            UserCategoryRule(
                user_id=user_id,
                keyword_or_merchant=keyword,
                category_id=category_id,
                created_from_transaction_id=transaction_id,
            )
        )

