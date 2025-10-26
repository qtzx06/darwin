#!/usr/bin/env python3
"""
Non-Interactive Code Output Demo
Shows the actual code outputs from each agent without requiring user input.
"""

import requests
import json
import time
import sys

# Flask API configuration
FLASK_BASE_URL = "http://localhost:5003"

def demo_code_outputs():
    """Demo the actual code outputs from each agent."""
    print("🎭 Competitive AI Agents - Code Output Demo")
    print("=" * 60)
    print("NOTE: This shows REAL code outputs from Letta AI agents with different personalities.")
    print("=" * 60)
    
    try:
        # Step 1: Health Check
        print("\n🔥 STEP 1: Health Check")
        response = requests.get(f"{FLASK_BASE_URL}/api/health", timeout=10)
        if response.status_code != 200:
            print("❌ Server not running!")
            return False
        print("✅ Server is running")
        
        # Step 2: Submit Project
        print("\n🔥 STEP 2: Submit Project")
        project_data = {"project_description": "Build a todo app"}
        response = requests.post(f"{FLASK_BASE_URL}/api/submit-project", json=project_data, timeout=10)
        if response.status_code != 200:
            print("❌ Submit project failed!")
            return False
        
        project_result = response.json()
        project_id = project_result.get('project_id')
        subtasks = project_result.get('subtasks', [])
        print(f"✅ Project created: {project_id}")
        print(f"📋 Subtasks: {len(subtasks)}")
        
        # Step 3: Create Agents
        print("\n🔥 STEP 3: Create Agents")
        print("⏳ This will take 30-60 seconds as we send context reset to real Letta agents...")
        agents_data = {"project_id": project_id}
        response = requests.post(f"{FLASK_BASE_URL}/api/create-agents", json=agents_data, timeout=120)
        if response.status_code != 200:
            print("❌ Create agents failed!")
            return False
        print("✅ Agents created")
        
        # Step 4: Start Work
        print("\n🔥 STEP 4: Start Work")
        work_data = {"project_id": project_id, "subtask_id": 1}
        response = requests.post(f"{FLASK_BASE_URL}/api/start-work", json=work_data, timeout=10)
        if response.status_code != 200:
            print("❌ Start work failed!")
            return False
        print("✅ Work started")
        
        # Step 5: Get Results (This is where we see the actual code!)
        print("\n🔥 STEP 5: Get Agent Results")
        print("⏳ This will take 30-60 seconds as we send subtask to real Letta agents...")
        results_data = {
            "project_id": project_id,
            "agent_names": ["One"]  # Only test Agent One for faster testing
        }
        response = requests.post(f"{FLASK_BASE_URL}/api/get-results", json=results_data, timeout=120)
        if response.status_code != 200:
            print("❌ Get results failed!")
            return False
        
        results = response.json()
        print("✅ Subtask sent to agents")
        
        # Step 6: Retrieve the actual code
        print("\n🔥 STEP 6: Retrieve Generated Code")
        print("⏳ Retrieving actual code from Agent One...")
        retrieve_data = {
            "project_id": project_id,
            "agent_name": "One"
        }
        response = requests.post(f"{FLASK_BASE_URL}/api/retrieve-code", json=retrieve_data, timeout=30)
        if response.status_code != 200:
            print("❌ Retrieve code failed!")
            return False
        
        code_result = response.json()
        if not code_result.get('success'):
            print(f"❌ Code retrieval failed: {code_result.get('error')}")
            return False
        
        agent_name = code_result.get('agent_name', 'One')
        code = code_result.get('code', '')
        
        print(f"✅ Retrieved code from {agent_name}")
        print("\n" + "="*80)
        
        # Show the agent's code output
        print(f"\n🤖 AGENT: {agent_name}")
        print(f"📏 Code Length: {len(code)} characters")
        print("\n" + "-"*60)
        print("💻 CODE OUTPUT:")
        print("-"*60)
        
        # Show the full code
        print(code)
        print("-"*60)
        print(f"End of {agent_name}'s code\n")
        
        print("="*80)
        print("🎉 Code output demo completed!")
        print("\n💡 Note: This shows REAL output from Agent One (Sarcastic, clean code with humor)")
        print("   • To test all agents, change agent_names to ['One', 'Two', 'Three', 'Four']")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

if __name__ == "__main__":
    success = demo_code_outputs()
    sys.exit(0 if success else 1)
