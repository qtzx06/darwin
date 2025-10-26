#!/usr/bin/env python3
"""
Darwin System - Main Entry Point
Pure Letta agents working on frontend development tasks
"""
import asyncio
import sys
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv
import requests

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.shared_memory import SharedMemory
from src.core.message_system import MessageBroker
from src.artifacts.artifact_manager import ArtifactManager
from src.agents.letta_dev_agent import LettaDevAgent
from src.agents.letta_orchestrator import LettaOrchestrator
from src.agents.letta_commentator import LettaCommentator

# Import artifact server
from artifact_server import start_background_server

try:
    from letta_client import Letta
except ImportError:
    self.console.print("Error: letta-client not installed. Install with: pip install letta-client")
    sys.exit(1)

load_dotenv()


class DarwinSystem:
    """Main system coordinator for Darwin architecture."""
    
    def __init__(self):
        self.console = Console()
        self.silent = True  # Only show commentator output
        
        # Initialize core systems
        self.shared_memory = SharedMemory()
        self.message_broker = MessageBroker()
        self.artifact_manager = ArtifactManager()
        
        # Letta client
        self.letta_client = None
        self.dev_agents = []
        self.orchestrator = None
        self.commentator = None
        
        # Start artifact server
        self.artifact_server_thread = None
        self._start_artifact_server()
    
    def _start_artifact_server(self):
        """Start the artifact viewer web server"""
        try:
            self.console.print("[cyan]🌐 Starting artifact server...[/cyan]")
            self.artifact_server_thread = start_background_server(port=5000)
            self.console.print("[green]✓ Artifact server running at http://localhost:5000[/green]\n")
        except Exception as e:
            self.console.print(f"[yellow]⚠️ Could not start artifact server: {e}[/yellow]\n")
    
    def _print(self, *args, **kwargs):
        """Conditional print based on silent flag."""
        if not self.silent:
            self.console.print(*args, **kwargs)
    
    def _setup_background_messaging(self):
        """Setup agent-to-agent messaging system."""
        # Get all dev agent IDs
        agent_ids = [agent.agent_id for agent in self.dev_agents]
        commentator_id = self.commentator.agent_id  # Fixed: use agent_id not letta_agent_id
        
        # Give each agent the list of other agents to message
        for agent in self.dev_agents:
            # Each agent can message all other agents (not itself)
            agent.other_agent_ids = [aid for aid in agent_ids if aid != agent.agent_id]
            agent.commentator_id = commentator_id
            
            # Start the messaging loop
            agent.start_background_messaging()

    
    def display_welcome(self):
        """Display welcome message."""
        welcome = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║         🧬 DARWIN - AI Frontend Development 🧬           ║
║                                                           ║
║     4 Letta Agents Compete on Frontend Tasks             ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

Architecture:
  • 4 Letta Dev Agents (distinct personalities)
    - Agent 1: The Hothead (easily triggered/angry)
    - Agent 2: The Professional (serious/formal)
    - Agent 3: The Troll (mischievous/saboteur)
    - Agent 4: The Nerd (smart but easily bullied)
  • 1 Orchestrator Agent (breaks down tasks, posts subtasks)
  • 1 Commentator Agent (live commentary every 5 seconds)
  • Shared Memory (all agents communicate chronologically)

Workflow:
  1. You provide a project goal
  2. Orchestrator breaks it into subtasks
  3. 4 agents work independently, chatting in shared memory
  4. Commentator narrates the drama live
  5. You give feedback after each subtask
  6. Repeat until project complete!

