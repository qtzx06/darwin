#!/usr/bin/env python3
"""
Setup 4 fullstack agents with different personalities that can communicate!
"""
import os
import asyncio
from dotenv import load_dotenv
from letta_client import Letta

load_dotenv()

async def setup_personality_agents():
    print("🔥 Setting up PERSONALITY-DRIVEN fullstack agents...")
    
    api_token = os.getenv("LETTA_API_TOKEN")
    project_slug = "default-project"
    
    if not api_token:
        print("❌ Missing API token in .env file")
        return
    
    client = Letta(token=api_token, project=project_slug)
    
    # Create shared identity for all agents to collaborate
    print("🤝 Creating shared identity for agent collaboration...")
    try:
        shared_identity = client.identities.create(
            identifier_key="dev_team_alpha",
            name="Dev Team Alpha",
            identity_type="org"
        )
        print(f"✅ Created shared identity: {shared_identity.id}")
    except Exception as e:
        print(f"⚠️  Identity might already exist: {e}")
        # Try to get existing identity
        identities = client.identities.list()
        shared_identity = next((i for i in identities if i.identifier_key == "dev_team_alpha"), None)
        if not shared_identity:
            print("❌ Could not create or find shared identity")
            return
    
    # Create shared memory block for agent communication
    print("💬 Creating shared communication block...")
    try:
        comm_block = client.blocks.create(
            value="Welcome to the dev team chat! 🚀",
            label="Team Chat"
        )
        print(f"✅ Created communication block: {comm_block.id}")
    except Exception as e:
        print(f"⚠️  Block might already exist: {e}")
        # Try to get existing block
        blocks = client.blocks.list()
        comm_block = next((b for b in blocks if b.label == "Team Chat"), None)
        if not comm_block:
            print("❌ Could not create or find communication block")
            return
    
    # Agent personalities and configurations
    agents_config = [
        {
            "name": "Alex The Hacker",
            "description": "The funny, sarcastic fullstack developer who loves memes and writes clean code with lots of comments",
            "personality": "Sarcastic, funny, loves memes, writes clean code with humor in comments",
            "coding_style": "Uses emojis in comments, writes clean functions, loves TypeScript, always includes error handling"
        },
        {
            "name": "Dr Sarah The Nerd",
            "description": "The super technical, perfectionist fullstack developer who loves documentation and over-engineering",
            "personality": "Technical perfectionist, loves documentation, over-engineers everything, very methodical",
            "coding_style": "Extensive documentation, type safety everywhere, comprehensive error handling, follows all best practices"
        },
        {
            "name": "Jake The Speed Demon",
            "description": "The fast, aggressive fullstack developer who ships code quickly and loves performance optimization",
            "personality": "Fast-paced, aggressive, loves performance, ships quickly, competitive",
            "coding_style": "Optimized code, minimal comments, focuses on performance, uses latest frameworks"
        },
        {
            "name": "Maya The Artist",
            "description": "The creative, design-focused fullstack developer who loves beautiful UI and user experience",
            "personality": "Creative, design-focused, loves beautiful UI, user-centric, artistic",
            "coding_style": "Beautiful, readable code, focuses on UX, loves CSS/design systems, clean architecture"
        }
    ]
    
    agent_ids = []
    
    try:
        for i, agent_config in enumerate(agents_config):
            print(f"\n🎭 Creating {agent_config['name']}...")
            
            # Create agent with personality
            agent = client.agents.create(
                name=agent_config['name'],
                description=agent_config['description']
            )
            
            agent_id = agent.id
            agent_ids.append(agent_id)
            
            # Associate agent with shared identity
            client.agents.modify(
                agent_id=agent_id,
                identity_ids=[shared_identity.id]
            )
            
            # Attach communication block to agent
            client.agents.blocks.attach(
                agent_id=agent_id,
                block_id=comm_block.id
            )
            
            print(f"✅ Created {agent_config['name']}: {agent_id}")
            print(f"   Personality: {agent_config['personality']}")
            print(f"   Coding Style: {agent_config['coding_style']}")
        
        # Create a group for all agents to communicate
        print(f"\n👥 Creating dev team group...")
        try:
            group = client.groups.create(
                name="Dev Team Alpha",
                description="The main development team for collaborative coding"
            )
            print(f"✅ Created group: {group.id}")
            
            # Add all agents to the group
            for agent_id in agent_ids:
                client.groups.attach_block_to_group(
                    group_id=group.id,
                    block_id=comm_block.id
                )
            print("✅ Added communication block to group")
            
        except Exception as e:
            print(f"⚠️  Group creation issue: {e}")
        
        # Update .env file with new agent IDs
        env_content = f"""LETTA_API_TOKEN={api_token}
LETTA_PROJECT_ID=1a5c9e14-14bc-4c57-962c-14659a595710
LETTA_PROJECT_SLUG={project_slug}

# Personality-Driven Fullstack Agents
LETTA_AGENT_ALEX={agent_ids[0]}
LETTA_AGENT_SARAH={agent_ids[1]}
LETTA_AGENT_JAKE={agent_ids[2]}
LETTA_AGENT_MAYA={agent_ids[3]}

# Shared Resources
LETTA_SHARED_IDENTITY={shared_identity.id}
LETTA_COMM_BLOCK={comm_block.id}
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print(f"\n🎉 ALL PERSONALITY AGENTS CREATED!")
        print(f"📝 Updated .env file with agent IDs")
        print(f"\n🚀 Now run: python3 main_personality.py")
        print(f"\n🎭 Your agents:")
        for i, agent_config in enumerate(agents_config):
            print(f"   • {agent_config['name']}: {agent_config['personality']}")
        
    except Exception as e:
        print(f"❌ Error creating agents: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(setup_personality_agents())
