#!/usr/bin/env python3
"""
Check account usage and limits
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

print("Checking account info...\n")

# Try to get user info
endpoints = [
    "/v1/user",
    "/v1/users/me",
    "/v1/account",
    "/v1/usage",
    "/v1/health"
]

for endpoint in endpoints:
    try:
        url = f"{BASE_URL}{endpoint}"
        response = requests.get(url, headers=headers)
        print(f"{endpoint}: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2))
        elif response.status_code != 404:
            print(f"  Response: {response.text[:200]}")
        print()
    except Exception as e:
        print(f"  Error: {e}\n")
