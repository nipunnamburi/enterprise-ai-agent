from pydantic import BaseModel, ConfigDict
from typing import Dict, Any, Optional
from datetime import datetime

class ToolParamInfo(BaseModel):
    type: str
    description: str
    required: bool = True
    default: Optional[Any] = None

class ToolInfo(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]
    category: str

class ToolExecutionLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    task_id: Optional[str] = None
    tool_name: str
    arguments: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    status: str
    duration_ms: float
    created_at: datetime
