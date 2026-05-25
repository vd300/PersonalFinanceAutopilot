from app.parsers.generic_csv import GenericCsvParser
from app.shared.enums import PaymentMethod, SourceType


class CreditCardParser(GenericCsvParser):
    source_type = SourceType.CREDIT_CARD
    default_payment_method = PaymentMethod.CREDIT_CARD

