"""
Main Competitive Simulator - Competitive fullstack agent collaboration system.
"""

import asyncio
import os
import time
from pathlib import Path
from typing import List, Dict, Any

from config.agents_config import LettaConfig
from src.core.agent_factory import AgentFactory
from src.core.competitive_workflow import CompetitiveWorkflow
from src.core.user_interaction import UserInteractionManager
from src.core.shared_memory import SharedMemory
from src.core.message_system import MessageBroker
from src.artifacts.artifact_manager import ArtifactManager
from src.agents.commentator_agent import CommentatorAgent
from src.agents.orchestrator_agent import OrchestrationAgent
from src.core.logger import PMSimulatorLogger

class CompetitivePMSimulator:
    """Main simulator for competitive agent collaboration."""
    
    def __init__(self):
        # Initialize configuration
        self.config = LettaConfig()
        self.client = self.config.client
        
        # Initialize core systems
        self.shared_memory = SharedMemory()
        self.message_broker = MessageBroker()
        self.artifact_manager = ArtifactManager()
        self.logger = PMSimulatorLogger()
        self.user_interaction = UserInteractionManager()
        
        # Initialize agent factory
        self.agent_factory = AgentFactory(self.client)
        
        # Initialize workflow
        self.workflow = CompetitiveWorkflow(
            self.artifact_manager,
            self.shared_memory,
            self.message_broker,
            self.logger,
            self.client
        )
        
        self.agents = []
        self.current_project_id = None
    
    async def _create_commentator_agent(self):
        """Reuse existing commentator agent and clear context."""
        try:
            # Try to reuse existing commentator agent
            existing_id = os.getenv("LETTA_AGENT_COMMENTATOR")
            
            if existing_id:
                print(f"♻️ Reusing existing Commentator agent: {existing_id}")
                
                # Clear context for new project
                await self._clear_agent_context(existing_id, "competitive_project")
                
                return {
                    "agent_id": existing_id,
                    "name": "Commentator",
                    "letta_agent": None
                }
            else:
                print("⚠️ No existing Commentator agent found, creating new one...")
                # Fallback to creating new agent
                letta_agent = self.client.agents.create(
                    memory_blocks=[
                        {
                            "label": "persona",
                            "value": "I am the Commentator, a project manager who observes and narrates the competitive coding process. I analyze different approaches, explain why winners won, and provide learning insights to the team."
                        },
                        {
                            "label": "project",
                            "value": "I am observing a competitive coding project where 4 agents work on the same subtasks and compete for the best approach.",
                            "description": "Stores current project context and observation details"
                        }
                    ],
                    tools=["web_search", "run_code"],
                    model="openai/gpt-4o-mini",
                    embedding="openai/text-embedding-3-small"
                )
                
                print(f"✅ Created new Commentator agent: {letta_agent.id}")
                
                return {
                    "agent_id": letta_agent.id,
                    "name": "Commentator",
                    "letta_agent": letta_agent
                }
            
        except Exception as e:
            print(f"❌ Failed to create Commentator agent: {e}")
            # Fallback to environment variable
            fallback_id = os.getenv("LETTA_AGENT_COMMENTATOR", "commentator")
            print(f"⚠️ Using fallback Commentator ID: {fallback_id}")
            
            return {
                "agent_id": fallback_id,
                "name": "Commentator",
                "letta_agent": None
            }
    
    async def _create_orchestrator_agent(self):
        """Reuse existing orchestrator agent and clear context."""
        try:
            # Try to reuse existing orchestrator agent
            existing_id = os.getenv("LETTA_AGENT_ORCHESTRATOR")
            
            if existing_id:
                print(f"♻️ Reusing existing Orchestrator agent: {existing_id}")
                
                # Clear context for new project
                await self._clear_agent_context(existing_id, "competitive_project")
                
                return {
                    "agent_id": existing_id,
                    "name": "Orchestrator",
                    "letta_agent": None
                }
            else:
                print("⚠️ No existing Orchestrator agent found, creating new one...")
                # Fallback to creating new agent
                letta_agent = self.client.agents.create(
                    memory_blocks=[
                        {
                            "label": "persona",
                            "value": "I am the Orchestrator, a project manager who breaks down main tasks into subtasks and manages the competitive workflow. I analyze project requirements and create logical subtask sequences."
                        },
                        {
                            "label": "project",
                            "value": "I am managing a competitive coding project where I break down tasks into subtasks for 4 agents to work on competitively.",
                            "description": "Stores current project context and task breakdown details"
                        }
                    ],
                    tools=["web_search", "run_code"],
                    model="openai/gpt-4o-mini",
                    embedding="openai/text-embedding-3-small"
                )
                
                print(f"✅ Created new Orchestrator agent: {letta_agent.id}")
                
                return {
                    "agent_id": letta_agent.id,
                    "name": "Orchestrator",
                    "letta_agent": letta_agent
                }
            
        except Exception as e:
            print(f"❌ Failed to create Orchestrator agent: {e}")
            # Fallback to environment variable
            fallback_id = os.getenv("LETTA_AGENT_ORCHESTRATOR", "orchestrator")
            print(f"⚠️ Using fallback Orchestrator ID: {fallback_id}")
            
            return {
                "agent_id": fallback_id,
                "name": "Orchestrator",
                "letta_agent": None
            }
    
    async def _clear_agent_context(self, agent_id: str, project_id: str):
        """Clear agent context for new project."""
        try:
            # Send a context clearing message to the agent
            clear_message = f"""
CONTEXT RESET for new project: {project_id}

You are starting fresh on a new project. Clear your previous context and prepare for new work.

Your personality and role remain the same, but forget any previous project details.
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
    
    async def run_competitive_simulation(self, project_description: str):
        """Run the competitive simulation."""
        print(f"\n🚀 COMPETITIVE PM SIMULATOR")
        print(f"{'='*60}")
        print(f"Project: {project_description}")
        print(f"{'='*60}")
        
        try:
            # Step 1: Create commentator and orchestrator agents
            print(f"\n🏭 Creating Commentator and Orchestrator agents...")
            commentator_agent = await self._create_commentator_agent()
            orchestrator_agent = await self._create_orchestrator_agent()
            
            # Initialize commentator and orchestrator
            commentator = CommentatorAgent(
                self.client,
                commentator_agent["agent_id"],
                self.logger
            )
            
            orchestrator = OrchestrationAgent(
                self.client,
                orchestrator_agent["agent_id"],
                self.logger
            )
            
            # Step 2: Create fresh coding agents
            print(f"\n🏭 Creating fresh coding agents...")
            self.agents = await self.agent_factory.create_fresh_agents("competitive_project")
            
            if not self.agents:
                print("❌ Failed to create agents")
                return
            
            print(f"✅ Created {len(self.agents)} fresh agents")
            
            # Step 3: Run competitive workflow with orchestrator
            print(f"\n🎯 Starting competitive workflow...")
            self.current_project_id = await self.workflow.start_competitive_project(
                project_description,
                project_description,  # Pass main task to orchestrator
                self.agents,
                commentator,
                orchestrator
            )
            
            # Step 4: Display final results
            await self._display_final_results()
            
            print(f"\n🎉 Competitive simulation completed!")
            print(f"📁 Check artifacts/{self.current_project_id}/ for all results")
            
        except Exception as e:
            print(f"❌ Simulation error: {e}")
            import traceback
            traceback.print_exc()
    
    async def _display_final_results(self):
        """Display final results of the competitive simulation."""
        if not self.current_project_id:
            return
        
        # Get final artifacts
        final_artifacts = await self.artifact_manager.get_final_artifacts(self.current_project_id)
        
        # Display results
        await self.user_interaction.display_final_results(self.current_project_id, final_artifacts)
        
        # Display project structure
        self.user_interaction.display_project_structure(self.current_project_id)

async def main():
    """Main entry point."""
    print("🎭 Competitive Fullstack Agent PM Simulator")
    print("=" * 50)
    
    # Get project description from user
    project_description = input("Enter project description: ").strip()
    
    if not project_description:
        project_description = "Build a modern todo application with React and TypeScript"
        print(f"Using default project: {project_description}")
    
    # Create and run simulator
    simulator = CompetitivePMSimulator()
    await simulator.run_competitive_simulation(project_description)

if __name__ == "__main__":
    asyncio.run(main())
