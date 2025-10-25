#!/usr/bin/env python3
"""
Find your Letta projects and get the correct project ID
"""
import os
from dotenv import load_dotenv
from letta_client import Letta

load_dotenv()

def main():
    api_token = os.getenv("LETTA_API_TOKEN")
    
    if not api_token:
        print("❌ No LETTA_API_TOKEN found in .env file")
        return
    
    print("🔍 Finding your Letta projects...")
    
    try:
        # Create client without project ID first
        client = Letta(token=api_token)
        
        # List projects
        projects_response = client.projects.list()
        
        print(f"Response type: {type(projects_response)}")
        print(f"Response: {projects_response}")
        
        # Access the projects
        projects = projects_response.projects
        
        print(f"\n📋 Found {len(projects)} projects:")
        print("-" * 50)
        
        for i, project in enumerate(projects, 1):
            print(f"{i}. Project: {project.name}")
            print(f"   ID: {project.id}")
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
            
            print(f"\n📝 Updated .env file with correct project ID")
            print("\n🚀 Now run: python3 setup_agents.py")
            
        else:
            print("❌ No projects found. Create a project first at https://app.letta.com")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
