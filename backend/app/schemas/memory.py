from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class MemoryCreate(BaseModel):
    category: str = "preference"  # preference, fact, task_context, entity
    content: str
    importance: float = 1.0
    confidence: float = 1.0

class MemoryUpdate(BaseModel):
    category: Optional[str] = None
    content: Optional[str] = None
    importance: Optional[float] = None

class MemoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    category: str
    content: str
    importance: float
    confidence: float
    source_task_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
