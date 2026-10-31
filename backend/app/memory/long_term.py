import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.memory import Memory
from app.core.config import settings

class LongTermMemoryManager:
    @staticmethod
    def extract_memories_from_interaction(
        user_message: str,
        assistant_response: str,
        current_task: str
    ) -> List[Dict[str, Any]]:
        """
        Determines whether the interaction contains explicit user preferences,
        facts, or recurring constraints worth persisting to PostgreSQL/SQLite.
        Does NOT persist ordinary conversational chit-chat.
        """
        extracted = []
        msg_lower = user_message.lower()

        # Preference patterns
        pref_patterns = [
            (r"(?:my preferred response style is|prefer my responses in|prefer|i prefer)\s+(.+)", "preference", 1.0),
            (r"(?:always format|format everything as|format as)\s+(.+)", "preference", 0.9),
            (r"(?:i am the|my role is|i work as)\s+(.+)", "fact", 0.9),
            (r"(?:remember that|note that|keep in mind that)\s+(.+)", "fact", 0.8),
            (r"(?:our company|my department|my team)\s+(.+)", "fact", 0.8),
        ]

        for pattern, category, importance in pref_patterns:
            match = re.search(pattern, user_message, re.IGNORECASE)
            if match:
                content = match.group(0).strip()
                extracted.append({
                    "category": category,
                    "content": content,
                    "importance": importance,
                    "confidence": 0.95
                })

        return extracted

    @staticmethod
    def save_memory(
        db: Session,
        user_id: str,
        category: str,
        content: str,
        importance: float = 1.0,
        confidence: float = 1.0,
        source_task_id: Optional[str] = None
    ) -> Memory:
        # Check for near-duplicate memory to avoid redundancy
        existing = db.query(Memory).filter(
            Memory.user_id == user_id,
            Memory.category == category,
            Memory.content.ilike(f"%{content[:40]}%")
        ).first()

        if existing:
            existing.importance = max(existing.importance, importance)
            existing.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(existing)
            return existing

        new_mem = Memory(
            user_id=user_id,
            category=category,
            content=content,
            importance=importance,
            confidence=confidence,
            source_task_id=source_task_id
        )
        db.add(new_mem)
        db.commit()
        db.refresh(new_mem)
        return new_mem

    @staticmethod
    def get_user_memories(db: Session, user_id: str, limit: int = 15) -> List[Memory]:
        return db.query(Memory).filter(
            Memory.user_id == user_id
        ).order_by(Memory.importance.desc(), Memory.created_at.desc()).limit(limit).all()

    @staticmethod
    def delete_memory(db: Session, memory_id: str, user_id: str) -> bool:
        mem = db.query(Memory).filter(
            Memory.id == memory_id,
            Memory.user_id == user_id
        ).first()
        if mem:
            db.delete(mem)
            db.commit()
            return True
        return False

long_term_memory = LongTermMemoryManager()
