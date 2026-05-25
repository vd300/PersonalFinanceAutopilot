import io
import re
from dataclasses import dataclass, field
from typing import Any

from app.enrichment.merchant_cleanup import clean_merchant
from app.parsers.base import BaseTransactionParser, FailedRow, ParseResult
from app.parsers.generic_csv import (
    AMOUNT_COLUMNS,
    BALANCE_COLUMNS,
    CREDIT_COLUMNS,
    DATE_COLUMNS,
    DEBIT_COLUMNS,
    DESCRIPTION_COLUMNS,
    MERCHANT_COLUMNS,
    METHOD_COLUMNS,
    REFERENCE_COLUMNS,
    TYPE_COLUMNS,
    GenericCsvParser,
)
from app.shared.enums import PaymentMethod, SourceType


DATE_PATTERN = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}\s*[A-Za-z]{3,9},\d{4}|\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})"
)
AMOUNT_PATTERN = re.compile(
    r"(?:Rs\.?|INR|₹)?\s*(?P<amount>\(?-?\d[\d,]*(?:\.\d{1,2})?\)?)\s*(?P<marker>CR|DR|Debit|Credit)?",
    re.IGNORECASE,
)
REFERENCE_PATTERN = re.compile(
    r"\b(?:UTR|RRN|Ref(?:erence)?|UPI\s*Transaction\s*ID|Txn(?:action)?\s*ID)[:\s-]*(?P<reference>[A-Z0-9-]+)",
    re.IGNORECASE,
)

HEADER_ALIASES = (
    DATE_COLUMNS
    + DESCRIPTION_COLUMNS
    + MERCHANT_COLUMNS
    + AMOUNT_COLUMNS
    + DEBIT_COLUMNS
    + CREDIT_COLUMNS
    + TYPE_COLUMNS
    + REFERENCE_COLUMNS
    + BALANCE_COLUMNS
    + METHOD_COLUMNS
)


@dataclass
class ExtractedPdfContent:
    text: str = ""
    tables: list[list[list[str]]] = field(default_factory=list)


def _source_value(source_type: str) -> str:
    return source_type.value if hasattr(source_type, "value") else str(source_type)


def _default_payment_method(source_type: str) -> PaymentMethod:
    source_value = _source_value(source_type)
    if source_value in {SourceType.GOOGLE_PAY.value, SourceType.PHONEPE.value}:
        return PaymentMethod.UPI
    if source_value in {SourceType.AMAZON_PAY.value, SourceType.PAYTM.value}:
        return PaymentMethod.WALLET
    if source_value in {SourceType.ONECARD.value, SourceType.CREDIT_CARD.value}:
        return PaymentMethod.CREDIT_CARD
    if source_value == SourceType.BANK_STATEMENT.value:
        return PaymentMethod.BANK_TRANSFER
    return PaymentMethod.UNKNOWN


def _cell(value: Any) -> str:
    return " ".join(str(value or "").split())


def _looks_like_header(row: list[str]) -> bool:
    normalized = [cell.lower() for cell in row]
    matched = 0
    for alias in HEADER_ALIASES:
        if any(alias in cell for cell in normalized):
            matched += 1
    return matched >= 2 and any("date" in cell for cell in normalized)


def _rows_from_table(table: list[list[Any]]) -> list[dict[str, str]]:
    cleaned_rows = [[_cell(cell) for cell in row] for row in table if any(_cell(cell) for cell in row)]
    if not cleaned_rows:
        return []

    header_index = next(
        (index for index, row in enumerate(cleaned_rows[:5]) if _looks_like_header(row)),
        None,
    )
    if header_index is None:
        return []

    headers = [
        header if header else f"column_{index + 1}"
        for index, header in enumerate(cleaned_rows[header_index])
    ]
    rows = []
    for row in cleaned_rows[header_index + 1 :]:
        rows.append(
            {
                headers[index] if index < len(headers) else f"column_{index + 1}": value
                for index, value in enumerate(row)
            }
        )
    return rows


def _split_compact_words(value: str) -> str:
    value = re.sub(r"([a-z])([A-Z])", r"\1 \2", value)
    value = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", value)
    return value.strip()


def _google_pay_description(line_tail: str) -> tuple[str, str, str]:
    compact_tail = line_tail.strip()
    for prefix, label, transaction_type in (
        ("Paidto", "Paid to", "expense"),
        ("Receivedfrom", "Received from", "income"),
    ):
        if compact_tail.startswith(prefix):
            merchant_token = compact_tail[len(prefix) :].strip(" -:")
            merchant = _split_compact_words(merchant_token)
            return f"{label} {merchant}".strip(), merchant, transaction_type
    return compact_tail, clean_merchant(compact_tail), "expense"


