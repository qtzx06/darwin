#!/usr/bin/env python3
"""
Find the correct project ID
"""
import os
from dotenv import load_dotenv
from letta_client import Letta

load_dotenv()

def find_projects():
    print("🔍 Finding your Letta projects...")
    
    api_token = os.getenv("LETTA_API_TOKEN")
    
    if not api_token:
        print("❌ Missing API token in .env file")
        return
    
    try:
        client = Letta(token=api_token)
        
        # List projects
        response = client.projects.list()
        
        # Access the projects list
        projects = response.projects
        
        print(f"\n📋 Found {len(projects)} projects:")
        for i, project in enumerate(projects):
            print(f"{i+1}. {project.name} (ID: {project.id})")
            print(f"   Slug: {project.slug}")
            print()
        
        if projects:
            # Use the first project
            project = projects[0]
            print(f"✅ Using project: {project.name}")
            print(f"   Project ID: {project.id}")
            print(f"   Project Slug: {project.slug}")
            
            # Update .env file
            env_content = f"""LETTA_API_TOKEN={api_token}
LETTA_PROJECT_ID={project.id}

# Agent IDs (these will be created when you run the setup)
LETTA_CODING_AGENT_ID_1=
LETTA_CODING_AGENT_ID_2=
LETTA_CODING_AGENT_ID_3=
LETTA_CODING_AGENT_ID_4=
LETTA_COMMENTATOR_AGENT_ID=
"""
            
            with open('.env', 'w') as f:
                f.write(env_content)
            
            print("📝 Updated .env file with correct project ID")
            print("\nNow run: python3 setup_agents.py")
        else:
            print("❌ No projects found. Create a project first at https://letta.ai")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    find_projects()
