#!/usr/bin/env python3
"""
Check available models
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("LETTA_API_TOKEN")
BASE_URL = "https://api.letta.com"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

print("Fetching available models...")
url = f"{BASE_URL}/v1/models"

try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nAvailable models:")
        for model in data:
            print(f"  - {model}")
    else:
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")
