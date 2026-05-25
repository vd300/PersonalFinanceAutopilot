from fastapi import HTTPException, status

from app.parsers.amazon_pay import AmazonPayParser
from app.parsers.bank_statement import BankStatementParser
from app.parsers.credit_card import CreditCardParser
from app.parsers.generic_csv import GenericCsvParser
from app.parsers.google_pay import GooglePayParser
from app.parsers.onecard import OneCardParser
from app.parsers.phonepe import PhonePeParser
from app.shared.enums import SourceType

PARSER_REGISTRY = {
    SourceType.GENERIC_CSV: GenericCsvParser(),
    SourceType.BANK_STATEMENT: BankStatementParser(),
    SourceType.GOOGLE_PAY: GooglePayParser(),
    SourceType.PHONEPE: PhonePeParser(),
    SourceType.AMAZON_PAY: AmazonPayParser(),
    SourceType.ONECARD: OneCardParser(),
    SourceType.CREDIT_CARD: CreditCardParser(),
}


def get_parser(source_type: str):
    parser = PARSER_REGISTRY.get(source_type)
    if not parser:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No parser for {source_type}")
    return parser

