from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class AgentPlan(BaseModel):
    objective: str = Field(description="The primary objective parsed from the user request")
    steps: List[str] = Field(description="Sequential list of planned execution steps")
    required_tools: List[str] = Field(description="List of tool names required to complete the objective")
    reasoning: str = Field(description="Why this plan and these tools were selected")

class ToolDecision(BaseModel):
    tool_name: str = Field(description="The exact name of the tool to invoke")
    arguments: Dict[str, Any] = Field(description="Key-value arguments conforming to the tool's schema")
    reason: str = Field(description="Why this tool invocation is necessary at this step")

class EvaluationResult(BaseModel):
    is_complete: bool = Field(description="Whether sufficient evidence and results have been gathered to fulfill the objective")
    summary_of_findings: str = Field(description="Summary of facts and calculations collected so far")
    next_action: Optional[str] = Field(default=None, description="Next step or tool if incomplete")
    confidence: str = Field(default="high", description="Confidence level: high, medium, low")
    missing_information: Optional[str] = Field(default=None, description="Any missing data points needed")

class AgentResponse(BaseModel):
    answer: str = Field(description="The final authoritative response to the user, incorporating citations and calculations")
    sources: List[str] = Field(default_factory=list, description="Explicit document citations, e.g. [Source: filename.pdf, page X]")
    tools_used: List[str] = Field(default_factory=list, description="Names of tools executed during this task")
    confidence: str = Field(default="high", description="Overall confidence level of the answer")
    key_findings: List[str] = Field(default_factory=list, description="Bullet points of key findings")

class ExecutionStepInfo(BaseModel):
    step_name: str
    status: str
    duration_ms: float
    description: str
    details: Optional[Dict[str, Any]] = None

class AgentChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    user_id: Optional[str] = "demo-user-123"

class AgentChatResponse(BaseModel):
    task_id: str
    conversation_id: str
    answer: str
    sources: List[str]
    tools_used: List[str]
    confidence: str
    execution_steps: List[ExecutionStepInfo]
    plan: Optional[AgentPlan] = None
    duration_ms: float

class AgentJobSubmitRequest(BaseModel):
    objective: str = Field(description="The autonomous research or execution objective")
    conversation_id: Optional[str] = None
    depth: int = Field(default=2, description="Research or search depth (1-3)")
    priority: str = Field(default="normal", description="Priority level: low, normal, high")

class AgentJobResponse(BaseModel):
    job_id: str
    objective: str
    status: str
    created_at: str
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    logs: List[str] = Field(default_factory=list)
