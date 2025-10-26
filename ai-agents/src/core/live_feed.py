"""
Live Feed System for Real-time Updates
Streams AutoGen conversations and Letta PM updates to the commentator
"""
import asyncio
from typing import Dict, Any, List, Callable
from datetime import datetime
from collections import deque
import json


class LiveFeedEvent:
    """Represents a single update in the live feed."""
    
    def __init__(
        self,
        event_type: str,  # "autogen_message", "pm_update", "code_generated", "review_complete"
        agent_id: str,
        agent_name: str,
        content: Any,
        timestamp: str = None
    ):
        self.event_type = event_type
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.content = content
        self.timestamp = timestamp or datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "content": self.content,
            "timestamp": self.timestamp
        }


class LiveFeed:
    """
    Central live feed system that collects real-time updates from all agents.
    Commentator subscribes to this feed for live narrative generation.
    """
    
    def __init__(self, max_events: int = 1000):
        self.events: deque = deque(maxlen=max_events)
        self.subscribers: List[Callable] = []
        self._lock = asyncio.Lock()
        self.current_subtask_id = None
        
    async def publish_event(self, event: LiveFeedEvent):
        """Publish a new event to the feed."""
        async with self._lock:
            self.events.append(event)
            
            # Notify all subscribers
            for subscriber in self.subscribers:
                try:
                    if asyncio.iscoroutinefunction(subscriber):
                        await subscriber(event)
                    else:
                        subscriber(event)
                except Exception as e:
                    print(f"Warning: Subscriber notification failed: {e}")
    
    def subscribe(self, callback: Callable):
        """Subscribe to live feed updates."""
        self.subscribers.append(callback)
    
    def unsubscribe(self, callback: Callable):
        """Unsubscribe from live feed."""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
    
    async def get_recent_events(
        self,
        count: int = 50,
        event_types: List[str] = None,
        agent_id: str = None
    ) -> List[LiveFeedEvent]:
        """Get recent events from the feed."""
        async with self._lock:
            events = list(self.events)
            
            # Filter by event type
            if event_types:
                events = [e for e in events if e.event_type in event_types]
            
            # Filter by agent
            if agent_id:
                events = [e for e in events if e.agent_id == agent_id]
            
            # Return most recent
            return events[-count:] if len(events) > count else events
    
    async def get_events_since(self, timestamp: str) -> List[LiveFeedEvent]:
        """Get all events since a specific timestamp."""
        async with self._lock:
            return [e for e in self.events if e.timestamp > timestamp]
    
    async def clear_subtask_events(self):
        """Clear events when starting a new subtask."""
        async with self._lock:
            self.events.clear()
    
    def set_current_subtask(self, subtask_id: int):
        """Set the current subtask being worked on."""
        self.current_subtask_id = subtask_id
    
    async def get_subtask_summary(self) -> Dict[str, Any]:
        """Get a summary of activity for current subtask."""
        async with self._lock:
            events_list = list(self.events)
            
            return {
                "subtask_id": self.current_subtask_id,
                "total_events": len(events_list),
                "event_types": {
                    event_type: len([e for e in events_list if e.event_type == event_type])
                    for event_type in set(e.event_type for e in events_list)
                },
                "agents_active": len(set(e.agent_id for e in events_list)),
                "latest_timestamp": events_list[-1].timestamp if events_list else None
            }


# Singleton instance
_live_feed_instance = None

def get_live_feed() -> LiveFeed:
    """Get the global live feed instance."""
    global _live_feed_instance
    if _live_feed_instance is None:
        _live_feed_instance = LiveFeed()
    return _live_feed_instance
