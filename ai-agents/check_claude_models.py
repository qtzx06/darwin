#!/usr/bin/env python3
"""
Show Claude models with all their fields
"""
import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

API_TOKEN = os.getenv("LETTA_API_TOKEN")
BASE_URL = "https://api.letta.com"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

print("Fetching Claude models...\n")
url = f"{BASE_URL}/v1/models"

try:
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        for model_info in data:
            if 'claude' in model_info.get('model', '').lower():
                print("="*70)
                print(f"Model: {model_info.get('model')}")
                print(f"Display Name: {model_info.get('display_name')}")
                print(f"Handle: {model_info.get('handle')}")
                print(f"Tier: {model_info.get('tier')}")
                print(f"Provider: {model_info.get('provider_name')}")
                print()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"Error: {e}")
