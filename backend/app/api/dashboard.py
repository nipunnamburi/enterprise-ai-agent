from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.document import Document
from app.models.conversation import Conversation
from app.models.task import Task, TaskStep, ToolExecution
from app.models.memory import Memory
from app.rag.vector_store import vector_store

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    doc_count = db.query(Document).count()
    chroma_stats = vector_store.get_stats()
    conv_count = db.query(Conversation).count()
    task_count = db.query(Task).count()
    tool_call_count = db.query(ToolExecution).count()
    memory_count = db.query(Memory).count()
    
    # Calculate average task latency
    tasks = db.query(Task).filter(Task.status == "completed").all()
    avg_latency = 0.0
    if tasks:
        avg_latency = round(sum(t.duration_ms for t in tasks) / len(tasks) / 1000.0, 2)

    # Fetch recent activity
    recent_tasks = db.query(Task).order_by(Task.created_at.desc()).limit(5).all()
    recent_activity = [{
        "id": t.id,
        "objective": t.objective,
        "status": t.status,
        "duration_s": round(t.duration_ms / 1000.0, 2),
        "created_at": t.created_at
    } for t in recent_tasks]

    return {
        "total_documents": doc_count,
        "indexed_chunks": chroma_stats.get("total_chunks", 0),
        "total_conversations": conv_count,
        "total_tasks": task_count,
        "total_tool_calls": tool_call_count,
        "total_memories": memory_count,
        "avg_latency_seconds": avg_latency,
        "system_status": "Healthy",
        "recent_activity": recent_activity
    }
