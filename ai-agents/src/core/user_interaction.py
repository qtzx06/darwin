"""
User Interaction Manager - Handles user input and artifact display for competitive workflow.
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

console = Console()

class UserInteractionManager:
    """Manages user interaction for competitive workflow."""
    
    def __init__(self):
        self.console = console
    
    async def display_round_options(self, project_id: str, round_num: int, 
                                  artifacts: List[Dict[str, Any]]) -> int:
        """Display round options to user and get their choice."""
        self.console.print(f"\n{'='*80}")
        self.console.print(f"🎯 ROUND {round_num} - Choose Your Winner!", style="bold blue")
        self.console.print(f"{'='*80}")
        
        # Create table of options
        table = Table(title=f"Round {round_num} Submissions")
        table.add_column("Option", style="cyan", no_wrap=True)
        table.add_column("Agent", style="magenta")
        table.add_column("Personality", style="green")
        table.add_column("Summary", style="white")
        table.add_column("Lines", style="yellow")
        
        for i, artifact in enumerate(artifacts, 1):
            table.add_row(
                str(i),
                artifact.get("agent_name", "Unknown"),
                artifact.get("personality", "")[:30] + "...",
                artifact.get("code_summary", "")[:50] + "...",
                str(artifact.get("lines_of_code", 0))
            )
        
        self.console.print(table)
        
        # Display code previews
        self.console.print(f"\n📝 Code Previews:")
        for i, artifact in enumerate(artifacts, 1):
            self.console.print(f"\n--- Option {i}: {artifact.get('agent_name', 'Unknown')} ---")
            
            code = artifact.get("code", "")
            if code:
                # Show first 20 lines of code
                code_lines = code.split('\n')[:20]
                preview_code = '\n'.join(code_lines)
                if len(code.split('\n')) > 20:
                    preview_code += "\n... (truncated)"
                
                syntax = Syntax(preview_code, "typescript", theme="monokai", line_numbers=True)
                self.console.print(syntax)
            else:
                self.console.print("[red]No code available[/red]")
        
        # Get user choice
        while True:
            try:
                choice = await self._get_user_input(f"\n👑 Choose winner (1-{len(artifacts)}): ")
                choice_num = int(choice)
                if 1 <= choice_num <= len(artifacts):
                    return choice_num - 1  # Convert to 0-based index
                else:
                    self.console.print(f"[red]Please enter a number between 1 and {len(artifacts)}[/red]")
            except ValueError:
                self.console.print("[red]Please enter a valid number[/red]")
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Exiting...[/yellow]")
                return 0  # Default to first option
    
    async def display_final_results(self, project_id: str, final_artifacts: List[Dict[str, Any]]):
        """Display final project results."""
        self.console.print(f"\n{'='*80}")
        self.console.print(f"🎉 PROJECT COMPLETED! - Final Results", style="bold green")
        self.console.print(f"{'='*80}")
        
        # Create results table
        table = Table(title="Final Agent Results")
        table.add_column("Agent", style="cyan")
        table.add_column("Personality", style="magenta")
        table.add_column("Wins", style="green")
        table.add_column("Total Rounds", style="yellow")
        table.add_column("Win Rate", style="blue")
        table.add_column("Lines of Code", style="white")
        
        for artifact in final_artifacts:
            wins = artifact.get("wins", 0)
            total_rounds = artifact.get("total_rounds", 0)
            win_rate = (wins / total_rounds * 100) if total_rounds > 0 else 0
            
            table.add_row(
                artifact.get("agent_name", "Unknown"),
                artifact.get("personality", "")[:30] + "...",
                str(wins),
                str(total_rounds),
                f"{win_rate:.1f}%",
                str(artifact.get("lines_of_code", 0))
            )
        
        self.console.print(table)
        
        # Show artifact locations
        self.console.print(f"\n📁 Artifacts saved to: artifacts/{project_id}/")
        self.console.print(f"  • Each agent has their own final/ folder")
        self.console.print(f"  • Canonical code in canonical/ folder")
        self.console.print(f"  • Round-by-round history in each agent's round_*/ folders")
    
    async def display_agent_work_progress(self, agent_name: str, subtask: str, progress: str):
        """Display real-time agent work progress."""
        self.console.print(f"  🔨 {agent_name}: {progress} on '{subtask}'")
    
    async def display_commentator_narration(self, narration: str):
        """Display commentator narration."""
        self.console.print(f"🎙️ Commentator: {narration}")
    
    async def get_user_feedback(self, prompt: str) -> str:
        """Get user feedback during the process."""
        return await self._get_user_input(f"💬 {prompt}")
    
    async def display_winner_analysis(self, winner: Dict[str, Any], analysis: str):
        """Display winner analysis."""
        self.console.print(f"\n🏆 Winner Analysis:")
        self.console.print(f"  Agent: {winner.get('agent_name', 'Unknown')}")
        self.console.print(f"  Why they won: {analysis}")
    
    async def display_learning_summary(self, learning: str):
        """Display learning summary sent to agents."""
        self.console.print(f"\n📚 Learning Summary:")
        self.console.print(f"  {learning}")
    
    async def _get_user_input(self, prompt: str) -> str:
        """Get user input asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, input, prompt)
    
    def display_project_structure(self, project_id: str):
        """Display the project folder structure."""
        project_path = Path("artifacts") / project_id
        
        if not project_path.exists():
            self.console.print(f"[red]Project {project_id} not found[/red]")
            return
        
        self.console.print(f"\n📁 Project Structure: {project_path}")
        
        def print_tree(path: Path, prefix: str = ""):
            """Print directory tree."""
            if path.is_file():
                self.console.print(f"{prefix}📄 {path.name}")
            elif path.is_dir():
                self.console.print(f"{prefix}📁 {path.name}/")
                try:
                    for child in sorted(path.iterdir()):
                        if child.name.startswith('.'):
                            continue
                        print_tree(child, prefix + "  ")
                except PermissionError:
                    pass
        
        print_tree(project_path)
    
    def display_artifact_metadata(self, artifact_path: str):
        """Display metadata for a specific artifact."""
        metadata_file = Path(artifact_path) / "metadata.json"
        
        if not metadata_file.exists():
            self.console.print(f"[red]Metadata file not found: {metadata_file}[/red]")
            return
        
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            self.console.print(f"\n📋 Artifact Metadata:")
            for key, value in metadata.items():
                self.console.print(f"  {key}: {value}")
                
        except Exception as e:
            self.console.print(f"[red]Error reading metadata: {e}[/red]")
    
    async def display_round_summary(self, round_num: int, subtask: str, 
                                  artifacts: List[Dict[str, Any]], winner: Dict[str, Any]):
        """Display summary of a completed round."""
        self.console.print(f"\n📊 Round {round_num} Summary:")
        self.console.print(f"  Subtask: {subtask}")
        self.console.print(f"  Submissions: {len(artifacts)}")
        self.console.print(f"  Winner: {winner.get('agent_name', 'Unknown')}")
        
        # Show code statistics
        total_lines = sum(artifact.get("lines_of_code", 0) for artifact in artifacts)
        avg_lines = total_lines / len(artifacts) if artifacts else 0
        
        self.console.print(f"  Total lines of code: {total_lines}")
        self.console.print(f"  Average lines per agent: {avg_lines:.1f}")
