#!/usr/bin/env python3
"""
Test script to verify the new SYNCHRONOUS CONVERSATIONAL system with Letta's built-in tools.
"""

import asyncio
import sys
import os
sys.path.append('src')

from main_personality import PersonalityPMSimulator

async def test_synchronous_conversations():
    """Test the new synchronous conversational system."""
    print("🧪 Testing SYNCHRONOUS CONVERSATIONAL System...")
    print("Using Letta's built-in multi-agent tools for real conversations!")
    
    simulator = PersonalityPMSimulator()
    
    if not await simulator.initialize_agents():
        print("❌ Failed to initialize agents")
        return
    
    print("✅ Agents initialized successfully!")
    
    # Test with a simple task
    task = "Build a simple todo app with React frontend and Node.js backend"
    print(f"\n🎯 Testing with task: {task}")
    
    # Run the synchronous conversational simulation
    await simulator.run_simulation(task)
    
    print("\n✅ SYNCHRONOUS CONVERSATIONAL test completed!")
    print("Check the logs to see the real conversations between agents!")

if __name__ == "__main__":
    asyncio.run(test_synchronous_conversations())
