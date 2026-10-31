from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTool(ABC):
    name: str
    description: str
    category: str = "general"

    @abstractmethod
    def get_parameters_schema(self) -> Dict[str, Any]:
        """Returns JSON schema of parameters accepted by this tool."""
        pass

    @abstractmethod
    def run(self, **kwargs) -> Dict[str, Any]:
        """Executes tool synchronously or asynchronously."""
        pass
