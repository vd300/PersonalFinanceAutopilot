from app.parsers.generic_csv import GenericCsvParser
from app.shared.enums import PaymentMethod, SourceType


class OneCardParser(GenericCsvParser):
    source_type = SourceType.ONECARD
    default_payment_method = PaymentMethod.CREDIT_CARD

