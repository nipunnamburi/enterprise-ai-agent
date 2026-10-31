import pytest
from app.tools.mcp_client import MCPClient, MCPToolAdapter
from app.tools.registry import tool_registry

def test_mcp_initialization_handshake():
    client = MCPClient()
    res = client.initialize()
    assert res.get("jsonrpc") == "2.0"
    assert "result" in res
    assert res["result"]["protocolVersion"] == "2024-11-05"
    assert "enterprise-embedded-mcp" in res["result"]["serverInfo"]["name"]

def test_mcp_list_tools_discovery():
    client = MCPClient()
    tools = client.list_tools()
    assert len(tools) >= 2
    tool_names = [t["name"] for t in tools]
    assert "enterprise_jira_issue_lookup" in tool_names
    assert "enterprise_cloud_health" in tool_names

def test_mcp_tool_execution():
    client = MCPClient()
    res = client.call_tool("enterprise_jira_issue_lookup", {"issue_key": "SEC-809"})
    assert res["success"] is True
    assert "Issue SEC-809" in res["output"]
    assert "IN_PROGRESS" in res["output"]

def test_mcp_tool_adapter_in_registry():
    # The default registry syncs default MCP client tools prefixed with mcp_
    jira_tool = tool_registry.get_tool("mcp_enterprise_jira_issue_lookup")
    assert jira_tool is not None
    assert jira_tool.category == "mcp_integration"
    
    schema = jira_tool.get_parameters_schema()
    assert "issue_key" in schema.get("properties", {})

    exec_result = tool_registry.execute_tool("mcp_enterprise_jira_issue_lookup", {
        "issue_key": "PROJ-441"
    })
    assert exec_result["success"] is True
    assert "PROJ-441" in exec_result["output"]

    health_exec = tool_registry.execute_tool("mcp_enterprise_cloud_health", {
        "service_name": "payment-service"
    })
    assert health_exec["success"] is True
    assert "payment-service" in health_exec["output"]
    assert "HEALTHY" in health_exec["output"]

def test_mcp_unknown_tool_error():
    client = MCPClient()
    res = client.call_tool("non_existent_tool", {})
    assert res["success"] is False
    assert "not found" in res["error"].lower()
