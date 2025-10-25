#!/usr/bin/env python3
"""
Test script to verify that personality agents generate LLM-based messages.
"""

import asyncio
import sys
import os
sys.path.append('src')

from main_personality import PersonalityPMSimulator

async def test_personality_messages():
    """Test that agents generate LLM-based messages."""
    print("🧪 Testing Personality Message Generation...")
    
    simulator = PersonalityPMSimulator()
    
    if not await simulator.initialize_agents():
        print("❌ Failed to initialize agents")
        return
    
    print("✅ Agents initialized successfully!")
    
    # Test with a simple task
    task = "Create a simple hello world function"
    print(f"\n🎯 Testing with task: {task}")
    
    # Run a quick simulation
    await simulator.run_simulation(task)
    
    print("\n✅ Test completed! Check the logs to see LLM-generated messages.")

if __name__ == "__main__":
    asyncio.run(test_personality_messages())
