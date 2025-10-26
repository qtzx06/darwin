#!/usr/bin/env python3
"""
Delete all current agents from Letta
"""
import os
import requests
from dotenv import load_dotenv, set_key

load_dotenv()

API_TOKEN = os.getenv("LETTA_API_TOKEN")
BASE_URL = "https://api.letta.com"
ENV_FILE = ".env"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# Agent IDs to delete
agent_ids = [
    ("LETTA_AGENT_1", os.getenv("LETTA_AGENT_1")),
    ("LETTA_AGENT_2", os.getenv("LETTA_AGENT_2")),
    ("LETTA_AGENT_3", os.getenv("LETTA_AGENT_3")),
    ("LETTA_AGENT_4", os.getenv("LETTA_AGENT_4")),
    ("LETTA_ORCHESTRATOR_AGENT_ID", os.getenv("LETTA_ORCHESTRATOR_AGENT_ID")),
    ("LETTA_COMMENTATOR_AGENT_ID", os.getenv("LETTA_COMMENTATOR_AGENT_ID"))
]

print("="*70)
print("🗑️  DELETING ALL AGENTS FROM LETTA")
print("="*70)
print()

deleted_count = 0
for env_name, agent_id in agent_ids:
    if not agent_id:
        print(f"⚠️  {env_name}: No agent ID found, skipping")
        continue
    
    print(f"Deleting {env_name} ({agent_id[:8]}...)...")
    
    try:
        url = f"{BASE_URL}/v1/agents/{agent_id}"
        response = requests.delete(url, headers=headers)
        
        if response.status_code in [200, 204]:
            print(f"  ✅ Deleted successfully")
            deleted_count += 1
            # Clear from .env
            set_key(ENV_FILE, env_name, "")
            print(f"  ✅ Cleared from .env")
        elif response.status_code == 404:
            print(f"  ⚠️  Agent not found (already deleted?)")
            # Still clear from .env
            set_key(ENV_FILE, env_name, "")
            print(f"  ✅ Cleared from .env")
        else:
            print(f"  ❌ Failed: {response.status_code}")
            print(f"     Response: {response.text[:200]}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

print()
print("="*70)
print(f"✅ DELETION COMPLETE - Deleted {deleted_count} agent(s)")
print("="*70)
print()
print("Next steps:")
print("1. Run: python setup_agents.py")
print("   (This will create fresh agents)")

