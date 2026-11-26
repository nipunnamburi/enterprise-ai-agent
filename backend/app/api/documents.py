import os
import re
import uuid
import shutil
from typing import List
from arq import create_pool
from arq.connections import RedisSettings
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.core.rate_limit import rate_limit_dependency
from app.models.document import Document
from app.models.user import User
from app.core.dependencies import get_current_user, require_role
from app.schemas.document import DocumentOut, DocumentUploadResponse, DocumentStatusResponse
from app.rag.document_loader import DocumentLoader

router = APIRouter(prefix="/documents", tags=["Documents & RAG"])

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".csv", ".docx", ".json", ".md"}
MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB limit


def sanitize_filename(raw_name: str) -> str:
    """Sanitize filename to prevent directory traversal and filesystem attacks."""
    base = os.path.basename(raw_name.strip())
    cleaned = re.sub(r"[^\w\.\-]", "_", base)
    return cleaned or "document.txt"


@router.get("", response_model=List[DocumentOut])
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tenant_id = getattr(current_user, "tenant_id", "default") or "default"
    return (
        db.query(Document)
        .filter(Document.tenant_id == tenant_id)
        .order_by(Document.created_at.desc())
        .all()
    )


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(rate_limit_dependency)],
)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"])),
):
    safe_name = sanitize_filename(file.filename or "uploaded_file")
    ext = os.path.splitext(safe_name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension '{ext}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}",
        )

    tenant_id = getattr(current_user, "tenant_id", "default") or "default"
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, safe_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE // (1024 * 1024)} MB",
        )

    checksum = DocumentLoader.calculate_checksum(file_path)

    doc_entry = (
        db.query(Document)
        .filter(Document.filename == safe_name, Document.tenant_id == tenant_id)
        .first()
    )
    if not doc_entry:
        doc_entry = Document(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            filename=safe_name,
            file_type=ext.lstrip(".") or "txt",
            file_size=file_size,
            chunk_count=0,
            checksum=checksum,
            status="PENDING",
        )
        db.add(doc_entry)
    else:
        doc_entry.file_size = file_size
        doc_entry.checksum = checksum
        doc_entry.status = "PENDING"
        doc_entry.error_message = None

    db.commit()
    db.refresh(doc_entry)

    job_id = None
    try:
        pool = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))
        job = await pool.enqueue_job(
            "ingest_document",
            str(doc_entry.id),
            tenant_id,
            file_path,
        )
        job_id = job.job_id if job else None
        await pool.close()
    except Exception as exc:
        doc_entry.status = "FAILED"
        doc_entry.error_message = f"Failed to enqueue ingestion job: {exc}"
        db.commit()
        raise HTTPException(status_code=503, detail=doc_entry.error_message)

    return DocumentUploadResponse(
        document_id=str(doc_entry.id),
        job_id=job_id,
        status=doc_entry.status,
        document=doc_entry,
        message="Document accepted and queued for asynchronous Docling ingestion.",
    )


@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
def get_document_status(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tenant_id = getattr(current_user, "tenant_id", "default") or "default"
    doc = (
        db.query(Document)
        .filter(Document.id == document_id, Document.tenant_id == tenant_id)
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentStatusResponse(
        document_id=str(doc.id),
        status=doc.status,
        chunk_count=doc.chunk_count,
        error_message=doc.error_message,
    )


@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"])),
):
    tenant_id = getattr(current_user, "tenant_id", "default") or "default"
    doc = (
        db.query(Document)
        .filter(Document.id == document_id, Document.tenant_id == tenant_id)
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    file_path = os.path.join(settings.UPLOAD_DIR, doc.filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass

    db.delete(doc)
    db.commit()
    return {"success": True, "message": f"Document {doc.filename} deleted from PostgreSQL and pgvector."}


@router.post("/reindex", dependencies=[Depends(rate_limit_dependency)])
async def reindex_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"])),
):
    tenant_id = getattr(current_user, "tenant_id", "default") or "default"
    docs = db.query(Document).filter(Document.tenant_id == tenant_id).all()
    queued_count = 0

    pool = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))
    try:
        for doc in docs:
            file_path = os.path.join(settings.UPLOAD_DIR, doc.filename)
            if os.path.exists(file_path):
                doc.status = "PENDING"
                doc.error_message = None
                await pool.enqueue_job(
                    "ingest_document",
                    str(doc.id),
                    tenant_id,
                    file_path,
                )
                queued_count += 1
        db.commit()
    finally:
        await pool.close()

    return {
        "success": True,
        "queued_documents": queued_count,
    }
