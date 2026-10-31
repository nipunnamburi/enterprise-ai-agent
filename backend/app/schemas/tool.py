from pydantic import BaseModel, ConfigDict, Field
from typing import Dict, Any, Optional, List, Type
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


# ---------------------------------------------------------------------------
# Strongly Typed Tool Argument Schemas with Validation
# ---------------------------------------------------------------------------

class CalculatorArgs(BaseModel):
    expression: str = Field(..., description="Mathematical or financial expression to evaluate (e.g. '2499.00 * (1 - 0.15)')")
    operation_type: str = Field(default="custom_expression", description="Operation classification tag")

class CustomerOrderLookupArgs(BaseModel):
    order_number: str = Field(..., description="Order identifier or number (e.g. '1024', '1025')")

class QueryDatabaseArgs(BaseModel):
    entity: str = Field(..., description="Database entity or table to query ('customers', 'orders', 'sales')")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Key-value query filter criteria")
    aggregation: Optional[str] = Field(default=None, description="Optional aggregation function (e.g. 'sum_revenue')")
    limit: Optional[int] = Field(default=10, description="Maximum number of records to return")

class WebSearchArgs(BaseModel):
    query: str = Field(..., description="Search query string")
    num_results: int = Field(default=3, ge=1, le=10, description="Number of results to retrieve")

class GenerateReportArgs(BaseModel):
    title: str = Field(..., description="Executive report title")
    summary: str = Field(..., description="Summary of investigation and evidence findings")
    recommendation: Optional[str] = Field(default=None, description="Recommended business decision or next step")

class SearchDocumentsArgs(BaseModel):
    query: str = Field(..., description="Natural language search query for document vector retrieval")
    top_k: int = Field(default=3, ge=1, le=10, description="Number of document chunks to retrieve")

class DeepResearchArgs(BaseModel):
    topic: str = Field(..., description="The central enterprise research subject or complex query")
    depth: int = Field(default=2, ge=1, le=3, description="Recursive traversal depth (1 to 3)")
    focus_areas: Optional[List[str]] = Field(default=None, description="Optional domain focus areas")

TOOL_ARGUMENT_SCHEMAS: Dict[str, Type[BaseModel]] = {
    "calculator": CalculatorArgs,
    "customer_order_lookup": CustomerOrderLookupArgs,
    "query_database": QueryDatabaseArgs,
    "web_search": WebSearchArgs,
    "generate_report": GenerateReportArgs,
    "search_documents": SearchDocumentsArgs,
    "deep_research": DeepResearchArgs,
}
