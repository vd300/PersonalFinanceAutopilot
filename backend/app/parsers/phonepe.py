from app.parsers.generic_csv import GenericCsvParser
from app.shared.enums import PaymentMethod, SourceType


class PhonePeParser(GenericCsvParser):
    source_type = SourceType.PHONEPE
    default_payment_method = PaymentMethod.UPI

