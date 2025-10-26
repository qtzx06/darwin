"""
Shared tools for all Letta agents.
These functions are registered with Letta and can be called by agents.
"""
from typing import Dict, Any, Optional
import asyncio
import json
from datetime import datetime


class AgentTools:
    """
    Collection of tools available to all agents.
    These tools interface with the shared memory and message systems.
    """
    
    def __init__(self, shared_memory, message_broker, artifact_manager):
        self.shared_memory = shared_memory
        self.message_broker = message_broker
        self.artifact_manager = artifact_manager
    
    async def write_code(
        self, 
        language: str, 
        code: str, 
        artifact_id: str,
        agent_id: str
    ) -> Dict[str, Any]:
        """Write code to an artifact."""
        try:
            # Update artifact with new code
            await self.artifact_manager.update_artifact(
                agent_id=agent_id,
                content={
                    "type": "code",
                    "language": language,
                    "code": code,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # Update agent status
            await self.shared_memory.update_agent_status(agent_id, {
                "last_activity": "writing_code",
                "current_language": language,
                "artifact_id": artifact_id
            })
            
            return {
                "success": True,
                "message": f"Code written to artifact {artifact_id}",
                "artifact_id": artifact_id,
                "language": language
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def read_shared_context(self, key: str, agent_id: str) -> Dict[str, Any]:
        """Read from shared memory context."""
        try:
            value = await self.shared_memory.read(key)
            return {
                "success": True,
                "key": key,
                "value": value
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def write_shared_context(
        self, 
        key: str, 
        value: str, 
        agent_id: str
    ) -> Dict[str, Any]:
        """Write to shared memory context."""
        try:
            await self.shared_memory.write(key, value)
            
            # Update agent status
            await self.shared_memory.update_agent_status(agent_id, {
                "last_activity": "updating_shared_context",
                "updated_key": key
            })
            
            return {
                "success": True,
                "message": f"Updated shared context key: {key}",
                "key": key,
                "value": value
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_agent_message(
        self, 
        to_agent: str, 
        message: str, 
        agent_id: str,
        message_type: str = "coordination"
    ) -> Dict[str, Any]:
        """Send a message to another agent."""
        try:
            from ..core.message_system import MessageType
            
            # Map string to MessageType enum
            msg_type_map = {
                "coordination": MessageType.COORDINATION,
                "question": MessageType.QUESTION,
                "response": MessageType.RESPONSE,
                "task_update": MessageType.TASK_UPDATE,
                "argument": MessageType.ARGUMENT,
                "agreement": MessageType.AGREEMENT
            }
            
            msg_type = msg_type_map.get(message_type, MessageType.COORDINATION)
            
            message_id = await self.message_broker.send_message(
                from_agent=agent_id,
                to_agent=to_agent,
                content=message,
                message_type=msg_type
            )
            
            # Update agent status
            await self.shared_memory.update_agent_status(agent_id, {
                "last_activity": "sending_message",
                "message_to": to_agent,
                "message_id": message_id
            })
            
            return {
                "success": True,
                "message_id": message_id,
                "to_agent": to_agent,
                "content": message
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_code(
        self, 
        code: str, 
        language: str,
        agent_id: str
    ) -> Dict[str, Any]:
        """Execute code in a sandboxed environment."""
        try:
            # For now, this is a placeholder - will be replaced with MCP integration
            from ..artifacts.sandbox import SandboxEnvironment
            
            sandbox = SandboxEnvironment()
            result = await sandbox.execute(code, language)
            
            # Update agent status
            await self.shared_memory.update_agent_status(agent_id, {
                "last_activity": "executing_code",
                "language": language,
                "execution_successful": result.get("success", False)
            })
            
            return {
                "success": True,
                "result": result,
                "language": language
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_summary(
        self, 
        current_work: str, 
        agent_id: str,
        progress: str = "",
        next_steps: str = ""
    ) -> Dict[str, Any]:
        """Create a summary of current work progress."""
        try:
            summary = {
                "agent_id": agent_id,
                "current_work": current_work,
                "progress": progress,
                "next_steps": next_steps,
                "timestamp": datetime.now().isoformat()
            }
            
            # Store summary in shared memory
            await self.shared_memory.write(f"agent_summary_{agent_id}", summary)
            
            # Update agent status
            await self.shared_memory.update_agent_status(agent_id, {
                "last_activity": "creating_summary",
                "summary_created": True
            })
            
            return {
                "success": True,
                "summary": summary
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_artifact(
        self, 
        artifact_id: str, 
        content: Dict[str, Any],
        agent_id: str
    ) -> Dict[str, Any]:
        """Update an artifact with new content."""
        try:
            await self.artifact_manager.update_artifact(agent_id, content)
            
            # Update agent status
            await self.shared_memory.update_agent_status(agent_id, {
                "last_activity": "updating_artifact",
                "artifact_id": artifact_id
            })
            
            return {
                "success": True,
                "artifact_id": artifact_id,
                "message": "Artifact updated successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_agent_status(self, target_agent_id: str, agent_id: str) -> Dict[str, Any]:
        """Get status of another agent."""
        try:
            status = await self.shared_memory.get_agent_status(target_agent_id)
            
            return {
                "success": True,
                "agent_id": target_agent_id,
                "status": status
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_recent_messages(self, agent_id: str, limit: int = 5) -> Dict[str, Any]:
        """Get recent messages for the agent."""
        try:
            messages = await self.message_broker.get_recent_messages(agent_id, limit)
            message_dicts = [msg.to_dict() for msg in messages]
            
            return {
                "success": True,
                "messages": message_dicts,
                "count": len(message_dicts)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def broadcast_update(
        self, 
        message: str, 
        agent_id: str,
        message_type: str = "task_update"
    ) -> Dict[str, Any]:
        """Broadcast an update to all agents."""
        try:
            from ..core.message_system import MessageType
            
            msg_type_map = {
                "task_update": MessageType.TASK_UPDATE,
                "coordination": MessageType.COORDINATION,
                "broadcast": MessageType.BROADCAST
            }
            
            msg_type = msg_type_map.get(message_type, MessageType.BROADCAST)
            
            message_id = await self.message_broker.broadcast(
                from_agent=agent_id,
                content=message,
                message_type=msg_type
            )
            
            return {
                "success": True,
                "message_id": message_id,
                "message": message
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


def create_tool_functions(agent_tools: AgentTools, agent_id: str):
    """
    Create tool functions that can be registered with Letta.
    Each function is bound to a specific agent ID.
    """
    
    async def write_code(language: str, code: str, artifact_id: str) -> Dict[str, Any]:
        return await agent_tools.write_code(language, code, artifact_id, agent_id)
    
    async def read_shared_context(key: str) -> Dict[str, Any]:
        return await agent_tools.read_shared_context(key, agent_id)
    
    async def write_shared_context(key: str, value: str) -> Dict[str, Any]:
        return await agent_tools.write_shared_context(key, value, agent_id)
    
    async def send_agent_message(to_agent: str, message: str, message_type: str = "coordination") -> Dict[str, Any]:
        return await agent_tools.send_agent_message(to_agent, message, agent_id, message_type)
    
    async def execute_code(code: str, language: str) -> Dict[str, Any]:
        return await agent_tools.execute_code(code, language, agent_id)
    
    async def create_summary(current_work: str, progress: str = "", next_steps: str = "") -> Dict[str, Any]:
        return await agent_tools.create_summary(current_work, agent_id, progress, next_steps)
    
    async def update_artifact(artifact_id: str, content: Dict[str, Any]) -> Dict[str, Any]:
        return await agent_tools.update_artifact(artifact_id, content, agent_id)
    
    async def get_agent_status(target_agent_id: str) -> Dict[str, Any]:
        return await agent_tools.get_agent_status(target_agent_id, agent_id)
    
    async def get_recent_messages(limit: int = 5) -> Dict[str, Any]:
        return await agent_tools.get_recent_messages(agent_id, limit)
    
    async def broadcast_update(message: str, message_type: str = "task_update") -> Dict[str, Any]:
        return await agent_tools.broadcast_update(message, agent_id, message_type)
    
    return {
        "write_code": write_code,
        "read_shared_context": read_shared_context,
        "write_shared_context": write_shared_context,
        "send_agent_message": send_agent_message,
        "execute_code": execute_code,
        "create_summary": create_summary,
        "update_artifact": update_artifact,
        "get_agent_status": get_agent_status,
        "get_recent_messages": get_recent_messages,
        "broadcast_update": broadcast_update
    }

