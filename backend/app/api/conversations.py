from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.conversation import Conversation, Message

router = APIRouter(prefix="/conversations", tags=["Conversations"])

@router.get("")
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    convs = (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )
    result = []
    for c in convs:
        last_msg = db.query(Message).filter(Message.conversation_id == c.id).order_by(Message.created_at.desc()).first()
        msg_count = db.query(Message).filter(Message.conversation_id == c.id).count()
        result.append({
            "id": c.id,
            "title": c.title,
            "summary": c.summary,
            "message_count": msg_count,
            "last_message": last_msg.content[:80] if last_msg else None,
            "updated_at": c.updated_at,
            "created_at": c.created_at
        })
    return result

@router.get("/{conversation_id}")
def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
        .first()
    )
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    
    messages = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at).all()
    return {
        "id": conv.id,
        "title": conv.title,
        "summary": conv.summary,
        "messages": [{
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "sources": m.sources or [],
            "tools_used": m.tools_used or [],
            "execution_steps": m.execution_steps or [],
            "confidence": m.confidence,
            "created_at": m.created_at
        } for m in messages]
    }

@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
        .first()
    )
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    db.delete(conv)
    db.commit()
    return {"success": True, "message": "Conversation deleted"}
