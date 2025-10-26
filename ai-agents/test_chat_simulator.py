"""
Quick test script to verify the chat simulator is working.
Run this if you want to test without the full interactive chat.
"""
import asyncio
import os
from dotenv import load_dotenv
from chat_config import get_system_prompt, AGENT_NAMES
from chat_manager import ClaudeManager


async def test_chat():
    """Quick test of the chat system."""
    print("🧪 Testing Chat Simulator Components...\n")
    
    # Load environment
    load_dotenv()
    api_key = os.getenv("CLAUDE_API_KEY")
    
    if not api_key:
        print("❌ CLAUDE_API_KEY not found in .env file")
        return
    
    print("✅ Claude API key found")
    
    # Initialize Claude manager
    try:
        manager = ClaudeManager(system_prompt=get_system_prompt())
        print("✅ Claude manager initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Claude manager: {e}")
        return
    
    # Test a simple chat trigger
    print("\n📝 Testing chat generation...")
    print("   Trigger: Frontend wants to talk to Backend\n")
    
    trigger = "[Random chat moment: Frontend wants to say something to Backend. Generate their message naturally.]"
    
    response = await manager.get_chat_response(trigger)
    
    if response:
        print("✅ Got response from Claude:\n")
        print(f"   {response}")
        print("\n✅ All tests passed! Run `python chat_simulator.py` to start the full chat.")
    else:
        print("❌ No response from Claude")


if __name__ == "__main__":
    asyncio.run(test_chat())
