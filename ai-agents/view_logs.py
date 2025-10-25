#!/usr/bin/env python3
"""
Log viewer for the Letta AI Agent PM Simulator.
View recent logs and session data.
"""
import json
import os
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()

def find_latest_logs():
    """Find the most recent log files."""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        return None, None
    
    # Find latest log files
    log_files = list(logs_dir.glob("pm_simulator_*.log"))
    session_files = list(logs_dir.glob("session_*.json"))
    
    if not log_files:
        return None, None
    
    # Get the most recent files
    latest_log = max(log_files, key=os.path.getctime)
    latest_session = max(session_files, key=os.path.getctime) if session_files else None
    
    return latest_log, latest_session

def view_session_summary(session_file):
    """View session summary from JSON file."""
    try:
        with open(session_file, 'r') as f:
            data = json.load(f)
        
        console.print(Panel(
            f"Session ID: {data.get('session_id', 'Unknown')}\n"
            f"Project: {data.get('project_description', 'Unknown')}\n"
            f"Start: {data.get('start_time', 'Unknown')}\n"
            f"End: {data.get('end_time', 'In Progress')}\n"
            f"Status: {data.get('final_status', 'Running')}",
            title="📊 Session Summary",
            border_style="blue"
        ))
        
        # Agent summary table
        agent_table = Table(title="🤖 Agents", show_header=True, header_style="bold magenta")
        agent_table.add_column("Agent", style="cyan")
        agent_table.add_column("Type", style="green")
        agent_table.add_column("Activities", style="yellow")
        agent_table.add_column("Artifacts", style="blue")
        agent_table.add_column("Messages", style="purple")
        
        for agent_id, agent_data in data.get("agents", {}).items():
            agent_table.add_row(
                agent_data.get("name", agent_id),
                agent_data.get("type", "unknown"),
                str(len(agent_data.get("activities", []))),
                str(agent_data.get("artifacts_created", 0)),
                f"{agent_data.get('messages_sent', 0)}/{agent_data.get('messages_received', 0)}"
            )
        
        console.print(agent_table)
        
        # Recent activities
        console.print("\n📝 Recent Activities:")
        for agent_id, agent_data in data.get("agents", {}).items():
            activities = agent_data.get("activities", [])
            if activities:
                latest = activities[-1]
                console.print(f"  • {agent_data.get('name', agent_id)}: {latest.get('activity', 'Unknown')}")
        
        # Recent messages
        messages = data.get("messages", [])
        if messages:
            console.print(f"\n💬 Recent Messages ({len(messages)} total):")
            for msg in messages[-5:]:  # Show last 5 messages
                from_name = msg.get("from_agent", "Unknown")
                to_name = msg.get("to_agent", "Unknown")
                content = msg.get("content", "")[:100] + "..." if len(msg.get("content", "")) > 100 else msg.get("content", "")
                console.print(f"  • {from_name} → {to_name}: {content}")
        
        # Artifacts
        artifacts = data.get("artifacts", [])
        if artifacts:
            console.print(f"\n📦 Artifacts Created ({len(artifacts)} total):")
            for artifact in artifacts[-5:]:  # Show last 5 artifacts
                agent_name = data.get("agents", {}).get(artifact.get("agent_id", ""), {}).get("name", artifact.get("agent_id", "Unknown"))
                console.print(f"  • {agent_name}: {artifact.get('type', 'unknown')} - {artifact.get('artifact_id', 'Unknown')}")
        
    except Exception as e:
        console.print(f"[red]Error reading session file: {e}[/red]")

def view_log_file(log_file, lines=50):
    """View recent lines from log file."""
    try:
        with open(log_file, 'r') as f:
            all_lines = f.readlines()
        
        recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        console.print(Panel(
            "".join(recent_lines),
            title=f"📄 Recent Log Entries (last {len(recent_lines)} lines)",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(f"[red]Error reading log file: {e}[/red]")

def main():
    """Main log viewer function."""
    console.print(Panel(
        "Letta AI Agent PM Simulator - Log Viewer",
        title="🔍 Log Viewer",
        border_style="bold blue"
    ))
    
    # Find latest logs
    log_file, session_file = find_latest_logs()
    
    if not log_file:
        console.print("[yellow]No log files found. Run the simulator first![/yellow]")
        return
    
    console.print(f"📁 Found log files:")
    console.print(f"  • Log: {log_file}")
    if session_file:
        console.print(f"  • Session: {session_file}")
    
    # View session summary
    if session_file:
        view_session_summary(session_file)
    
    # View recent log entries
    console.print("\n" + "="*80)
    view_log_file(log_file)
    
    console.print(f"\n💡 Tip: Use 'tail -f {log_file}' to watch logs in real-time")

if __name__ == "__main__":
    main()

