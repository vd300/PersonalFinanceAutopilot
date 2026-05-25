from app.parsers.generic_csv import GenericCsvParser
from app.shared.enums import PaymentMethod, SourceType


class BankStatementParser(GenericCsvParser):
    source_type = SourceType.BANK_STATEMENT
    default_payment_method = PaymentMethod.BANK_TRANSFER

