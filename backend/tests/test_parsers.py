from app.parsers.google_pay import GooglePayParser
from app.parsers.generic_pdf import ExtractedPdfContent, GenericPdfParser
from app.shared.enums import SourceType


def test_google_pay_parser_normalizes_basic_csv():
    content = b"Date,Description,Amount,Type,Reference\n2026-05-01,Paid to Swiggy,450,expense,abc123\n"
    result = GooglePayParser().parse("sample.csv", content)
    assert not result.failed_rows
    assert result.transactions[0].merchant_name == "Swiggy"
    assert result.transactions[0].payment_method == "upi"


def test_generic_pdf_parser_uses_selected_source_and_text_rows(monkeypatch):
    def fake_extract(content: bytes, password: str | None) -> ExtractedPdfContent:
        return ExtractedPdfContent(
            text="01May,2026 PaidtoSwiggy INR 450\n10:21PM UPITransactionID:abc123\nPaidbyStateBankofIndia1704\n02 May 2026 Salary INR 50000 CR"
        )

    monkeypatch.setattr("app.parsers.generic_pdf._extract_pdf_content", fake_extract)

    result = GenericPdfParser(SourceType.GOOGLE_PAY).parse("statement.pdf", b"%PDF")

    assert not result.failed_rows
    assert len(result.transactions) == 2
    assert result.transactions[0].source_type == SourceType.GOOGLE_PAY
    assert result.transactions[0].payment_method == "upi"
    assert result.transactions[0].merchant_name == "Swiggy"
    assert result.transactions[0].reference_id == "abc123"
    assert result.transactions[1].transaction_type == "income"


def test_generic_pdf_parser_reports_scanned_pdf_when_no_text(monkeypatch):
    def fake_extract(content: bytes, password: str | None) -> ExtractedPdfContent:
        return ExtractedPdfContent()

    monkeypatch.setattr("app.parsers.generic_pdf._extract_pdf_content", fake_extract)

    result = GenericPdfParser(SourceType.BANK_STATEMENT).parse("scanned.pdf", b"%PDF")

    assert not result.transactions
    assert result.warnings
