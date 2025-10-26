#!/usr/bin/env python3
"""
Darwin Hybrid System - Main Entry Point
Letta agents orchestrating AutoGen teams for competitive development
"""
import asyncio
import sys
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.shared_memory import SharedMemory
from src.core.message_system import MessageBroker
from src.artifacts.artifact_manager import ArtifactManager
from src.core.logger import PMSimulatorLogger
from src.agents.hybrid_letta_autogen_agent import HybridLettaDevAgent
from src.agents.hybrid_orchestrator import HybridOrchestrator
from src.agents.hybrid_commentator import HybridCommentator
from src.artifact_server import start_artifact_server

try:
    from letta_client import Letta
except ImportError:
    print("Error: letta-client not installed. Install with: pip install letta-client")
    sys.exit(1)

load_dotenv()


class DarwinHybridSystem:
    """Main system coordinator for Darwin hybrid architecture."""
    
    def __init__(self):
        self.console = Console()
        self.silent = True  # Only show commentator output
        
        # Initialize core systems
        self.shared_memory = SharedMemory()
        self.message_broker = MessageBroker()
        self.artifact_manager = ArtifactManager()
        self.logger = PMSimulatorLogger()
        
        # Letta client
        self.letta_client = None
        self.dev_agents = []
        self.orchestrator = None
        self.commentator = None
        self.artifact_server = None
    
    def _print(self, *args, **kwargs):
        """Conditional print based on silent flag."""
        if not self.silent:
            self.console.print(*args, **kwargs)
    
    def display_welcome(self):
        """Display welcome message."""
        welcome = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║         🧬 DARWIN - Competitive AI Development 🧬        ║
║                                                           ║
║   Letta Memory + AutoGen Problem-Solving = Evolution     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

Architecture:
  • 4 Letta Dev Agents (each managing an AutoGen team)
  • 1 Orchestrator Agent (breaks down tasks, collects feedback)
  • 1 Commentator Agent (narrates the competition)

Workflow:
  1. You provide a project goal
  2. Orchestrator breaks it into subtasks
  3. 4 teams compete on each subtask
  4. You give feedback
  5. Teams learn and improve for next subtask
  6. Repeat until project complete!
