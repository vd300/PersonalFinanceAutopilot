import hashlib
import re
from datetime import date
from decimal import Decimal


def normalize_for_fingerprint(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", value.lower())).strip()


def build_fingerprint(
    user_id: str,
    transaction_date: date,
    amount: Decimal,
    transaction_type: str,
    merchant_or_description: str | None,
) -> str:
    material = "|".join(
        [
            user_id,
            transaction_date.isoformat(),
            f"{Decimal(amount):.2f}",
            transaction_type,
            normalize_for_fingerprint(merchant_or_description),
        ]
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()

