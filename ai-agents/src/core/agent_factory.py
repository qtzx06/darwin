"""
Agent Factory - Creates fresh Letta agent instances for each new project.
"""

import os
import uuid
from typing import List, Dict, Any
from letta_client import Letta
from dataclasses import dataclass

@dataclass
class AgentConfig:
    """Configuration for a fresh agent."""
    agent_id: str
    name: str
    personality: str
    coding_style: str
    description: str

class AgentFactory:
    """Factory for creating fresh Letta agent instances."""
    
    def __init__(self, client: Letta):
        self.client = client
        self.agent_configs = [
            {
                "name": "One",
                "personality": "Sarcastic, funny, loves memes, writes clean code with humor in comments",
                "coding_style": "Uses emojis in comments, writes clean functions, loves TypeScript, always includes error handling",
                "description": "Fullstack developer who brings humor and sarcasm to code while maintaining high quality"
            },
            {
                "name": "Two",
                "personality": "Technical perfectionist, loves documentation, over-engineers everything, very methodical",
                "coding_style": "Extensive documentation, type safety everywhere, comprehensive error handling, follows all best practices",
                "description": "Fullstack developer obsessed with type safety, documentation, and enterprise-grade code"
            },
            {
                "name": "Three",
                "personality": "Fast-paced, aggressive, loves performance, ships quickly, competitive",
                "coding_style": "Optimized code, minimal comments, focuses on performance, uses latest frameworks",
                "description": "Fullstack developer who prioritizes speed and performance in everything they build"
            },
            {
                "name": "Four",
                "personality": "Creative, design-focused, loves beautiful UI, user-centric, artistic",
                "coding_style": "Beautiful, readable code, focuses on UX, loves CSS/design systems, clean architecture",
                "description": "Fullstack developer who creates beautiful, user-focused applications with artistic flair"
            }
        ]
    
    async def create_fresh_agents(self, project_id: str) -> List[Dict[str, Any]]:
        """Reuse existing agents and clear their context for a new project."""
        print(f"🏭 Reusing existing agents for project: {project_id}")
        
        agents = []
        
        for config in self.agent_configs:
            # Try to reuse existing agent from environment variables
            existing_agent_id = self._get_existing_agent_id(config["name"])
            
            if existing_agent_id:
                print(f"♻️ Reusing existing agent: {config['name']} ({existing_agent_id})")
                
                # Clear agent context for new project
                await self._clear_agent_context(existing_agent_id, project_id)
                
                agent_config = AgentConfig(
                    agent_id=existing_agent_id,
                    name=config["name"],
                    personality=config["personality"],
                    coding_style=config["coding_style"],
                    description=config["description"]
                )
                
                agents.append({
                    "config": agent_config,
                    "letta_agent": {
                        "agent_id": existing_agent_id,
                        "name": config["name"],
                        "fresh_context": True  # Context was cleared
                    }
                })
                
                print(f"✅ Reused agent: {config['name']} ({existing_agent_id})")
            else:
                print(f"⚠️ No existing agent found for {config['name']}, skipping...")
                continue
        
        print(f"🎉 Reused {len(agents)} agents for project {project_id}")
        return agents
    
    def _get_existing_agent_id(self, agent_name: str) -> str:
        """Get existing agent ID from environment variables."""
        agent_id_mapping = {
            "One": os.getenv("LETTA_AGENT_ONE"),
            "Two": os.getenv("LETTA_AGENT_TWO"),
            "Three": os.getenv("LETTA_AGENT_THREE"),
            "Four": os.getenv("LETTA_AGENT_FOUR")
        }
        return agent_id_mapping.get(agent_name)
    
    async def _clear_agent_context(self, agent_id: str, project_id: str):
        """Clear agent context for new project."""
        try:
            # Send a context clearing message to the agent
            clear_message = f"""
CONTEXT RESET for new project: {project_id}

You are starting fresh on a new project. Clear your previous context and prepare for new work.

Your personality and coding style remain the same, but forget any previous project details.
"""
            
            # Send the clearing message
            response = self.client.agents.messages.create(
                agent_id=agent_id,
                messages=[{"role": "user", "content": clear_message}]
            )
            
            print(f"🧹 Cleared context for agent {agent_id}")
            
        except Exception as e:
            print(f"⚠️ Context clearing failed for agent {agent_id}: {e}")
            print(f"   Continuing without context clearing...")
    
    async def _create_letta_agent(self, agent_id: str, name: str, description: str):
        """Create a fresh Letta agent instance."""
        try:
            # Create a fresh Letta agent with proper memory blocks
            letta_agent = self.client.agents.create(
                memory_blocks=[
                    {
                        "label": "persona",
                        "value": f"I am {name}, a fullstack developer. {description}"
                    },
                    {
                        "label": "project",
                        "value": "I am working on a competitive coding project with other agents.",
                        "description": "Stores current project context and requirements"
                    }
                ],
                tools=["web_search", "run_code"],
                model="openai/gpt-4o-mini",
                embedding="openai/text-embedding-3-small"
            )
            
            print(f"✅ Created fresh Letta agent: {name} (ID: {letta_agent.id})")
            
            return {
                "agent_id": letta_agent.id,
                "name": name,
                "fresh_context": True,
                "letta_agent": letta_agent
            }
            
        except Exception as e:
            print(f"❌ Failed to create Letta agent {name}: {e}")
            # Fallback to existing agent IDs if creation fails
            agent_id_mapping = {
                "One": os.getenv("LETTA_AGENT_ONE"),
                "Two": os.getenv("LETTA_AGENT_TWO"),
                "Three": os.getenv("LETTA_AGENT_THREE"),
                "Four": os.getenv("LETTA_AGENT_FOUR")
            }
            
            existing_agent_id = agent_id_mapping.get(name)
            if not existing_agent_id:
                raise ValueError(f"No existing Letta agent ID found for {name}")
            
            print(f"⚠️ Using existing agent ID for {name}: {existing_agent_id}")
            
            return {
                "agent_id": existing_agent_id,
                "name": name,
                "fresh_context": False,
                "letta_agent": None
            }
    
    def get_agent_configs(self) -> List[Dict[str, Any]]:
        """Get the agent configuration templates."""
        return self.agent_configs.copy()
