import pytest
from app.tools.deep_research import DeepResearchSynthesizer, deep_research_tool
from app.tools.registry import tool_registry
from app.core.security import create_access_token
from app.agents.graph import agent_graph

def test_deep_research_decomposition():
    synthesizer = DeepResearchSynthesizer()
    sub_queries = synthesizer.decompose_topic("Autonomous AI Deployment", focus_areas=["security", "compliance", "scalability"])
    
    assert len(sub_queries) == 3
    assert sub_queries[0]["focus_area"] == "security"
    assert "security" in sub_queries[0]["query"].lower()
    assert sub_queries[1]["focus_area"] == "compliance"
    assert sub_queries[2]["focus_area"] == "scalability"

def test_deep_research_multi_hop_execution():
    synthesizer = DeepResearchSynthesizer()
    res = synthesizer.execute_deep_research("Enterprise SaaS SLA benchmark standards", depth=2)
    
    assert res["total_hops"] == 2
    assert len(res["hops_record"]) == 2
    assert res["hops_record"][0]["hop"] == 1
    assert res["hops_record"][1]["hop"] == 2
    assert res["sources_count"] > 0
    assert len(res["claims"]) > 0
    assert "Enterprise SaaS SLA & Refund Standards 2024" in [s["title"] for s in res["sources"]]
    assert "Executive Summary" in res["dossier"]
    assert "Key Verified Findings & Claims" in res["dossier"]

def test_deep_research_registry_integration():
    tool = tool_registry.get_tool("deep_research")
    assert tool is not None
    assert tool.name == "deep_research"
    assert tool.category == "research_and_synthesis"

    result = tool_registry.execute_tool("deep_research", {
        "topic": "B2B hardware return policy benchmarks",
        "depth": 2
    })

    assert result["success"] is True
    assert "completed deep research" in result["summary"].lower()
    assert len(result["sources_consulted"]) > 0
    assert len(result["claims"]) > 0
    assert "dossier" in result

def test_deep_research_validation_empty_topic():
    result = tool_registry.execute_tool("deep_research", {"topic": "   "})
    assert result["success"] is False
    assert "Parameter 'topic' must be a non-empty string" in result["error"]

def test_deep_research_api_endpoint(client):
    token = create_access_token(subject="demo-user-123")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/agent/research", json={
        "topic": "Enterprise SaaS uptime benchmark standards",
        "depth": 1,
        "focus_areas": ["sla", "compliance"]
    }, headers=headers)

    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "Enterprise Deep Research Dossier" in data["dossier"]
    assert len(data["sources_consulted"]) > 0
    assert len(data["claims"]) > 0

def test_deep_research_agent_graph_workflow():
    initial_state = {
        "user_id": "demo-user-123",
        "conversation_id": "conv-deep-res-1",
        "task_id": "task-deep-res-1",
        "messages": [],
        "current_task": "Conduct recursive deep research on enterprise SLA uptime benchmarks",
        "user_memories": [],
        "compressed_history_summary": None,
        "plan": None,
        "execution_trace": [],
        "retrieved_documents": [],
        "pending_tool_calls": [],
        "tool_results": [],
        "tools_used": [],
        "iterations": 0,
        "is_complete": False,
        "evaluation": None,
        "final_answer": None,
        "sources": [],
        "confidence": "high",
        "key_findings": []
    }

    final_state = agent_graph.invoke(initial_state)
    assert "deep_research" in final_state.get("tools_used", [])
    assert "Enterprise Deep Research Dossier" in final_state.get("final_answer", "")
    assert len(final_state.get("sources", [])) > 0