"""
        self._print(Panel(welcome, border_style="cyan", title="🚀 Welcome"))
    
    async def initialize(self) -> bool:
        """Initialize all agents."""
        self._print("\n[cyan]Initializing Darwin Hybrid System...[/cyan]")
        
        # Check for required API keys
        if not os.getenv("LETTA_API_TOKEN"):
            self._print("[red]❌ LETTA_API_TOKEN not set in .env file[/red]")
            return False
        
        # Check for at least one LLM provider
        has_llm = any([
            os.getenv("GOOGLE_API_KEY_TEAM1"),
            os.getenv("ANTHROPIC_API_KEY"),
            os.getenv("OPENAI_API_KEY")
        ])
        
        if not has_llm:
            self._print("[red]❌ No LLM API keys found in .env[/red]")
            self._print("[yellow]Need at least: GOOGLE_API_KEY_TEAM1 (or ANTHROPIC/OPENAI)[/yellow]")
            return False
        
        try:
            # Initialize Letta client
            self.letta_client = Letta(
                token=os.getenv("LETTA_API_TOKEN"),
                project="default-project"
            )
            self._print("[green]✓[/green] Letta client initialized")
            
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
                self._print("[red]❌ Missing dev agent IDs in .env[/red]")
                self._print("[yellow]Required: LETTA_AGENT_1 through LETTA_AGENT_4[/yellow]")
                self._print("[yellow]Run 'python setup_hybrid_agents.py' to create agents first[/yellow]")
                return False
            
            if not orchestrator_id:
                self._print("[red]❌ LETTA_ORCHESTRATOR_AGENT_ID not set in .env[/red]")
                self._print("[yellow]Run 'python setup_hybrid_agents.py' to create agents first[/yellow]")
                return False
            
            if not commentator_id:
                self._print("[red]❌ LETTA_COMMENTATOR_AGENT_ID not set in .env[/red]")
                self._print("[yellow]Run 'python setup_hybrid_agents.py' to create agents first[/yellow]")
                return False
            
            # Verify agents exist in Letta (read-only check)
            self._print("[cyan]Verifying agents exist in Letta...[/cyan]")
            # NOTE: Letta API verification temporarily disabled
            # The API structure has changed and we need to find the new method
            # For now, we'll just verify the IDs are set
            self._print("[yellow]⚠️  Agent verification skipped (API changed)[/yellow]")
            self._print("[dim]  Agents will be validated when first used[/dim]")
            
            # Create 4 hybrid dev agents - simple team names
            names = [
                "Team 1",
                "Team 2", 
                "Team 3",
                "Team 4"
            ]
            
            # Specializations for internal use only (not displayed)
            specializations = [
                "Full-stack development",
                "Full-stack development",
                "Full-stack development",
                "Full-stack development"
            ]
            
            for i, (agent_id, spec, name) in enumerate(zip(dev_agent_ids, specializations, names)):
                # NOTE: We use existing agents - NEVER create new ones
                agent = HybridLettaDevAgent(
                    agent_id=agent_id,  # From .env - must already exist
                    name=name,
                    specialization=spec,
                    team_number=i + 1,  # Team 1, 2, 3, 4 for separate Gemini keys
                    letta_client=self.letta_client,
                    shared_memory=self.shared_memory,
                    message_broker=self.message_broker,
                    artifact_manager=self.artifact_manager,
                    logger=self.logger
                )
                self.dev_agents.append(agent)
                self._print(f"[green]✓[/green] {name} loaded (Team {i+1} API key)")
            
            # Create orchestrator (uses existing agent)
            self.orchestrator = HybridOrchestrator(
                letta_agent_id=orchestrator_id,  # From .env - must already exist
                letta_client=self.letta_client,
                shared_memory=self.shared_memory,
                message_broker=self.message_broker,
                dev_agents=self.dev_agents,
                commentator_agent=None,  # Will set after creating commentator
                logger=self.logger
            )
            self._print(f"[green]✓[/green] Orchestrator loaded")
            
            # Create commentator (uses existing agent)
            self.commentator = HybridCommentator(
                letta_agent_id=commentator_id,  # From .env - must already exist
                letta_client=self.letta_client,
                shared_memory=self.shared_memory,
                message_broker=self.message_broker,
                logger=self.logger
            )
            self.orchestrator.commentator = self.commentator
            self._print(f"[green]✓[/green] Commentator loaded")
            
            # Start artifact server
            self.artifact_server = start_artifact_server(port=8080)
            if self.artifact_server:
                self._print("[green]✓[/green] Artifact viewer started at http://localhost:8080/artifact_viewer.html")
            
            self._print("\n[bold green]✅ All 6 agents loaded from .env![/bold green]")
            self._print("[dim]Note: This system ONLY uses existing agents, never creates new ones[/dim]\n")
            return True
            
        except Exception as e:
            self._print(f"[red]❌ Initialization error: {e}[/red]")
            import traceback
            traceback.print_exc()
            return False
    
    async def reset_agent_memories(self):
        """Wipe all agent memories for a fresh start on new project."""
        self._print("\n[yellow]🧹 Resetting all agent memories...[/yellow]")
        
        try:
            # Reset all dev agents
            for agent in self.dev_agents:
                # NOTE: Letta API changed - get_messages method no longer exists
                # For now, just reset internal state
                # TODO: Use new Letta API when available
                
                # Reset agent's internal state
                agent.is_working = False
                agent.current_subtask = None
                agent.subtasks_completed = 0
                agent._write_codebase("")  # Clear codebase file
            
            # Reset orchestrator
            if self.orchestrator:
                # NOTE: Letta API changed - send_message no longer exists
                # Just reset internal state for now
                self.orchestrator.subtasks = []
                self.orchestrator.feedback_history = []
                self.orchestrator.project_goal = ""
            
            # Reset commentator
            if self.commentator:
                # NOTE: Letta API changed - send_message no longer exists
                # Just reset internal state for now
                await self.commentator.clear_live_buffer()
            
            # Clear shared memory
            self.shared_memory.clear_all()
            
            # Clear artifacts directory (optional - keeps old projects)
            # artifacts_dir = Path("artifacts")
            # if artifacts_dir.exists():
            #     import shutil
            #     shutil.rmtree(artifacts_dir)
            #     artifacts_dir.mkdir()
            
            self._print("[green]✅ All memories reset! Ready for new project.[/green]\n")
            
        except Exception as e:
            self._print(f"[red]❌ Error resetting memories: {e}[/red]")
            import traceback
            traceback.print_exc()
    
    async def run(self):
        """Main run loop - supports multiple projects."""
        try:
            self.display_welcome()
            
            if not await self.initialize():
                self._print("[red]Failed to initialize system.[/red]")
                return
            
            # Main project loop - user can do multiple projects
            while True:
                # Get user project prompt (ALWAYS show this)
                self.console.print("\n[bold cyan]What would you like to build?[/bold cyan]")
                self.console.print("[dim]Example: 'Create an interactive 3D solar system website'[/dim]")
                self.console.print("[dim]Type 'quit' or 'exit' to stop[/dim]\n")
                
                user_prompt = input("Your project: ").strip()
                
                if not user_prompt or user_prompt.lower() in ['quit', 'exit', 'q']:
                    self.console.print("[yellow]👋 Goodbye![/yellow]")
                    break
                
                # Reset memories for new project
                await self.reset_agent_memories()
                
                # Start project
                result = await self.orchestrator.start_project(user_prompt)
                
                if not result.get("success"):
                    self.console.print(f"[red]Failed to start project: {result.get('error')}[/red]")
                    continue
                
                # Run full project workflow
                await self.orchestrator.run_full_project()
                
                # Generate final summary
                num_subtasks = len(self.orchestrator.subtasks)
                final_summary = await self.commentator.generate_project_summary(num_subtasks)
                self.console.print(Panel(final_summary, border_style="green", title="🏆 Final Summary"))
                
                # Ask if user wants to do another project
                self.console.print("\n[cyan]Ready for another project![/cyan]")
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]⏸️ Interrupted by user[/yellow]")
        except Exception as e:
            self.console.print(f"[red]❌ Error: {e}[/red]")
            import traceback
            traceback.print_exc()


async def main():
    """Entry point."""
    system = DarwinHybridSystem()
    await system.run()


if __name__ == "__main__":
    asyncio.run(main())
