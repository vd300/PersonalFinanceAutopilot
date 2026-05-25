from app.parsers.generic_csv import GenericCsvParser
from app.shared.enums import PaymentMethod, SourceType


class GooglePayParser(GenericCsvParser):
    source_type = SourceType.GOOGLE_PAY
    default_payment_method = PaymentMethod.UPI

