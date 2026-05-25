from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.imports.schemas import ConfirmImportResponse, UploadPreviewResponse, UploadResponse
from app.imports.service import available_sources, confirm_upload, create_upload_preview, list_uploads, upload_preview_response
from app.models import User

router = APIRouter(prefix="/import", tags=["import"])


@router.get("/sources")
def sources_route() -> list[dict[str, str]]:
    return available_sources()


@router.post("/upload", response_model=UploadPreviewResponse)
async def upload_route(
    source_type: str = Form(...),
    pdf_password: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    upload = await create_upload_preview(db, current_user.id, source_type, file, pdf_password)
    return upload_preview_response(upload)


@router.post("/uploads/{upload_id}/confirm", response_model=ConfirmImportResponse)
def confirm_route(
    upload_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ConfirmImportResponse:
    upload = confirm_upload(db, current_user.id, upload_id)
    return ConfirmImportResponse(
        upload_id=upload.id,
        imported_rows=upload.imported_rows,
        duplicate_rows=upload.duplicate_rows,
        failed_rows=upload.failed_rows,
        status=upload.status,
    )


@router.get("/uploads", response_model=list[UploadResponse])
def uploads_route(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return [
        UploadResponse(
            id=upload.id,
            source_type=upload.source_type,
            file_name=upload.file_name,
            status=upload.status,
            total_rows=upload.total_rows,
            imported_rows=upload.imported_rows,
            duplicate_rows=upload.duplicate_rows,
            failed_rows=upload.failed_rows,
            error_message=upload.error_message,
            created_at=upload.created_at.isoformat(),
        )
        for upload in list_uploads(db, current_user.id)
    ]
