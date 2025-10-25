"""
Shared memory system for AI agents to coordinate and share context.
"""
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime
import json


class SharedMemory:
    """
    Thread-safe shared memory system for agent coordination.
    Stores global context, agent statuses, and artifact metadata.
    """
    
    def __init__(self):
        self._memory: Dict[str, Any] = {
            "current_task": None,
            "agent_statuses": {},
            "artifacts_metadata": {},
            "global_context": {},
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        self._lock = asyncio.Lock()
    
    async def read(self, key: str) -> Optional[Any]:
        """Read a value from shared memory."""
        async with self._lock:
            return self._memory.get(key)
    
    async def write(self, key: str, value: Any) -> None:
        """Write a value to shared memory."""
        async with self._lock:
            self._memory[key] = value
            self._memory["last_updated"] = datetime.now().isoformat()
    
    async def update(self, key: str, value: Any) -> None:
        """Update a value in shared memory (same as write for now)."""
        await self.write(key, value)
    
    async def read_all(self) -> Dict[str, Any]:
        """Read the entire shared memory."""
        async with self._lock:
            return self._memory.copy()
    
    async def update_agent_status(self, agent_id: str, status: Dict[str, Any]) -> None:
        """Update an agent's status in shared memory."""
        async with self._lock:
            self._memory["agent_statuses"][agent_id] = {
                **status,
                "last_updated": datetime.now().isoformat()
            }
            self._memory["last_updated"] = datetime.now().isoformat()
    
    async def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get an agent's current status."""
        async with self._lock:
            return self._memory["agent_statuses"].get(agent_id)
    
    async def update_artifact_metadata(self, agent_id: str, artifact_info: Dict[str, Any]) -> None:
        """Update artifact metadata for an agent."""
        async with self._lock:
            self._memory["artifacts_metadata"][agent_id] = {
                **artifact_info,
                "last_updated": datetime.now().isoformat()
            }
            self._memory["last_updated"] = datetime.now().isoformat()
    
    async def get_artifact_metadata(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get artifact metadata for an agent."""
        async with self._lock:
            return self._memory["artifacts_metadata"].get(agent_id)
    
    async def set_current_task(self, task_description: str) -> None:
        """Set the current task for all agents."""
        await self.write("current_task", {
            "description": task_description,
            "created_at": datetime.now().isoformat(),
            "status": "in_progress"
        })
    
    async def get_current_task(self) -> Optional[Dict[str, Any]]:
        """Get the current task."""
        return await self.read("current_task")
    
    async def to_json(self) -> str:
        """Convert shared memory to JSON string."""
        async with self._lock:
            return json.dumps(self._memory, indent=2, default=str)

