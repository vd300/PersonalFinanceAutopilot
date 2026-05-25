import json
from decimal import Decimal

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.categorization.service import categorize
from app.deduplication.fingerprint import build_fingerprint
from app.deduplication.service import find_duplicate
from app.enrichment.source_priority import source_score
from app.insights.orchestrator import refresh_insights
from app.models import Transaction, TransactionMergeLink, TransactionSource, Upload
from app.parsers.base import ParsedTransaction
from app.parsers.generic_pdf import GenericPdfParser
from app.parsers.registry import get_parser
from app.shared.enums import SourceType, TransactionType, UploadStatus


SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xlsm", ".xls", ".pdf"}


def available_sources() -> list[dict[str, str]]:
    labels = {
        SourceType.GOOGLE_PAY: "Google Pay",
        SourceType.PHONEPE: "PhonePe",
        SourceType.AMAZON_PAY: "Amazon Pay",
        SourceType.ONECARD: "OneCard",
        SourceType.CREDIT_CARD: "Credit Card Statement",
        SourceType.BANK_STATEMENT: "Bank Statement",
        SourceType.GENERIC_CSV: "Generic CSV / Excel / PDF",
    }
    return [{"value": source.value, "label": label} for source, label in labels.items()]


async def create_upload_preview(
    db: Session,
    user_id: str,
    source_type: str,
    file: UploadFile,
    pdf_password: str | None = None,
) -> Upload:
    if "." not in file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must have an extension")
    extension = "." + file.filename.rsplit(".", 1)[-1].lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF, CSV, and Excel files are supported",
        )

    content = await file.read()
    upload = Upload(
        user_id=user_id,
        source_type=source_type,
        file_name=file.filename,
        file_type=extension,
        status=UploadStatus.PENDING,
    )
    db.add(upload)
    db.flush()

    try:
        parser = GenericPdfParser(source_type) if extension == ".pdf" else get_parser(source_type)
        parse_result = parser.parse(file.filename, content, password=pdf_password)
        upload.total_rows = len(parse_result.transactions) + len(parse_result.failed_rows)
        upload.failed_rows = len(parse_result.failed_rows)
        upload.preview_json = parse_result.model_dump_json()
    except Exception as exc:  # noqa: BLE001
        upload.status = UploadStatus.FAILED
        upload.error_message = str(exc)
    db.commit()
    return upload


def _preview_transactions(upload: Upload) -> list[dict]:
    if not upload.preview_json:
        return []
    data = json.loads(upload.preview_json)
    return data.get("transactions", [])


def upload_preview_response(upload: Upload) -> dict:
    payload = json.loads(upload.preview_json or "{}")
    return {
        "upload_id": upload.id,
        "status": upload.status,
        "total_rows": upload.total_rows,
        "failed_rows": upload.failed_rows,
        "error_message": upload.error_message,
        "warnings": payload.get("warnings", []),
        "transactions": _preview_transactions(upload)[:50],
    }


def _transaction_source(db: Session, user_id: str, source_type: str) -> TransactionSource:
    source = db.scalar(
        select(TransactionSource).where(
            TransactionSource.user_id == user_id,
            TransactionSource.source_type == source_type,
        )
    )
    if source:
        return source
    source = TransactionSource(user_id=user_id, source_type=source_type, display_name=source_type.replace("_", " ").title())
    db.add(source)
    db.flush()
    return source


def _merge_richer_details(existing: Transaction, incoming: Transaction) -> None:
    if source_score(incoming.source_type) < source_score(existing.source_type):
        return
    for field in ["merchant_name", "display_name", "description", "payment_method", "reference_id"]:
        incoming_value = getattr(incoming, field)
        if incoming_value and (not getattr(existing, field) or len(str(incoming_value)) > len(str(getattr(existing, field)))):
            setattr(existing, field, incoming_value)
    existing.confidence_score = max(existing.confidence_score, incoming.confidence_score)


def _model_from_parsed(db: Session, user_id: str, upload: Upload, parsed: ParsedTransaction) -> Transaction:
    merchant = parsed.merchant_name or parsed.display_name or parsed.raw_description
    category = categorize(db, user_id, merchant, parsed.description or parsed.raw_description, parsed.transaction_type)
    transaction_type = parsed.transaction_type
    if category.type == TransactionType.TRANSFER:
        transaction_type = TransactionType.TRANSFER
    fingerprint = build_fingerprint(user_id, parsed.transaction_date, parsed.amount, transaction_type, merchant)
    source = _transaction_source(db, user_id, parsed.source_type)
    return Transaction(
        user_id=user_id,
        upload_id=upload.id,
        transaction_source_id=source.id,
        transaction_date=parsed.transaction_date,
        raw_description=parsed.raw_description,
        description=parsed.description,
        merchant_name=merchant,
        display_name=parsed.display_name or merchant,
        amount=Decimal(parsed.amount),
        transaction_type=transaction_type,
        payment_method=parsed.payment_method,
        source_type=parsed.source_type,
        source_account_label=parsed.source_account_label,
        category_id=category.id,
        balance_after_transaction=parsed.balance_after_transaction,
        reference_id=parsed.reference_id,
        card_last_four=parsed.card_last_four,
        fingerprint=fingerprint,
    )


def confirm_upload(db: Session, user_id: str, upload_id: str) -> Upload:
    upload = db.get(Upload, upload_id)
    if not upload or upload.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload not found")
    if upload.status == UploadStatus.PROCESSED:
        return upload
    if upload.status == UploadStatus.FAILED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=upload.error_message or "Upload failed during parsing",
        )
    if not upload.preview_json:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Upload has no parsed preview")

    imported = 0
    duplicates = 0
    preview_transactions = _preview_transactions(upload)
    if not preview_transactions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Upload has no parsed transactions to import",
        )

    for item in preview_transactions:
        parsed = ParsedTransaction(**item)
        candidate = _model_from_parsed(db, user_id, upload, parsed)
        duplicate, reason, confidence = find_duplicate(db, candidate)
        if duplicate:
            duplicates += 1
            candidate.is_duplicate = True
            candidate.duplicate_of_transaction_id = duplicate.id
            db.add(candidate)
            db.flush()
            _merge_richer_details(duplicate, candidate)
            db.add(
                TransactionMergeLink(
                    user_id=user_id,
                    primary_transaction_id=duplicate.id,
                    duplicate_transaction_id=candidate.id,
                    merge_reason=reason,
                    confidence_score=confidence,
                )
            )
        else:
            imported += 1
            db.add(candidate)

    upload.imported_rows = imported
    upload.duplicate_rows = duplicates
    upload.status = UploadStatus.PROCESSED
    db.flush()
    refresh_insights(db, user_id)
    db.commit()
    return upload


def list_uploads(db: Session, user_id: str) -> list[Upload]:
    return list(db.scalars(select(Upload).where(Upload.user_id == user_id).order_by(Upload.created_at.desc())))
