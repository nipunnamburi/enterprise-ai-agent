import uuid
import time
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.models.task import Task, TaskStep, ToolExecution
from app.models.memory import Memory
from app.schemas.agent import AgentChatRequest, AgentChatResponse, ExecutionStepInfo, AgentPlan
from app.agents.graph import agent_graph
from app.agents.context_manager import context_manager

router = APIRouter(prefix="/agent", tags=["Agent Workflows"])

@router.post("/chat", response_model=AgentChatResponse)
def execute_agent_chat(request: AgentChatRequest, db: Session = Depends(get_db)):
    start_time = time.time()
    user_id = request.user_id or "demo-user-123"

    # Ensure user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = db.query(User).first()
        if user:
            user_id = user.id
        else:
            user = User(id=user_id, email="analyst@enterprise.ai", hashed_password="pwd", full_name="AI Analyst")
            db.add(user)
            db.commit()

    # Get or create conversation
    conv_id = request.conversation_id
    if not conv_id:
        conv = Conversation(user_id=user_id, title=request.message[:40] + ("..." if len(request.message) > 40 else ""))
        db.add(conv)
        db.commit()
        db.refresh(conv)
        conv_id = conv.id
    else:
        conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
        if not conv:
            conv = Conversation(id=conv_id, user_id=user_id, title=request.message[:40])
            db.add(conv)
            db.commit()

    # Save user message
    user_msg = Message(
        conversation_id=conv_id,
        role="user",
        content=request.message
    )
    db.add(user_msg)
    db.commit()

    # Fetch conversation history & memories
    past_messages = db.query(Message).filter(Message.conversation_id == conv_id).order_by(Message.created_at).all()
    history_dicts = [{"role": m.role, "content": m.content} for m in past_messages]

    user_memories_rows = db.query(Memory).filter(Memory.user_id == user_id).all()
    user_memories_list = [m.content for m in user_memories_rows]

    # Summarize older messages if history is long
    compressed_summary = None
    if len(past_messages) > 6:
        compressed_summary = context_manager.summarize_conversation(history_dicts)

    # Initialize Task Record
    task_id = f"task-{uuid.uuid4().hex[:8]}"
    task_record = Task(
        id=task_id,
        conversation_id=conv_id,
        user_id=user_id,
        objective=request.message,
        status="running",
        model_used="gpt-4o"
    )
    db.add(task_record)
    db.commit()

    # Initial LangGraph State
    initial_state = {
        "user_id": user_id,
        "conversation_id": conv_id,
        "task_id": task_id,
        "messages": history_dicts,
        "current_task": request.message,
        "user_memories": user_memories_list,
        "compressed_history_summary": compressed_summary,
        "plan": None,
        "execution_trace": [],
        "retrieved_documents": [],
        "pending_tool_calls": [],
        "tool_results": [],
        "tools_used": [],
        "evaluation": None,
        "final_answer": None,
        "sources": [],
        "confidence": "high",
        "key_findings": [],
        "iterations": 0,
        "max_iterations": 5,
        "is_complete": False,
        "error": None
    }

    # Execute LangGraph workflow
    try:
        final_state = agent_graph.invoke(initial_state)
    except Exception as e:
        print(f"[AgentAPI] LangGraph execution error: {e}")
        task_record.status = "failed"
        task_record.error = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Agent workflow error: {str(e)}")

    total_duration_ms = round((time.time() - start_time) * 1000, 2)
    final_answer = final_state.get("final_answer") or "Agent processing finished."
    sources = final_state.get("sources", [])
    tools_used = final_state.get("tools_used", [])
    execution_trace = final_state.get("execution_trace", [])
    plan_dict = final_state.get("plan")

    # Update Task Record
    task_record.status = "completed"
    task_record.duration_ms = total_duration_ms
    task_record.plan = plan_dict
    db.commit()

    # Persist Task Steps & Tool Executions
    for step in execution_trace:
        step_rec = TaskStep(
            task_id=task_id,
            step_name=step.get("step_name", "step"),
            status=step.get("status", "completed"),
            duration_ms=step.get("duration_ms", 0.0),
            input_data=step.get("details"),
            output_data={"description": step.get("description")}
        )
        db.add(step_rec)

    for tr in final_state.get("tool_results", []):
        t_exec = ToolExecution(
            task_id=task_id,
            tool_name=tr.get("tool_name", "unknown"),
            arguments=tr.get("arguments", {}),
            result=tr.get("result", {}),
            duration_ms=tr.get("duration_ms", 0.0),
            status="success" if tr.get("result", {}).get("success", True) else "error"
        )
        db.add(t_exec)

    # Save Assistant Message
    assistant_msg = Message(
        conversation_id=conv_id,
        role="assistant",
        content=final_answer,
        sources=sources,
        tools_used=tools_used,
        execution_steps=execution_trace,
        confidence=final_state.get("confidence", "high")
    )
    db.add(assistant_msg)
    db.commit()

    # Build response payload
    step_infos = [
        ExecutionStepInfo(
            step_name=s.get("step_name", "step"),
            status=s.get("status", "completed"),
            duration_ms=s.get("duration_ms", 0.0),
            description=s.get("description", ""),
            details=s.get("details")
        ) for s in execution_trace
    ]

    plan_obj = AgentPlan(**plan_dict) if plan_dict else None

    return AgentChatResponse(
        task_id=task_id,
        conversation_id=conv_id,
        answer=final_answer,
        sources=sources,
        tools_used=tools_used,
        confidence=final_state.get("confidence", "high"),
        execution_steps=step_infos,
        plan=plan_obj,
        duration_ms=total_duration_ms
    )

@router.get("/tasks/{task_id}")
def get_task_details(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    steps = db.query(TaskStep).filter(TaskStep.task_id == task_id).order_by(TaskStep.created_at).all()
    tool_execs = db.query(ToolExecution).filter(ToolExecution.task_id == task_id).all()

    return {
        "id": task.id,
        "conversation_id": task.conversation_id,
        "objective": task.objective,
        "plan": task.plan,
        "status": task.status,
        "duration_ms": task.duration_ms,
        "model_used": task.model_used,
        "steps": [{
            "id": s.id,
            "step_name": s.step_name,
            "status": s.status,
            "duration_ms": s.duration_ms,
            "details": s.input_data,
            "description": s.output_data.get("description") if s.output_data else None
        } for s in steps],
        "tool_executions": [{
            "tool_name": t.tool_name,
            "arguments": t.arguments,
            "result": t.result,
            "duration_ms": t.duration_ms,
            "status": t.status
        } for t in tool_execs],
        "created_at": task.created_at
    }

@router.get("/tasks/{task_id}/steps")
def get_task_steps(task_id: str, db: Session = Depends(get_db)):
    steps = db.query(TaskStep).filter(TaskStep.task_id == task_id).order_by(TaskStep.created_at).all()
    return [{
        "id": s.id,
        "step_name": s.step_name,
        "status": s.status,
        "duration_ms": s.duration_ms,
        "details": s.input_data,
        "created_at": s.created_at
    } for s in steps]