def _rows_from_text(text: str) -> list[dict[str, str]]:
    rows = []
    lines = [" ".join(line.split()) for line in text.splitlines() if line.strip()]
    for index, line in enumerate(lines):
        if not line or not DATE_PATTERN.search(line):
            continue

        detail_lines = [line]
        for detail_line in lines[index + 1 : index + 5]:
            if DATE_PATTERN.search(detail_line) or detail_line.startswith(("Note:", "Page", "Date&time")):
                break
            detail_lines.append(detail_line)

        chunk = " ".join(detail_lines)
        reference_match = REFERENCE_PATTERN.search(chunk)
        line_without_reference = REFERENCE_PATTERN.sub("", line)
        date_match = DATE_PATTERN.search(line_without_reference)
        if not date_match:
            continue

        tail = line_without_reference[date_match.end() :]
        amount_matches = list(AMOUNT_PATTERN.finditer(tail))
        if not amount_matches:
            continue

        amount_match = amount_matches[-1]
        amount = amount_match.group("amount")
        marker = (amount_match.group("marker") or "").lower()
        transaction_type = "expense"

        lowered = line.lower()
        if marker in {"cr", "credit"} or " received " in f" {lowered} ":
            transaction_type = "income"
        elif "transfer" in lowered:
            transaction_type = "transfer"

        description = f"{tail[: amount_match.start()]} {tail[amount_match.end() :]}".strip()
        description = REFERENCE_PATTERN.sub("", description).strip(" -:")
        description, merchant_hint, inferred_type = _google_pay_description(description)
        merchant = clean_merchant(merchant_hint)

        rows.append(
            {
                "Date": date_match.group("date"),
                "Description": description or merchant,
                "Merchant": merchant,
                "Amount": amount,
                "Type": transaction_type if transaction_type != "expense" else inferred_type,
                "Reference": reference_match.group("reference") if reference_match else "",
            }
        )
    return rows


def _extract_with_pdfplumber(content: bytes, password: str | None) -> ExtractedPdfContent | None:
    try:
        import pdfplumber
    except ImportError:
        return None

    try:
        with pdfplumber.open(io.BytesIO(content), password=password or "") as pdf:
            text_parts = []
            tables = []
            for page in pdf.pages:
                text_parts.append(page.extract_text() or "")
                tables.extend(page.extract_tables() or [])
            return ExtractedPdfContent(text="\n".join(text_parts), tables=tables)
    except Exception as exc:  # noqa: BLE001
        message = str(exc).lower()
        if "password" in message or "decrypt" in message:
            raise ValueError("PDF password is required or incorrect.") from exc
        raise


def _extract_with_pymupdf(content: bytes, password: str | None) -> ExtractedPdfContent | None:
    try:
        import fitz
    except ImportError:
        return None

    try:
        document = fitz.open(stream=content, filetype="pdf")
        if document.needs_pass and not document.authenticate(password or ""):
            raise ValueError("PDF password is required or incorrect.")
        text = "\n".join(page.get_text("text") for page in document)
        return ExtractedPdfContent(text=text)
    except ValueError:
        raise
    except Exception as exc:  # noqa: BLE001
        message = str(exc).lower()
        if "password" in message or "decrypt" in message:
            raise ValueError("PDF password is required or incorrect.") from exc
        raise


def _extract_pdf_content(content: bytes, password: str | None) -> ExtractedPdfContent:
    extracted = _extract_with_pdfplumber(content, password)
    if extracted is not None:
        return extracted

    extracted = _extract_with_pymupdf(content, password)
    if extracted is not None:
        return extracted

    raise RuntimeError("PDF parsing requires pdfplumber or PyMuPDF to be installed.")


class GenericPdfParser(BaseTransactionParser):
    def __init__(self, source_type: str = SourceType.GENERIC_CSV):
        self.source_type = _source_value(source_type)
        self.default_payment_method = _default_payment_method(source_type)

    def parse(self, filename: str, content: bytes, password: str | None = None) -> ParseResult:
        result = ParseResult()
        extracted = _extract_pdf_content(content, password)

        rows = []
        for table in extracted.tables:
            rows.extend(_rows_from_table(table))
        if not rows:
            rows = _rows_from_text(extracted.text)

        if not rows:
            result.warnings.append(
                "No selectable transaction text was found. This may be a scanned or image-based PDF; OCR support is not enabled for MVP."
            )
            return result

        csv_parser = GenericCsvParser()
        csv_parser.source_type = self.source_type
        csv_parser.default_payment_method = self.default_payment_method

        for index, row in enumerate(rows, start=1):
            try:
                result.transactions.append(csv_parser._parse_row(row))
            except Exception as exc:  # noqa: BLE001
                result.failed_rows.append(FailedRow(row_number=index, message=str(exc), raw=row))

        if extracted.text and not extracted.tables:
            result.warnings.append("PDF text extraction was used; please review the preview before confirming.")
        return result
