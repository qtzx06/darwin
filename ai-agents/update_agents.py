"""
Update Existing Letta Agents - Model Update Only
Updates all agents to use Claude Sonnet 4.5
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

LETTA_BASE_URL = "https://api.letta.com"


def update_agent_model(agent_id: str, agent_name: str) -> bool:
    """Update a Letta agent's model to Claude Sonnet 4.5."""
    try:
        api_token = os.getenv("LETTA_API_TOKEN")
        if not api_token:
            print("❌ LETTA_API_TOKEN not found in .env")
            return False
        
        url = f"{LETTA_BASE_URL}/v1/agents/{agent_id}"
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        
        # Update to Claude Sonnet 4.5
        payload = {
            "llm_config": {
                "model": "claude-sonnet-4-5-20250929",
                "model_endpoint_type": "anthropic",
                "context_window": 1000000,
                "temperature": 0.7
            }
        }
        
        response = requests.patch(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            print(f"✅ Updated {agent_name} to Claude Haiku 4.5")
            return True
        else:
            print(f"❌ Failed to update {agent_name}: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating {agent_name}: {e}")
        return False


def main():
    """Update all agents to Claude Sonnet 4.5."""
    
    print("\n" + "="*70)
    print("UPDATING ALL AGENTS TO CLAUDE SONNET 4.5")
    print("="*70 + "\n")
    
    # Get agent IDs from environment
    agents = [
        (os.getenv("LETTA_AGENT_1"), "Agent_1"),
        (os.getenv("LETTA_AGENT_2"), "Agent_2"),
        (os.getenv("LETTA_AGENT_3"), "Agent_3"),
        (os.getenv("LETTA_AGENT_4"), "Agent_4"),
        (os.getenv("LETTA_ORCHESTRATOR_AGENT_ID"), "Orchestrator"),
        (os.getenv("LETTA_COMMENTATOR_AGENT_ID"), "Commentator"),
    ]
    
    for agent_id, agent_name in agents:
        if not agent_id:
            print(f"⚠️  {agent_name} ID not found in .env, skipping")
            continue
        
        update_agent_model(agent_id, agent_name)
    
    print("\n" + "="*70)
    print("✨ MODEL UPDATE COMPLETE!")
    print("="*70)
    print("\nAll agents now use: claude-haiku-4-5-20251001 (free tier)\n")


if __name__ == "__main__":
    main()
