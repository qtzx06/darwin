#!/usr/bin/env python3
"""
Quick setup script to create Letta agents and update .env file
"""
import os
import asyncio
from dotenv import load_dotenv
from letta_client import Letta

load_dotenv()

async def setup_agents():
    print("🚀 Setting up Letta agents...")
    
    api_token = os.getenv("LETTA_API_TOKEN")
    project_id = os.getenv("LETTA_PROJECT_ID")
    
    if not api_token or not project_id:
        print("❌ Missing API token or project ID in .env file")
        return
    
    # Use project slug instead of ID
    client = Letta(token=api_token, project="default-project")
    
    # Agent configurations
    agents = [
        {"name": "Frontend Specialist", "description": "UI/UX Design & Frontend Development"},
        {"name": "Backend Architect", "description": "System Design & Data Management"},
        {"name": "DevOps Engineer", "description": "Infrastructure & Deployment"},
        {"name": "Full-Stack Developer", "description": "Versatile Problem Solving"},
        {"name": "Project Narrator", "description": "Progress Monitoring & Commentary"}
    ]
    
    agent_ids = []
    
    try:
        for i, agent in enumerate(agents):
            print(f"Creating {agent['name']}...")
            
            # Create agent
            response = client.agents.create(
                name=agent['name'],
                description=agent['description']
            )
            
            agent_id = response.id
            agent_ids.append(agent_id)
            print(f"✅ Created {agent['name']}: {agent_id}")
        
        # Update .env file
        env_content = f"""LETTA_API_TOKEN={api_token}
LETTA_PROJECT_ID={project_id}

# Agent IDs
LETTA_CODING_AGENT_ID_1={agent_ids[0]}
LETTA_CODING_AGENT_ID_2={agent_ids[1]}
LETTA_CODING_AGENT_ID_3={agent_ids[2]}
LETTA_CODING_AGENT_ID_4={agent_ids[3]}
LETTA_COMMENTATOR_AGENT_ID={agent_ids[4]}
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("\n🎉 All agents created successfully!")
        print("📝 Updated .env file with agent IDs")
        print("\nNow you can run: python3 main.py")
        
    except Exception as e:
        print(f"❌ Error creating agents: {e}")
        print("Make sure your API token and project ID are correct")

if __name__ == "__main__":
    asyncio.run(setup_agents())
