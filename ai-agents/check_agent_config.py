#!/usr/bin/env python3
"""
Check agent configuration
"""
import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

API_TOKEN = os.getenv("LETTA_API_TOKEN")
AGENT_ID = os.getenv("LETTA_AGENT_1")
BASE_URL = "https://api.letta.com"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

print(f"Checking Agent 1: {AGENT_ID}")
print()

url = f"{BASE_URL}/v1/agents/{AGENT_ID}"

try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n=== AGENT CONFIGURATION ===\n")
        print(f"Name: {data.get('name')}")
        print(f"\nLLM Config:")
        llm_config = data.get('llm_config', {})
        print(json.dumps(llm_config, indent=2))
        print(f"\nEmbedding Config:")
        embedding_config = data.get('embedding_config', {})
        print(json.dumps(embedding_config, indent=2))
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")
