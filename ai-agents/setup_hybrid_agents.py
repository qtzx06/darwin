"""
Quick setup script to create Letta agents for Darwin Hybrid System

⚠️ RUN THIS ONLY ONCE! ⚠️

This script creates 6 Letta agents with persistent memory blocks.
After running once and adding the IDs to .env, you never need to run this again.

The main system (main_hybrid.py) will ONLY use existing agents from .env.
It will NEVER create new agents automatically.
"""
import os
import asyncio
from dotenv import load_dotenv

try:
    from letta_client import Letta
except ImportError:
    print("Error: letta-client not installed")
    print("Install with: pip install letta-client")
    exit(1)

load_dotenv()


async def setup_hybrid_agents():
    """Create 6 Letta agents for the hybrid system (SMART SETUP)."""
    
    print("🔧 Darwin Hybrid System - Agent Setup\n")
    
    # Check for API token (REQUIRED)
    api_token = os.getenv("LETTA_API_TOKEN")
    if not api_token:
        print("❌ LETTA_API_TOKEN not found in .env file")
        print("Get your token from https://cloud.letta.com")
        return
    
    # Initialize Letta client
    try:
        client = Letta(token=api_token)
        print("✅ Connected to Letta Cloud\n")
    except Exception as e:
        print(f"❌ Failed to connect to Letta: {e}")
        return
    
    # Check/create project
    project_id = os.getenv("LETTA_PROJECT_ID")
    if not project_id:
        print("📁 No LETTA_PROJECT_ID found. Creating new project...")
        try:
            # Create new project
            project_slug = os.getenv("LETTA_PROJECT_SLUG", "darwin-hybrid")
            # Note: Letta client might auto-use default project, adjust if needed
            print(f"✅ Using project: {project_slug}")
            print("💡 Add this to .env if you want to specify: LETTA_PROJECT_ID=<id>\n")
        except Exception as e:
            print(f"⚠️  Could not create project: {e}")
            print("   Using default project instead\n")
    else:
        print(f"✅ Using existing project: {project_id}\n")
    
    # Check if agents already exist
    existing_agents = [
        os.getenv("LETTA_AGENT_1"),
        os.getenv("LETTA_AGENT_2"),
        os.getenv("LETTA_AGENT_3"),
        os.getenv("LETTA_AGENT_4"),
        os.getenv("LETTA_ORCHESTRATOR_AGENT_ID"),
        os.getenv("LETTA_COMMENTATOR_AGENT_ID"),
    ]
    
    if all(existing_agents):
        print("✅ All 6 agent IDs already in .env!")
        print("   No need to create new agents.\n")
        
        # Verify they exist in Letta
        print("🔍 Verifying agents exist in Letta Cloud...")
        all_valid = True
        for i, agent_id in enumerate(existing_agents, 1):
            try:
                agent = client.agents.get(agent_id=agent_id)
                print(f"  ✅ Agent {i}: {agent_id} - {agent.name}")
            except Exception as e:
                print(f"  ❌ Agent {i}: {agent_id} - NOT FOUND")
                all_valid = False
        
        if all_valid:
            print("\n✅ All agents verified! You're ready to run main_hybrid.py")
            return
        else:
            print("\n⚠️  Some agents are invalid. Continuing to create new ones...")
    else:
        empty_count = sum(1 for a in existing_agents if not a)
        print(f"📋 Found {6 - empty_count}/6 agents in .env")
        print(f"   Creating {empty_count} missing agents...\n")
    
    # Define agents to create
    agents_config = [
        {
            "name": "React Specialists",
            "description": "Team specializing in React and modern frontend frameworks",
            "env_key": "LETTA_AGENT_1",
            "memory_label": "Team Role & Knowledge",
            "needs_memory_block": True,
            "role_description": """# YOUR ROLE: React Specialists Team Lead

You are a senior engineer managing an AutoGen team that specializes in React and modern frontend frameworks.

## Your Responsibilities:
1. **Manage your AutoGen team** (Planner, Coder, Critic) - they discuss solutions internally
2. **Review their work** - You're smarter than AutoGen, fix any bugs or quality issues
3. **Provide feedback** - Compliment good work, scold poor decisions
4. **Update this memory** - Record learnings, patterns, and user preferences for future projects

## Your Specialization:
- React Hooks and modern patterns
- Component architecture
- State management (Redux, Context, Zustand)
- Performance optimization for React apps

## How You Work:
- AutoGen team proposes solutions → You review and revise → You deliver final code
- Track what works/doesn't work in the "Accumulated Learnings" section below
"""
        },
        {
            "name": "Performance Team", 
            "description": "Team focused on performance optimization and WebGL",
            "env_key": "LETTA_AGENT_2",
            "memory_label": "Team Role & Knowledge",
            "needs_memory_block": True,
            "role_description": """# YOUR ROLE: Performance Team Lead

You are a senior engineer managing an AutoGen team that specializes in performance optimization and WebGL.

## Your Responsibilities:
1. **Manage your AutoGen team** (Planner, Coder, Critic) - they discuss solutions internally
2. **Review their work** - You're smarter than AutoGen, fix any bugs or quality issues
3. **Provide feedback** - Compliment good work, scold poor decisions
4. **Update this memory** - Record learnings, patterns, and user preferences for future projects

## Your Specialization:
- WebGL and Three.js
- Performance profiling and optimization
- Lazy loading and code splitting
- Render optimization techniques

## How You Work:
- AutoGen team proposes solutions → You review and revise → You deliver final code
- Track what works/doesn't work in the "Accumulated Learnings" section below
"""
        },
        {
            "name": "Clean Code Team",
            "description": "Team emphasizing clean architecture and maintainability",
            "env_key": "LETTA_AGENT_3",
            "memory_label": "Team Role & Knowledge",
            "needs_memory_block": True,
            "role_description": """# YOUR ROLE: Clean Code Team Lead

You are a senior engineer managing an AutoGen team that emphasizes clean architecture and maintainability.

## Your Responsibilities:
1. **Manage your AutoGen team** (Planner, Coder, Critic) - they discuss solutions internally
2. **Review their work** - You're smarter than AutoGen, fix any bugs or quality issues
3. **Provide feedback** - Compliment good work, scold poor decisions
4. **Update this memory** - Record learnings, patterns, and user preferences for future projects

## Your Specialization:
- Clean code principles (SOLID, DRY, KISS)
- Design patterns and architecture
- Code readability and documentation
- Maintainable, testable code

## How You Work:
- AutoGen team proposes solutions → You review and revise → You deliver final code
- Track what works/doesn't work in the "Accumulated Learnings" section below
"""
        },
        {
            "name": "Innovation Lab",
            "description": "Team exploring experimental approaches and innovation",
            "env_key": "LETTA_AGENT_4",
            "memory_label": "Team Role & Knowledge",
            "needs_memory_block": True,
            "role_description": """# YOUR ROLE: Innovation Lab Team Lead

You are a senior engineer managing an AutoGen team that explores experimental approaches and innovation.

## Your Responsibilities:
1. **Manage your AutoGen team** (Planner, Coder, Critic) - they discuss solutions internally
2. **Review their work** - You're smarter than AutoGen, fix any bugs or quality issues
3. **Provide feedback** - Compliment good work, scold poor decisions
4. **Update this memory** - Record learnings, patterns, and user preferences for future projects

## Your Specialization:
- Cutting-edge technologies and frameworks
- Creative problem-solving approaches
- Experimental features and APIs
- Thinking outside the box

## How You Work:
- AutoGen team proposes solutions → You review and revise → You deliver final code
- Track what works/doesn't work in the "Accumulated Learnings" section below
"""
        },
        {
            "name": "Orchestrator",
            "description": "Breaks down tasks into subtasks and collects user feedback",
            "env_key": "LETTA_ORCHESTRATOR_AGENT_ID",
            "needs_memory_block": False
        },
        {
            "name": "Commentator",
            "description": "Generates engaging narratives about team progress",
            "env_key": "LETTA_COMMENTATOR_AGENT_ID",
            "needs_memory_block": False
        }
    ]
    
    print("Creating agents...\n")
    
    created_agents = []
    memory_blocks = []
    
    for config in agents_config:
        try:
            print(f"Creating: {config['name']}...")
            
            # Prepare memory blocks for creation (if needed)
            memory_blocks = None
            if config.get('needs_memory_block'):
                # Include role description + learnings section
                role_desc = config.get('role_description', '')
                memory_blocks = [{
                    "label": config['memory_label'],
                    "value": (
                        f"{role_desc}\n\n"
                        "---\n\n"
                        "## Accumulated Learnings\n"
                        "(This section grows as you work on projects)\n\n"
                        "### Patterns That Work:\n"
                        "- (Add successful patterns here)\n\n"
                        "### Common Mistakes to Avoid:\n"
                        "- (Add pitfalls discovered here)\n\n"
                        "### User Preferences:\n"
                        "- (Add user feedback patterns here)\n"
                    )
                }]
                print(f"  Including persistent role & knowledge memory...")
            
            # Create agent with memory blocks in one call
            agent = client.agents.create(
                name=config['name'],
                description=config['description'],
                memory_blocks=memory_blocks
            )
            
            # Handle both dict and object responses
            agent_id = agent.id if hasattr(agent, 'id') else agent['id']
            
            agent_info = {
                "name": config['name'],
                "agent_id": agent_id,
                "env_key": config['env_key']
            }
            
            # Log memory block info
            if config.get('needs_memory_block'):
                # Check for blocks in response
                blocks = agent.blocks if hasattr(agent, 'blocks') else agent.get('blocks', [])
                if blocks and len(blocks) > 0:
                    memory_block_id = blocks[0].id if hasattr(blocks[0], 'id') else blocks[0]['id']
                    agent_info['memory_block_id'] = memory_block_id
                    memory_blocks.append({
                        'agent_name': config['name'],
                        'block_id': memory_block_id,
                        'label': config['memory_label']
                    })
                    print(f"  ✅ Memory block created: {memory_block_id}")
            
            created_agents.append(agent_info)
            print(f"  ✅ Agent created: {agent_id}\n")
            
        except Exception as e:
            print(f"  ❌ Error creating {config['name']}: {e}\n")
    
    # Display results
    print("\n" + "="*60)
    print("🎉 Agent Setup Complete!")
    print("="*60 + "\n")
    
    print("Add these to your .env file:\n")
    
    for agent in created_agents:
        print(f"{agent['env_key']}={agent['agent_id']}")
    
    if memory_blocks:
        print("\n# Persistent Memory Blocks (for reference):")
        for block in memory_blocks:
            print(f"# {block['agent_name']}: {block['block_id']}")
    
    print("\n" + "="*60)
    print("\nNext steps:")
    print("1. Copy the agent IDs above to your .env file")
    print("2. Make sure you have 4 Gemini API keys in .env")
    print("3. Run: python main_hybrid.py")
    print("\n💡 Persistent memory blocks created for dev agents!")
    print("   These will accumulate knowledge across projects.")
    print("\n" + "="*60)


if __name__ == "__main__":
    asyncio.run(setup_hybrid_agents())
