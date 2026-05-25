from app.parsers.generic_csv import GenericCsvParser
from app.shared.enums import PaymentMethod, SourceType


class AmazonPayParser(GenericCsvParser):
    source_type = SourceType.AMAZON_PAY
    default_payment_method = PaymentMethod.WALLET

