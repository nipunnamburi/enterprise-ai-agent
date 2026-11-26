import json
import os
import asyncio
from typing import Dict, Any, List, Optional
from langchain_mcp_adapters.client import MultiServerMCPClient
from app.tools.base import BaseTool


class MCPToolAdapter(BaseTool):
    """Wraps a LangChain MCP StructuredTool into the repository's BaseTool interface."""

    def __init__(self, lc_tool: Any, requires_approval: bool = True):
        self.name = lc_tool.name
        self.description = getattr(lc_tool, "description", "") or f"MCP tool {lc_tool.name}"
        self.category = "mcp"
        self.requires_approval = requires_approval
        self._lc_tool = lc_tool

    def get_parameters_schema(self) -> Dict[str, Any]:
        args_schema = getattr(self._lc_tool, "args_schema", None)
        if isinstance(args_schema, dict):
            return args_schema
        if hasattr(args_schema, "model_json_schema"):
            return args_schema.model_json_schema()
        return {"type": "object", "properties": {}}

    def run(self, **kwargs) -> Dict[str, Any]:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                result = pool.submit(lambda: asyncio.run(self._lc_tool.ainvoke(kwargs))).result()
        else:
            result = asyncio.run(self._lc_tool.ainvoke(kwargs))
        return {"success": True, "data": result}


def load_mcp_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    path = config_path or os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../mcp_servers.json")
    )
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("mcpServers", data) if isinstance(data, dict) else {}


async def load_mcp_tools(config_path: Optional[str] = None) -> List[MCPToolAdapter]:
    """Load external MCP tools via langchain-mcp-adapters MultiServerMCPClient."""
    servers = load_mcp_config(config_path)
    if not servers:
        return []

    client = MultiServerMCPClient(servers)
    lc_tools = await client.get_tools()
    adapters: List[MCPToolAdapter] = []
    for lc_tool in lc_tools:
        # Mark mutating/external MCP tools as requiring approval by default
        adapters.append(MCPToolAdapter(lc_tool, requires_approval=True))
    return adapters
