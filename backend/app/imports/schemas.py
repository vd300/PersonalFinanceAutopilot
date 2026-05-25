from pydantic import BaseModel


class ImportPreviewTransaction(BaseModel):
    transaction_date: str
    amount: float
    transaction_type: str
    payment_method: str
    source_type: str
    merchant_name: str | None
    raw_description: str
    reference_id: str | None


class UploadPreviewResponse(BaseModel):
    upload_id: str
    status: str
    total_rows: int
    failed_rows: int
    error_message: str | None = None
    warnings: list[str]
    transactions: list[ImportPreviewTransaction]


class ConfirmImportResponse(BaseModel):
    upload_id: str
    imported_rows: int
    duplicate_rows: int
    failed_rows: int
    status: str


class UploadResponse(BaseModel):
    id: str
    source_type: str
    file_name: str
    status: str
    total_rows: int
    imported_rows: int
    duplicate_rows: int
    failed_rows: int
    error_message: str | None
    created_at: str
