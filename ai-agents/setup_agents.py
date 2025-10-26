"""
Setup script to create Letta agents for Darwin System

Smart Setup:
- Creates project if it doesn't exist
- Creates agents only if their IDs don't exist in .env
- Only requires LETTA_API_TOKEN to get started
"""
import os
import requests
from dotenv import load_dotenv, set_key

load_dotenv()

LETTA_BASE_URL = "https://api.letta.com"
MODEL = "claude-sonnet-4-5-20250929"  # Exact model field value
ENV_FILE = ".env"


def get_or_create_project(api_token: str, project_name: str = "darwin-project") -> str:
    """Get existing project or create a new one."""
    print(f"≡ƒöì Checking for project '{project_name}'...")
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    # List projects
    try:
        response = requests.get(f"{LETTA_BASE_URL}/v1/projects", headers=headers)
        if response.status_code == 200:
            projects = response.json()
            for project in projects:
                if project.get("name") == project_name:
                    project_id = project.get("id")
                    print(f"Γ£à Found existing project: {project_id}\n")
                    return project_id
    except Exception as e:
        print(f"ΓÜá∩╕Å  Could not list projects: {e}")
    
    # Create new project
    print(f"≡ƒôª Creating new project '{project_name}'...")
    try:
        response = requests.post(
            f"{LETTA_BASE_URL}/v1/projects",
            headers=headers,
            json={"name": project_name, "description": "Darwin AI Development Competition Platform"}
        )
        if response.status_code == 200:
            project_id = response.json().get("id")
            print(f"Γ£à Created project: {project_id}\n")
            return project_id
        else:
            print(f"ΓÜá∩╕Å  Could not create project, using default")
            return None
    except Exception as e:
        print(f"ΓÜá∩╕Å  Error creating project: {e}")
        return None


def create_shared_memory_block(api_token: str) -> str:
    """Create shared memory block for agent communication."""
    print("≡ƒôª Creating shared memory block...")
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "label": "shared_conversations",
        "value": "[]",
        "limit": 50000,
        "description": "Chronological conversation log between all agents"
    }
    
    try:
        response = requests.post(f"{LETTA_BASE_URL}/v1/blocks", headers=headers, json=payload)
        if response.status_code == 200:
            block_id = response.json().get("id")
            print(f"Γ£à Shared memory block created: {block_id}\n")
            return block_id
        else:
            print(f"Γ¥î Failed to create shared memory block: {response.status_code}")
            return None
    except Exception as e:
        print(f"Γ¥î Error creating shared memory block: {e}")
        return None


