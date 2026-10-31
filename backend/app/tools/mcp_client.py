import json
import logging
from typing import Dict, Any, List, Optional
import httpx
from app.tools.base import BaseTool

logger = logging.getLogger(__name__)

class MCPToolAdapter(BaseTool):
    """
    Dynamic BaseTool adapter that bridges any remote or local MCP server tool
    into the agent's ToolRegistry.
    """
    def __init__(self, mcp_client: "MCPClient", tool_def: Dict[str, Any]):
        self.client = mcp_client
        self.name = f"mcp_{tool_def.get('name', 'unnamed')}"
        self.raw_name = tool_def.get("name", "unnamed")
        self.description = tool_def.get("description", "Dynamic tool registered via Model Context Protocol.")
        self.category = "mcp_integration"
        self._input_schema = tool_def.get("inputSchema", {
            "type": "object",
            "properties": {},
            "required": []
        })

    def get_parameters_schema(self) -> Dict[str, Any]:
        return self._input_schema

    def run(self, **kwargs) -> Dict[str, Any]:
        return self.client.call_tool(self.raw_name, kwargs)


class MCPClient:
    """
    Model Context Protocol (MCP) JSON-RPC 2.0 client.
    Supports HTTP/SSE transports, standard MCP handshake, tool discovery,
    and invocation as used in Enterprise-Multi-Agent-Engine.
    """
    def __init__(self, server_url: Optional[str] = None, auth_token: Optional[str] = None):
        self.server_url = server_url
        self.auth_token = auth_token
        self._request_id = 0
        self._is_initialized = False
        self._registered_adapters: Dict[str, MCPToolAdapter] = {}

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    def initialize(self) -> Dict[str, Any]:
        """Performs standard MCP initialize handshake (client capabilities <-> server capabilities)."""
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": True}
                },
                "clientInfo": {
                    "name": "enterprise-ai-agent-client",
                    "version": "1.0.0"
                }
            }
        }
        res = self._send_request(payload)
        self._is_initialized = True
        return res

    def list_tools(self) -> List[Dict[str, Any]]:
        """Queries the MCP server for available tools via tools/list."""
        if not self._is_initialized:
            self.initialize()

        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/list",
            "params": {}
        }
        res = self._send_request(payload)
        if "error" in res:
            logger.error(f"[MCP] list_tools returned error: {res['error']}")
            return []
        return res.get("result", {}).get("tools", [])

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Invokes a specific tool on the MCP server via tools/call."""
        if not self._is_initialized:
            self.initialize()

        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments
            }
        }
        res = self._send_request(payload)
        if "error" in res:
            return {
                "success": False,
                "error": res["error"].get("message", "MCP Tool Execution Failed"),
                "code": res["error"].get("code", -32000)
            }
        
        result = res.get("result", {})
        content_items = result.get("content", [])
        text_output = "\n".join([item.get("text", "") for item in content_items if item.get("type") == "text"])
        
        return {
            "success": not result.get("isError", False),
            "tool_name": name,
            "output": text_output or str(result),
            "content": content_items
        }

    def _send_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatches JSON-RPC request to HTTP endpoint or local mock server."""
        if self.server_url and self.server_url.startswith("http"):
            headers = {"Content-Type": "application/json"}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            try:
                with httpx.Client(timeout=10.0) as client:
                    resp = client.post(self.server_url, json=payload, headers=headers)
                    if resp.status_code == 200:
                        return resp.json()
                    return {
                        "jsonrpc": "2.0",
                        "id": payload.get("id"),
                        "error": {"code": resp.status_code, "message": resp.text}
                    }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": payload.get("id"),
                    "error": {"code": -32603, "message": f"Connection error: {str(e)}"}
                }

        # Simulated enterprise MCP server (Jira/Confluence & Cloud monitoring) for local/offline execution
        return self._simulate_mcp_server(payload)

    def _simulate_mcp_server(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        method = payload.get("method")
        req_id = payload.get("id")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "enterprise-embedded-mcp", "version": "1.0.0"}
                }
            }

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": [
                        {
                            "name": "enterprise_jira_issue_lookup",
                            "description": "Fetches enterprise Jira issue details, priority, and assignees.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "issue_key": {"type": "string", "description": "Jira issue key (e.g. PROJ-102)"}
                                },
                                "required": ["issue_key"]
                            }
                        },
                        {
                            "name": "enterprise_cloud_health",
                            "description": "Queries real-time infrastructure latency, CPU, and memory metrics.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "service_name": {"type": "string", "description": "Target cloud microservice name"}
                                },
                                "required": ["service_name"]
                            }
                        }
                    ]
                }
            }

        elif method == "tools/call":
            params = payload.get("params", {})
            name = params.get("name")
            args = params.get("arguments", {})

            if name == "enterprise_jira_issue_lookup":
                key = args.get("issue_key", "UNKNOWN")
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": f"Issue {key}: Status='IN_PROGRESS', Priority='High', Assignee='Dev Team Lead', Summary='Investigate SLA reporting variance'"
                        }],
                        "isError": False
                    }
                }
            elif name == "enterprise_cloud_health":
                svc = args.get("service_name", "api-gateway")
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": f"Service '{svc}': Status=HEALTHY, CPU_Utilization=34.2%, Memory_Usage=58.1%, P99_Latency=42ms"
                        }],
                        "isError": False
                    }
                }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method or tool '{name}' not found on MCP server"}
                }

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Unsupported method '{method}'"}
        }

    def sync_to_registry(self, registry) -> List[str]:
        """Discovers tools from MCP server and dynamically registers MCPToolAdapters."""
        tools = self.list_tools()
        registered = []
        for t in tools:
            adapter = MCPToolAdapter(self, t)
            registry.register(adapter)
            self._registered_adapters[adapter.name] = adapter
            registered.append(adapter.name)
        return registered

