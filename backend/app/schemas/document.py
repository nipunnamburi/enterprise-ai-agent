from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime

class DocumentChunkOut(BaseModel):
    chunk_id: str
    content: str
    page_number: Optional[int] = None
    metadata: Dict[str, Any] = {}

class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    file_type: str
    file_size: int
    chunk_count: int
    status: str
    doc_metadata: Dict[str, Any] = {}
    created_at: datetime

class DocumentUploadResponse(BaseModel):
    document: DocumentOut
    message: str
