#!/usr/bin/env python3
"""
Debug script to test individual agent responses.
"""
import asyncio
import os
from dotenv import load_dotenv
from letta_client import Letta

async def test_agent_response():
    """Test a single agent response."""
    load_dotenv()
    
    client = Letta(token=os.getenv("LETTA_API_TOKEN"))
    
    # Get agent ID
    agent_id = os.getenv("LETTA_CODING_AGENT_ID_1")
    
    print(f"Testing agent: {agent_id}")
    
    # Send a simple message
    response = client.agents.messages.create(
        agent_id=agent_id,
        messages=[{"role": "user", "content": "Write a simple Python function to add two numbers."}]
    )
    
    print("Response:")
    print(f"Number of messages: {len(response.messages)}")
    
    for i, msg in enumerate(response.messages):
        print(f"Message {i}:")
        print(f"  Type: {msg.message_type}")
        print(f"  Content: {msg.content}")
        print()

if __name__ == "__main__":
    asyncio.run(test_agent_response())

