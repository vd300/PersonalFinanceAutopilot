import re


KNOWN_MERCHANTS = {
    "zomato": "Zomato",
    "swiggy": "Swiggy",
    "starbucks": "Starbucks",
    "amazon": "Amazon",
    "amazon pay": "Amazon Pay",
    "flipkart": "Flipkart",
    "myntra": "Myntra",
    "netflix": "Netflix",
    "spotify": "Spotify",
    "hotstar": "Disney+ Hotstar",
    "uber": "Uber",
    "ola": "Ola",
    "rapido": "Rapido",
    "bigbasket": "BigBasket",
    "blinkit": "Blinkit",
    "zepto": "Zepto",
    "airtel": "Airtel",
    "jio": "Jio",
    "onecard": "OneCard",
}


def clean_merchant(description: str | None) -> str:
    if not description:
        return "Unknown Merchant"
    lowered = description.lower()
    for needle, merchant in KNOWN_MERCHANTS.items():
        if needle in lowered:
            return merchant

    cleaned = re.sub(r"upi|pos|debit|credit|txn|payment|india|pvt|ltd|limited", " ", lowered)
    cleaned = re.sub(r"[^a-z0-9 ]+", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if not cleaned:
        return description[:80].strip() or "Unknown Merchant"
    return " ".join(word.capitalize() for word in cleaned.split()[:4])

