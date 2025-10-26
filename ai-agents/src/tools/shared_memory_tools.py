"""
Letta Tools for Shared Memory Communication
Tools that Letta agents use to post/read from shared memory
"""
from typing import Optional
import json
from datetime import datetime


def post_to_shared_memory(agent_name: str, message: str, recipient: Optional[str] = None) -> str:
    """
    Post a message to shared memory for other agents to see.
    
    Args:
        agent_name: Your agent name (e.g., "Agent 1")
        message: The message content to share
        recipient: Optional - specific agent to address (e.g., "Agent 2", "Orchestrator", "all")
    
    Returns:
        Confirmation message
    """
    # This will be intercepted and handled by the system
    # The actual implementation will append to the shared memory block
    
    timestamp = datetime.now().isoformat()
    
    if recipient:
        formatted_message = f"[{timestamp}] {agent_name} → {recipient}: {message}"
    else:
        formatted_message = f"[{timestamp}] {agent_name}: {message}"
    
    # Return confirmation
    return f"✓ Posted to shared memory: {formatted_message[:100]}..."


def read_shared_memory() -> str:
    """
    Read the current shared memory contents to see what other agents have posted.
    
    Returns:
        The shared memory conversation log
    """
    # This will be intercepted and handled by the system
    # The actual implementation will read from the shared memory block
    return "Reading shared memory..."


def announce_deliverable_complete(agent_name: str, description: str) -> str:
    """
    Announce that you have completed your deliverable for the current subtask.
    
    Args:
        agent_name: Your agent name
        description: Brief description of what you delivered (not the code itself)
    
    Returns:
        Confirmation message
    """
    timestamp = datetime.now().isoformat()
    formatted_message = f"[{timestamp}] {agent_name} ✅ DELIVERABLE COMPLETE: {description}"
    
    return f"✓ Announced completion: {formatted_message}"


def get_current_subtask() -> str:
    """
    Get the current subtask assigned by the orchestrator.
    
    Returns:
        The current subtask description
    """
    # This will be intercepted and handled by the system
    return "Fetching current subtask..."