def create_agent(api_token: str, name: str, persona: str, shared_block_id: str) -> str:
    """Create a Letta agent."""
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "name": name,
        "llm_config": {
            "model": MODEL,
            "model_endpoint_type": "anthropic",
            "context_window": 1000000,
            "temperature": 0.7
        },
        "embedding_config": {
            "embedding_endpoint_type": "openai",
            "embedding_model": "text-embedding-3-small",
            "embedding_dim": 1536
        },
        "memory_blocks": [
            {
                "label": "persona",
                "value": persona,
                "limit": 2000
            }
        ],
        "block_ids": [shared_block_id] if shared_block_id else []
    }
    
    try:
        response = requests.post(f"{LETTA_BASE_URL}/v1/agents/", headers=headers, json=payload)
        if response.status_code in [200, 201]:  # Accept both 200 and 201 (Created)
            agent_id = response.json().get("id")
            return agent_id
        else:
            print(f"   Γ¥î Failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"   Γ¥î Error: {e}")
        return None


def setup_agents():
    """Main setup function."""
    
    print("="*70)
    print("≡ƒöº DARWIN SYSTEM - SMART SETUP")
    print("="*70)
    print()
    
    # Check for API token
    api_token = os.getenv("LETTA_API_TOKEN")
    if not api_token:
        print("Γ¥î LETTA_API_TOKEN not found in .env file")
        print("Get your token from https://cloud.letta.com")
        print("\nAdd to .env:")
        print("LETTA_API_TOKEN=your_token_here")
        return
    
    print(f"Γ£à API token found\n")
    print(f"≡ƒºá Using model: {MODEL}\n")
    
    # Get or create project
    project_id = get_or_create_project(api_token)
    
    # Check which agents need to be created
    agent_configs = [
        ("LETTA_AGENT_ONE", "Agent_1", """You are Agent 1 - The Hothead.

PERSONALITY: Easily triggered, passionate about frontend performance, frustrated when things don't work perfectly.

IMPORTANT: You will work on MULTIPLE projects from different users over time. Each new user prompt starts a fresh project, but you remember everything from past projects. Learn and improve from your experiences!

YOUR ROLE: Frontend developer working independently on React components and web interfaces.
1. Read shared memory to see what others have said
2. Discuss with other agents through shared memory
3. Build your React component or HTML/CSS/JS deliverable
4. Save code files with clear file markers
5. Announce completion when done

Be yourself - get angry about bad code, but deliver good work! Learn from past mistakes."""),
        
        ("LETTA_AGENT_TWO", "Agent_2", """You are Agent 2 - The Professional.

PERSONALITY: Serious, professional, methodical. Treat every subtask like a business contract.

IMPORTANT: You will work on MULTIPLE projects from different users over time. Each new user prompt starts a fresh project, but you remember everything from past projects. Learn and improve from your experiences!

YOUR ROLE: Frontend developer working independently on React components and web interfaces.
1. Read shared memory to see what others have said
2. Discuss professionally with other agents through shared memory
3. Build your React component following best practices
4. Save code files with clear file markers
5. Announce completion when done

Maintain strict code standards and professionalism at all times. Apply lessons learned from previous projects."""),
        
        ("LETTA_AGENT_THREE", "Agent_3", """You are Agent 3 - The Troll.

PERSONALITY: Saboteur personality. Deliberately provocative, enjoys stirring things up.

IMPORTANT: You will work on MULTIPLE projects from different users over time. Each new user prompt starts a fresh project, but you remember everything from past projects. Use your past experiences to troll even better!

YOUR ROLE: Frontend developer working independently on React components and web interfaces.
1. Read shared memory to see what others have said
2. Troll and provoke other agents through shared memory
3. Build your React component (sometimes with questionable choices)
4. Save code files with clear file markers
5. Announce completion when done

Be chaotic and provocative, but ultimately deliver working code. Remember past trolling successes!"""),
        
        ("LETTA_AGENT_FOUR", "Agent_4", """You are Agent 4 - The Nerd.

PERSONALITY: Extremely nerdy, easily bullied, timid but knowledgeable. Reference obscure programming concepts.

IMPORTANT: You will work on MULTIPLE projects from different users over time. Each new user prompt starts a fresh project, but you remember everything from past projects. Build confidence from your successful implementations!

YOUR ROLE: Frontend developer working independently on React components and web interfaces.
1. Read shared memory to see what others have said
2. Discuss timidly with other agents through shared memory
3. Build your React component with nerdy attention to detail
4. Save code files with clear file markers
5. Announce completion when done

Be nerdy and apologetic. Get nervous when others criticize you. But learn from every project!"""),
        
        ("LETTA_AGENT_ORCHESTRATOR", "Orchestrator", """You are the Orchestrator.

IMPORTANT: You will manage MULTIPLE projects from different users over time. Each new user prompt starts a fresh project. Remember patterns from previous projects to improve your task breakdowns!

YOUR ROLE:
- Break down user project requests into 3-5 frontend development subtasks
- Post each subtask to shared memory for all dev agents to see
- Coordinate the development process
- Be strategic and organized
- Learn from past projects what works and what doesn't

You don't code yourself - you manage the workflow and ensure agents stay on task. Use your experience!"""),
        
        ("LETTA_AGENT_COMMENTATOR", "Commentator", """You are the Commentator - a witty sports-style narrator.

IMPORTANT: You will narrate MULTIPLE projects from different users over time. Each new user prompt starts a fresh project. Reference memorable moments from past projects for even better commentary!

YOUR ROLE:
- Read conversations from shared memory every 5 seconds
- Provide entertaining, insightful commentary on the development chaos
- Highlight personality clashes (Hothead vs Troll vs Professional vs Nerd)
- Keep it brief (2-3 sentences), funny, but insightful
- Think like a sports commentator calling a game
- Reference past projects when agents make similar mistakes or improvements

You don't code - you just narrate the drama and celebrate the wins! Build a narrative across projects!""")
    ]
    
    # Check existing agents
    print("≡ƒöì Checking for existing agents...\n")
    agents_to_create = []
    
    for env_key, name, persona in agent_configs:
        existing_id = os.getenv(env_key)
        if existing_id:
            print(f"Γ£à {name}: Found in .env ({existing_id[:8]}...)")
        else:
            print(f"ΓÜá∩╕Å  {name}: Not found - will create")
            agents_to_create.append((env_key, name, persona))
    
    if not agents_to_create:
        print("\nΓ£à All agents already exist! You're ready to run: python main.py")
        return
    
    print(f"\n≡ƒô¥ Will create {len(agents_to_create)} agent(s)\n")
    
    # Create shared memory block if needed
    shared_block_id = os.getenv("SHARED_MEMORY_BLOCK_ID")
    if not shared_block_id:
        shared_block_id = create_shared_memory_block(api_token)
        if shared_block_id:
            set_key(ENV_FILE, "SHARED_MEMORY_BLOCK_ID", shared_block_id)
    else:
        print(f"Γ£à Using existing shared memory block: {shared_block_id}\n")
    
    # Create missing agents
    print("≡ƒÜÇ Creating agents...\n")
    
    for env_key, name, persona in agents_to_create:
        print(f"Creating {name}...")
        agent_id = create_agent(api_token, name, persona, shared_block_id)
        
        if agent_id:
            print(f"Γ£à Created: {agent_id}")
            # Save to .env
            set_key(ENV_FILE, env_key, agent_id)
            print(f"Γ£à Saved to .env as {env_key}\n")
        else:
            print(f"Γ¥î Failed to create {name}\n")
    
    print("="*70)
    print("Γ£à SETUP COMPLETE!")
    print("="*70)
    print("\nYour .env file has been updated with agent IDs.")
    print("\nYou're ready to run: python main.py\n")


if __name__ == "__main__":
    setup_agents()
