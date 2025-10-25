#!/usr/bin/env python3
"""
Demo script to show real Letta agents working on a task.
"""
import asyncio
import os
from dotenv import load_dotenv
from letta_client import Letta

async def demo_real_agents():
    """Demonstrate real Letta agents working on a task."""
    load_dotenv()
    
    client = Letta(token=os.getenv("LETTA_API_TOKEN"))
    
    # Get agent IDs
    frontend_id = os.getenv("LETTA_CODING_AGENT_ID_1")
    backend_id = os.getenv("LETTA_CODING_AGENT_ID_2")
    commentator_id = os.getenv("LETTA_COMMENTATOR_AGENT_ID")
    
    print("🚀 Real Letta Agents Demo")
    print("=" * 50)
    
    # Task for the agents
    task = "Build a simple calculator app with React frontend and Node.js backend"
    
    print(f"📋 Task: {task}")
    print()
    
    # Frontend Specialist
    print("🎨 Frontend Specialist working...")
    frontend_response = client.agents.messages.create(
        agent_id=frontend_id,
        messages=[{"role": "user", "content": f"Task: {task}\n\nAs a Frontend Specialist, design and implement the React frontend for this calculator app. Provide the complete React component code with modern styling."}]
    )
    
    print("Frontend Specialist Response:")
    for msg in frontend_response.messages:
        if msg.message_type == "assistant_message":
            print(f"  {msg.content}")
            break
    print()
    
    # Backend Architect
    print("🏗️  Backend Architect working...")
    backend_response = client.agents.messages.create(
        agent_id=backend_id,
        messages=[{"role": "user", "content": f"Task: {task}\n\nAs a Backend Architect, design and implement the Node.js backend API for this calculator app. Provide the complete server code with proper error handling."}]
    )
    
    print("Backend Architect Response:")
    for msg in backend_response.messages:
        if msg.message_type == "assistant_message":
            print(f"  {msg.content}")
            break
    print()
    
    # Project Narrator
    print("🎙️  Project Narrator observing...")
    commentator_response = client.agents.messages.create(
        agent_id=commentator_id,
        messages=[{"role": "user", "content": f"Task: {task}\n\nAs a Project Narrator, observe the progress of the Frontend Specialist and Backend Architect on this calculator app project. Provide a summary of what has been accomplished and what the next steps should be."}]
    )
    
    print("Project Narrator Response:")
    for msg in commentator_response.messages:
        if msg.message_type == "assistant_message":
            print(f"  {msg.content}")
            break
    print()
    
    print("✅ Demo completed! Real Letta agents successfully collaborated on the task.")

if __name__ == "__main__":
    asyncio.run(demo_real_agents())

