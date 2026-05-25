SOURCE_PRIORITY = {
    "user_edit": 100,
    "google_pay": 80,
    "phonepe": 80,
    "paytm": 75,
    "amazon_pay": 70,
    "onecard": 65,
    "credit_card": 60,
    "bank_statement": 40,
    "generic_csv": 30,
    "other": 20,
}


def source_score(source_type: str) -> int:
    return SOURCE_PRIORITY.get(source_type, 20)

