from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    # Identifiers
    user_id: str
    conversation_id: str
    task_id: str
    
    # Input & conversation context
    messages: List[Dict[str, Any]]
    current_task: str
    user_memories: List[str]
    compressed_history_summary: Optional[str]
    
    # Multi-step planning
    plan: Optional[Dict[str, Any]]
    execution_trace: List[Dict[str, Any]]
    
    # Tool and knowledge state
    retrieved_documents: List[Dict[str, Any]]
    pending_tool_calls: List[Dict[str, Any]]
    tool_results: List[Dict[str, Any]]
    tools_used: List[str]
    
    # Evaluation and final output
    evaluation: Optional[Dict[str, Any]]
    final_answer: Optional[str]
    sources: List[str]
    confidence: str
    key_findings: List[str]
    
    # Graph control
    iterations: int
    max_iterations: int
    is_complete: bool
    error: Optional[str]
