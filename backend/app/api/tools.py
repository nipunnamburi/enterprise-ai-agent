from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.task import ToolExecution
from app.schemas.tool import ToolInfo, ToolExecutionLogOut
from app.tools.registry import tool_registry

from app.models.user import User
from app.core.dependencies import get_current_user, require_role

router = APIRouter(prefix="/tools", tags=["Tools Registry & Audit"])

@router.get("", response_model=List[ToolInfo])
def list_registered_tools(current_user: User = Depends(get_current_user)):
    return tool_registry.list_tools()

@router.get("/audit", response_model=List[ToolExecutionLogOut])
def list_tool_audit_logs(
    limit: int = 25,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logs = db.query(ToolExecution).order_by(ToolExecution.created_at.desc()).limit(limit).all()
    return logs

@router.post("/execute")
def execute_tool_direct(
    tool_name: str = Body(..., embed=True),
    arguments: Dict[str, Any] = Body(default_factory=dict, embed=True),
    current_user: User = Depends(require_role(["admin", "analyst"])),
):
    result = tool_registry.execute_tool(tool_name, arguments)
    return {
        "tool_name": tool_name,
        "arguments": arguments,
        "result": result
    }
