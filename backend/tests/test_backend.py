import os
import sys
import pytest
from fastapi.testclient import TestClient

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app
from app.tools.registry import tool_registry
from app.core.security import create_access_token

client = TestClient(app)

def get_auth_headers(sub="demo-user-123"):
    token = create_access_token(subject=sub)
    return {"Authorization": f"Bearer {token}"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_list_tools():
    response = client.get("/tools", headers=get_auth_headers())
    assert response.status_code == 200
    tools = response.json()
    tool_names = [t["name"] for t in tools]
    assert "search_documents" in tool_names
    assert "query_database" in tool_names
    assert "calculator" in tool_names
    assert "customer_order_lookup" in tool_names
    assert "web_search" in tool_names
    assert "generate_report" in tool_names

def test_calculator_tool():
    result = tool_registry.execute_tool("calculator", {"expression": "2499.00 * 0.85"})
    assert result["success"] is True
    assert result["result"] == 2124.15

def test_customer_order_lookup_tool():
    result = tool_registry.execute_tool("customer_order_lookup", {"order_number": "1024"})
    assert result["success"] is True
    assert "order" in result["data"]
    assert result["data"]["order"]["order_number"] == "1024"

def test_query_database_tool():
    result = tool_registry.execute_tool("query_database", {
        "entity": "sales",
        "filters": {"quarter": "Q3", "year": 2024},
        "aggregation": "sum_revenue"
    })
    assert result["success"] is True
    assert result["total_actual_revenue"] > 0

def test_agent_chat_multistep():
    payload = {
        "message": "Analyze customer complaint for order 1024, check refund policy, and calculate the refund amount.",
        "user_id": "demo-user-123"
    }
    response = client.post("/agent/chat", json=payload, headers=get_auth_headers())
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert len(data["execution_steps"]) > 0
    assert data["task_id"].startswith("task-")
