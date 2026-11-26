from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime


class DocumentChunkOut(BaseModel):
    chunk_id: str
    content: str
    page_number: Optional[int] = None
    metadata: Dict[str, Any] = {}


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str = "default"
    filename: str
    file_type: str
    file_size: int
    chunk_count: int
    status: str
    error_message: Optional[str] = None
    doc_metadata: Dict[str, Any] = {}
    created_at: datetime


class DocumentUploadResponse(BaseModel):
    document_id: str
    job_id: Optional[str] = None
    status: str
    document: DocumentOut
    message: str


class DocumentStatusResponse(BaseModel):
    document_id: str
    status: str
    chunk_count: int
    error_message: Optional[str] = None
