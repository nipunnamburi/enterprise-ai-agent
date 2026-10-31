from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.memory import Memory
from app.schemas.memory import MemoryCreate, MemoryOut, MemoryUpdate

from app.models.user import User
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/memory", tags=["Agent Memory"])

@router.get("", response_model=List[MemoryOut])
def get_memories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Memory)
        .filter(Memory.user_id == current_user.id)
        .order_by(Memory.importance.desc(), Memory.created_at.desc())
        .all()
    )

@router.post("", response_model=MemoryOut)
def create_memory(
    mem_in: MemoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    mem = Memory(
        user_id=current_user.id,
        category=mem_in.category,
        content=mem_in.content,
        importance=mem_in.importance,
        confidence=mem_in.confidence
    )
    db.add(mem)
    db.commit()
    db.refresh(mem)
    return mem

@router.delete("/{memory_id}")
def delete_memory(
    memory_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    mem = db.query(Memory).filter(Memory.id == memory_id, Memory.user_id == current_user.id).first()
    if not mem:
        raise HTTPException(status_code=404, detail="Memory not found")
    db.delete(mem)
    db.commit()
    return {"success": True, "message": "Memory deleted successfully"}
