#!/usr/bin/env python3
"""
Main entry point for the Letta AI Agent PM Simulator.
CLI interface for user input and real-time display of agent activities.
"""
import asyncio
import sys
import os
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.live import Live

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.coordinator import Coordinator


class PMSimulatorCLI:
    """Command-line interface for the PM Simulator."""
    
    def __init__(self):
        self.console = Console()
        self.coordinator = Coordinator()
        self.is_running = False
    
    def display_welcome(self):
        """Display welcome message and instructions."""
        welcome_text = Text("Letta AI Agent PM Simulator", style="bold blue")
        subtitle = Text("Watch AI agents collaborate on your project in real-time", style="italic")
        
        self.console.print(Panel.fit(
            f"{welcome_text}\n\n{subtitle}\n\n"
            "This simulator features:\n"
            "• 4 Coding Agents with different specializations\n"
            "• 1 Commentator Agent for real-time narration\n"
            "• Shared memory and inter-agent communication\n"
            "• Live artifact tracking and progress monitoring\n\n"
            "Enter a project description to get started!",
            title="🤖 AI Agent PM Simulator",
            border_style="blue"
        ))
    
    def display_agent_info(self):
        """Display information about the available agents."""
        table = Table(title="Available AI Agents", show_header=True, header_style="bold magenta")
        table.add_column("Agent", style="cyan", no_wrap=True)
        table.add_column("Specialization", style="green")
        table.add_column("Personality", style="yellow")
        
        agents = [
            ("Frontend Specialist", "UI/UX Design & Frontend Development", "Detail-oriented and creative"),
            ("Backend Architect", "System Design & Data Management", "Logical and methodical"),
            ("DevOps Engineer", "Infrastructure & Deployment", "Pragmatic and security-focused"),
            ("Full-Stack Developer", "Versatile Problem Solving", "Adaptable and collaborative"),
            ("Project Narrator", "Progress Monitoring & Commentary", "Observant and articulate")
        ]
        
        for agent, specialization, personality in agents:
            table.add_row(agent, specialization, personality)
        
        self.console.print(table)
    
    async def initialize_system(self) -> bool:
        """Initialize the coordinator and all agents."""
        self.console.print("\n[bold blue]Initializing AI agents...[/bold blue]")
        
        try:
            # Initialize agents
            success = await self.coordinator.initialize_agents()
            
            if success:
                self.console.print("[green]✅ All agents initialized successfully![/green]")
                return True
            else:
                self.console.print("[red]❌ Failed to initialize agents. Check your Letta configuration.[/red]")
                return False
                
        except Exception as e:
            self.console.print(f"[red]❌ Error initializing system: {e}[/red]")
            return False
    
    def get_user_input(self) -> str:
        """Get project description from user."""
        self.console.print("\n[bold cyan]Enter your project description:[/bold cyan]")
        self.console.print("[dim]Example: 'Build a web-based task management application'[/dim]")
        
        while True:
            try:
                user_input = input("\n> ").strip()
                if user_input:
                    return user_input
                else:
                    self.console.print("[yellow]Please enter a project description.[/yellow]")
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Operation cancelled by user.[/yellow]")
                return None
            except EOFError:
                self.console.print("\n[yellow]Operation cancelled.[/yellow]")
                return None
    
    async def run_simulation(self, task_description: str):
        """Run the agent simulation with real-time display."""
        self.console.print(f"\n[bold green]Starting simulation for:[/bold green] {task_description}")
        
        # Distribute task
        distribution_result = await self.coordinator.distribute_task(task_description)
        if not distribution_result.get("success"):
            self.console.print(f"[red]❌ Failed to distribute task: {distribution_result.get('error')}[/red]")
            return
        
        # Display task distribution
        self.console.print("\n[bold cyan]Task Distribution:[/bold cyan]")
        for agent_id, subtask in distribution_result.get("distribution", {}).items():
            agent_name = agent_id.replace("_", " ").title()
            self.console.print(f"  • {agent_name}: {subtask}")
        
        # Start simulation with live display
        await self._run_with_live_display()
        
        # Show log file location
        if hasattr(self.coordinator, 'logger'):
            summary = self.coordinator.logger.get_session_summary()
            self.console.print(f"\n📋 Session Summary:")
            self.console.print(f"  • Agents: {summary['agents']}")
            self.console.print(f"  • Artifacts: {summary['artifacts']}")
            self.console.print(f"  • Messages: {summary['messages']}")
            self.console.print(f"  • Events: {summary['events']}")
            self.console.print(f"\n📁 Log files saved to:")
            self.console.print(f"  • Log: {summary['log_file']}")
            self.console.print(f"  • Session: {summary['session_file']}")
    
    async def _run_with_live_display(self):
        """Run simulation with live progress display."""
        self.is_running = True
        
        try:
            # Start simulation in background
            simulation_task = asyncio.create_task(self.coordinator.start_simulation())
            
            # Simple display loop
            while self.is_running and not simulation_task.done():
                # Get current progress
                progress = await self.coordinator.monitor_progress()
                
                # Display current status
                self.console.clear()
                self.console.print("[bold blue]🤖 AI Agent PM Simulator[/bold blue]")
                self.console.print(f"[green]Status: {progress.get('overall_status', 'Running')}[/green]")
                
                # Show agent statuses
                for agent_id, status in progress.get('agent_statuses', {}).items():
                    self.console.print(f"🤖 {agent_id}: {status.get('status', 'Unknown')}")
                
                await asyncio.sleep(2)  # Update every 2 seconds
            
            # Wait for simulation to complete
            if not simulation_task.done():
                await simulation_task
                
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Simulation interrupted by user.[/yellow]")
            await self.coordinator.stop_simulation()
        finally:
            self.is_running = False
    
    
    async def display_final_results(self):
        """Display final results after simulation completes."""
        self.console.print("\n[bold green]Simulation Complete![/bold green]")
        
        try:
            # Get project overview
            overview = await self.coordinator.get_project_overview()
            
            if overview.get("error"):
                self.console.print(f"[red]Error getting results: {overview['error']}[/red]")
                return
            
            # Display agent summaries
            self.console.print("\n[bold cyan]Agent Summaries:[/bold cyan]")
            for agent_id, agent_data in overview.get("agents", {}).items():
                agent_name = agent_data.get("name", agent_id)
                summary = agent_data.get("summary", "No summary available")
                
                self.console.print(Panel(
                    summary,
                    title=f"🤖 {agent_name}",
                    border_style="blue"
                ))
            
            # Display artifacts summary
            artifacts_summary = await self.coordinator.get_artifacts_summary()
            self.console.print("\n[bold cyan]Artifacts Created:[/bold cyan]")
            
            for agent_id, agent_data in artifacts_summary.get("agents", {}).items():
                agent_name = agent_data.get("name", agent_id)
                count = agent_data.get("artifact_count", 0)
                self.console.print(f"  • {agent_name}: {count} artifacts")
            
            # Display message statistics
            message_stats = overview.get("messages", {})
            if message_stats:
                self.console.print(f"\n[bold cyan]Communication Stats:[/bold cyan]")
                self.console.print(f"  • Total messages: {message_stats.get('total_messages', 0)}")
                self.console.print(f"  • Active agents: {message_stats.get('unique_agents', 0)}")
            
        except Exception as e:
            self.console.print(f"[red]Error displaying results: {e}[/red]")
    
    async def run(self):
        """Main run loop."""
        try:
            # Display welcome and agent info
            self.display_welcome()
            self.display_agent_info()
            
            # Initialize system
            if not await self.initialize_system():
                return
            
            # Get user input
            task_description = self.get_user_input()
            if not task_description:
                return
            
            # Run simulation
            await self.run_simulation(task_description)
            
            # Display final results
            await self.display_final_results()
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Goodbye![/yellow]")
        except Exception as e:
            self.console.print(f"[red]Unexpected error: {e}[/red]")
        finally:
            if self.is_running:
                await self.coordinator.stop_simulation()


async def main():
    """Main entry point."""
    simulator = PMSimulatorCLI()
    await simulator.run()


if __name__ == "__main__":
    # Check if running in the correct directory
    if not os.path.exists("src"):
        print("Error: Please run this script from the ai-agents directory")
        sys.exit(1)
    
    # Run the simulator
    asyncio.run(main())
