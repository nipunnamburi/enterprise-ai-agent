from typing import Dict, List, Optional, Any
from app.tools.base import BaseTool
from app.tools.search_documents import search_documents_tool
from app.tools.query_database import query_database_tool
from app.tools.calculator import calculator_tool
from app.tools.customer_order_lookup import customer_order_lookup_tool
from app.tools.web_search import web_search_tool
from app.tools.generate_report import generate_report_tool
from app.tools.deep_research import deep_research_tool

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self.register_defaults()

    def register(self, tool: BaseTool):
        self._tools[tool.name] = tool

    def register_defaults(self):
        self.register(search_documents_tool)
        self.register(query_database_tool)
        self.register(calculator_tool)
        self.register(customer_order_lookup_tool)
        self.register(web_search_tool)
        self.register(generate_report_tool)
        self.register(deep_research_tool)

    def get_tool(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def list_tools(self) -> List[Dict[str, Any]]:
        return [{
            "name": tool.name,
            "description": tool.description,
            "category": tool.category,
            "parameters": tool.get_parameters_schema()
        } for tool in self._tools.values()]

    def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        tool = self.get_tool(name)
        if not tool:
            return {
                "success": False,
                "error": f"Tool '{name}' is not registered or authorized."
            }
        try:
            return tool.run(**arguments)
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution of tool '{name}' failed: {str(e)}"
            }

tool_registry = ToolRegistry()