All agents use Claude Sonnet 4.5 🧠
"""
        self.console.print(Panel(welcome, border_style="cyan", title="🚀 Welcome"))
    
    async def initialize(self) -> bool:
        """Initialize all agents."""
        self.console.print("\n[cyan]Initializing Darwin System...[/cyan]")
        
        # Check for required API keys
        if not os.getenv("LETTA_API_TOKEN"):
            self.console.print("[red]❌ LETTA_API_TOKEN not set in .env file[/red]")
            return False
        
        try:
            # Initialize Letta client
            self.letta_client = Letta(
                token=os.getenv("LETTA_API_TOKEN"),
                project="default-project"
            )
            self.console.print("[green]✓[/green] Letta client initialized")
            
            # Get agent IDs from environment
            dev_agent_ids = [
                os.getenv("LETTA_AGENT_1"),
                os.getenv("LETTA_AGENT_2"),
                os.getenv("LETTA_AGENT_3"),
                os.getenv("LETTA_AGENT_4"),
            ]
            
            orchestrator_id = os.getenv("LETTA_ORCHESTRATOR_AGENT_ID")
            commentator_id = os.getenv("LETTA_COMMENTATOR_AGENT_ID")
            
            # Validate agent IDs
            if not all(dev_agent_ids):
                self.console.print("[red]❌ Missing dev agent IDs in .env[/red]")
                self.console.print("[yellow]Required: LETTA_AGENT_1 through LETTA_AGENT_4[/yellow]")
                self.console.print("[yellow]Run 'python setup_hybrid_agents.py' to create agents first[/yellow]")
                return False
            
            if not orchestrator_id:
                self.console.print("[red]❌ LETTA_ORCHESTRATOR_AGENT_ID not set in .env[/red]")
                self.console.print("[yellow]Run 'python setup_hybrid_agents.py' to create agents first[/yellow]")
                return False
            
            if not commentator_id:
                self.console.print("[red]❌ LETTA_COMMENTATOR_AGENT_ID not set in .env[/red]")
                self.console.print("[yellow]Run 'python setup_hybrid_agents.py' to create agents first[/yellow]")
                return False
            
            # Agent personas
            personas = [
                "The Hothead - Easily triggered and gets angry quickly. Passionate about frontend performance but frustrated when things don't work perfectly.",
                "The Professional - Serious, professional, and methodical. Treats every subtask like a business contract.",
                "The Troll - Mischievous and enjoys sabotaging or adding hidden 'features' to their code. Makes sarcastic comments.",
                "The Nerd - Extremely nerdy and knowledgeable but easily bullied by other agents. Timid and apologetic."
            ]
            
            # Initialize dev agents
            for i, (agent_id, persona) in enumerate(zip(dev_agent_ids, personas), 1):
                agent = LettaDevAgent(
                    agent_id=agent_id,
                    name=f"Agent {i}",
                    persona=persona,
                    letta_client=self.letta_client,
                    shared_memory=self.shared_memory,
                    message_broker=self.message_broker,
                    artifact_manager=self.artifact_manager
                )
                self.dev_agents.append(agent)
                self.console.print(f"[green]✓[/green] Dev Agent {i} initialized")
            
            # Initialize commentator
            self.commentator = LettaCommentator(
                letta_agent_id=commentator_id,
                letta_client=self.letta_client,
                shared_memory=self.shared_memory,
                message_broker=self.message_broker
            )
            self.console.print("[green]✓[/green] Commentator initialized")
            
            # Initialize orchestrator
            self.orchestrator = LettaOrchestrator(
                letta_agent_id=orchestrator_id,
                letta_client=self.letta_client,
                shared_memory=self.shared_memory,
                message_broker=self.message_broker,
                dev_agents=self.dev_agents,
                commentator_agent=self.commentator
            )
            self.console.print("[green]✓[/green] Orchestrator initialized")
            
            # Setup background messaging between agents
            self._setup_background_messaging()
            self.console.print("[green]✓[/green] Background messaging enabled (3s intervals)")
            
            return True
            
        except Exception as e:
            self.console.print(f"[red]❌ Initialization error: {e}[/red]")
            return False
    
    async def run_project(self, user_prompt: str):
        """Run a complete project workflow."""
        try:
            # Note: Agents keep their memories across projects to learn and improve!
            
            # Start project and break down into subtasks
            result = await self.orchestrator.start_project(user_prompt)
            
            if not result["success"]:
                self.console.print("[red]Failed to start project[/red]")
                return
            
            subtasks = result["subtasks"]
            
            # Start live commentary
            await self.commentator.start_live_commentary()
            
            # Work through each subtask
            for i, subtask in enumerate(subtasks):
                self.console.print(f"\n{'='*70}")
                self.console.print(f"🎯 WORKING ON SUBTASK {i+1}/{len(subtasks)}")
                self.console.print(f"{'='*70}\n")
                
                # Assign subtask (posts to shared memory)
                await self.orchestrator.assign_subtask(i)
                
                # All dev agents work on the subtask in parallel
                tasks = [
                    agent.work_on_subtask(subtask, i)
                    for agent in self.dev_agents
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Give agents time to communicate in shared memory
                self.console.print("\n⏳ Allowing time for agent discussions...")
                await asyncio.sleep(15)  # 15 seconds for agents to chat
                
                # Show deliverables
                self.console.print(f"\n{'='*70}")
                self.console.print(f"📦 DELIVERABLES - SUBTASK {i+1}")
                self.console.print(f"{'='*70}\n")
                
                for j, result in enumerate(results, 1):
                    if isinstance(result, dict) and result.get("success"):
                        files_created = result.get('files_created', [])
                        if files_created:
                            self.console.print(f"✓ Agent {j}: {result.get('deliverable_description', 'Completed')}")
                            self.console.print(f"  Location: {result.get('deliverable_path', 'N/A')}")
                            self.console.print(f"  Files: {', '.join(files_created)}")
                        else:
                            self.console.print(f"✓ Agent {j}: {result.get('deliverable_description', 'Completed')}")
                            self.console.print(f"  File: {result.get('deliverable_path', 'N/A')}")
                    else:
                        self.console.print(f"✗ Agent {j}: Failed or error")
                
                self.console.print()
                
                # Collect user feedback
                feedback = await self.orchestrator.collect_feedback()
                
                # Brief pause before next subtask
                if i < len(subtasks) - 1:
                    self.console.print("\n⏳ Moving to next subtask...\n")
                    await asyncio.sleep(3)
            
            # Stop commentary and generate final summary
            await self.commentator.stop_live_commentary()
            await self.commentator.generate_final_summary()
            
            self.console.print(f"\n{'='*70}")
            self.console.print(f"✨ PROJECT COMPLETE!")
            self.console.print(f"{'='*70}\n")
            self.console.print(f"Check 'artifacts/' directory for all deliverables\n")
            
        except Exception as e:
            self.console.print(f"\n[red]Error during project: {e}[/red]")
            await self.commentator.stop_live_commentary()
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.commentator:
            await self.commentator.stop_live_commentary()


async def main():
    """Main entry point."""
    console = Console()
    system = DarwinSystem()
    
    # Display welcome
    system.display_welcome()
    
    # Initialize system
    if not await system.initialize():
        console.print("\n[red]Failed to initialize system. Please check your .env configuration.[/red]")
        return
    
    console.print("\n[green]✓ System ready![/green]\n")
    
    # Get user input
    console.print("="*70)
    console.print("Enter your frontend development project goal:")
    console.print("="*70)
    console.print("\nExamples:")
    console.print("  • Create an interactive 3D solar system visualization")
    console.print("  • Build a todo list app with drag-and-drop")
    console.print("  • Design a data dashboard with charts")
    console.print("  • Make a portfolio website with animations\n")
    
    user_prompt = input("Your project: ").strip()
    
    if not user_prompt:
        console.print("[yellow]No project provided. Exiting.[/yellow]")
        return
    
    # Run the project
    try:
        await system.run_project(user_prompt)
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Interrupted by user[/yellow]")
    finally:
        await system.cleanup()


if __name__ == "__main__":
    console = Console()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n\nGoodbye! 👋")
