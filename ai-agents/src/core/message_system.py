"""
Message system for agent-to-agent communication with history tracking.
"""
from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class MessageType(Enum):
    """Types of messages agents can send."""
    TASK_UPDATE = "task_update"
    COORDINATION = "coordination"
    QUESTION = "question"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    ARGUMENT = "argument"
    AGREEMENT = "agreement"


@dataclass
class Message:
    """Represents a message between agents."""
    id: str
    from_agent: str
    to_agent: Optional[str]  # None for broadcasts
    content: str
    message_type: MessageType
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "id": self.id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "content": self.content,
            "message_type": self.message_type.value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata or {}
        }


class MessageBroker:
    """
    Handles agent-to-agent communication with message history.
    Thread-safe message passing system.
    """
    
    def __init__(self):
        self._messages: List[Message] = []
        self._agent_messages: Dict[str, List[Message]] = {}
        self._lock = asyncio.Lock()
        self._message_counter = 0
    
    def _generate_message_id(self) -> str:
        """Generate unique message ID."""
        self._message_counter += 1
        return f"msg_{self._message_counter}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    async def send_message(
        self, 
        from_agent: str, 
        to_agent: str, 
        content: str, 
        message_type: MessageType = MessageType.COORDINATION,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Send a message from one agent to another."""
        message_id = self._generate_message_id()
        message = Message(
            id=message_id,
            from_agent=from_agent,
            to_agent=to_agent,
            content=content,
            message_type=message_type,
            timestamp=datetime.now(),
            metadata=metadata
        )
        
        async with self._lock:
            self._messages.append(message)
            
            # Add to recipient's message list
            if to_agent not in self._agent_messages:
                self._agent_messages[to_agent] = []
            self._agent_messages[to_agent].append(message)
        
        return message_id
    
    async def broadcast(
        self, 
        from_agent: str, 
        content: str, 
        message_type: MessageType = MessageType.BROADCAST,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Broadcast a message to all agents."""
        message_id = self._generate_message_id()
        message = Message(
            id=message_id,
            from_agent=from_agent,
            to_agent=None,  # None indicates broadcast
            content=content,
            message_type=message_type,
            timestamp=datetime.now(),
            metadata=metadata
        )
        
        async with self._lock:
            self._messages.append(message)
            
            # Add to all agent message lists
            for agent_id in self._agent_messages.keys():
                self._agent_messages[agent_id].append(message)
        
        return message_id
    
    async def get_messages(self, agent_id: str) -> List[Message]:
        """Get all messages for a specific agent."""
        async with self._lock:
            return self._agent_messages.get(agent_id, []).copy()
    
    async def get_recent_messages(self, agent_id: str, limit: int = 10) -> List[Message]:
        """Get recent messages for an agent."""
        messages = await self.get_messages(agent_id)
        return messages[-limit:] if messages else []
    
    async def get_messages_by_type(
        self, 
        agent_id: str, 
        message_type: MessageType
    ) -> List[Message]:
        """Get messages of a specific type for an agent."""
        messages = await self.get_messages(agent_id)
        return [msg for msg in messages if msg.message_type == message_type]
    
    async def get_all_messages(self) -> List[Message]:
        """Get all messages (for commentator visibility)."""
        async with self._lock:
            return self._messages.copy()
    
    async def get_conversation(self, agent1: str, agent2: str) -> List[Message]:
        """Get conversation between two specific agents."""
        async with self._lock:
            conversation = []
            for message in self._messages:
                if ((message.from_agent == agent1 and message.to_agent == agent2) or
                    (message.from_agent == agent2 and message.to_agent == agent1)):
                    conversation.append(message)
            return conversation
    
    async def clear_agent_messages(self, agent_id: str) -> None:
        """Clear all messages for a specific agent."""
        async with self._lock:
            if agent_id in self._agent_messages:
                self._agent_messages[agent_id] = []
    
    async def get_message_stats(self) -> Dict[str, Any]:
        """Get statistics about messages."""
        async with self._lock:
            total_messages = len(self._messages)
            agent_counts = {agent_id: len(msgs) for agent_id, msgs in self._agent_messages.items()}
            type_counts = {}
            
            for message in self._messages:
                msg_type = message.message_type.value
                type_counts[msg_type] = type_counts.get(msg_type, 0) + 1
            
            return {
                "total_messages": total_messages,
                "agent_message_counts": agent_counts,
                "message_type_counts": type_counts,
                "unique_agents": len(self._agent_messages)
            }

