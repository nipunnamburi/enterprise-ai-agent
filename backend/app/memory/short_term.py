from typing import Dict, Any, List
from datetime import datetime, timezone

class EphemeralTaskMemory:
    """Manages short-term scratchpad memory during multi-step LangGraph agent execution."""
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}

    def init_task(self, task_id: str, objective: str):
        self._cache[task_id] = {
            "objective": objective,
            "intermediate_results": [],
            "entity_graph": {},
            "created_at": datetime.now(timezone.utc).isoformat()
        }

    def record_step(self, task_id: str, step_name: str, data: Any):
        if task_id in self._cache:
            self._cache[task_id]["intermediate_results"].append({
                "step": step_name,
                "data": data,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })

    def get_task_scratchpad(self, task_id: str) -> Dict[str, Any]:
        return self._cache.get(task_id, {})

    def cleanup_task(self, task_id: str):
        if task_id in self._cache:
            del self._cache[task_id]

ephemeral_memory = EphemeralTaskMemory()
