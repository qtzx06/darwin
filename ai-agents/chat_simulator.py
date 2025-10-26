"""
Main chat simulator - orchestrates the randomized chat between agents and Boss.
Handles timing, message routing, and terminal display.
"""
import asyncio
import random
import sys
from datetime import datetime
from typing import Optional, List
from collections import deque
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from chat_config import (
    AGENT_NAMES, 
    CHAT_SETTINGS, 
    get_system_prompt
)
from chat_manager import ClaudeManager


class ChatSimulator:
    """Main chat simulator with randomized timing and agent interactions."""
    
    def __init__(self):
        self.console = Console()
        self.claude_manager = ClaudeManager(system_prompt=get_system_prompt())
        
        # Chat state
        self.is_running = False
        self.chat_history: deque = deque(maxlen=100)  # Keep last 100 messages
        self.pending_user_messages: List[str] = []
        self.last_user_input_time: Optional[float] = None
        
        # Timing controls
        self.next_agent_message_time: Optional[float] = None
        
        # Competition state
        self.competition_active = False
        
    async def start_competition(self):
        """Start the active competition phase."""
        self.competition_active = True
        self.claude_manager.add_system_context(
            "COMPETITION HAS STARTED! Agents are now actively building and competing. "
            "Ramp up the trash talk, boasting, and rivalry. Flex about your progress, "
            "roast others' approaches, and try to impress Boss."
        )
        self.console.print("[bold green]🏆 COMPETITION STARTED 🏆[/bold green]")
    
    async def add_agent_progress(self, agent_name: str, progress_update: str):
        """Feed agent progress context to Claude without requiring response."""
        self.claude_manager.add_system_context(
            f"[Progress Update] {agent_name}: {progress_update}"
        )
    
    async def start(self):
        """Start the chat simulator."""
        self.is_running = True
        
        # Schedule first agent message
        self._schedule_next_agent_message()
        
        # Start concurrent tasks
        tasks = [
            asyncio.create_task(self._agent_message_loop()),
            asyncio.create_task(self._user_input_loop()),
            asyncio.create_task(self._user_message_processor())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            pass  # Silent exit
        finally:
            self.is_running = False
    
    async def _agent_message_loop(self):
        """Main loop for random agent messages."""
        while self.is_running:
            current_time = asyncio.get_event_loop().time()
            
            # Check if it's time for an agent message
            if self.next_agent_message_time and current_time >= self.next_agent_message_time:
                await self._trigger_agent_message()
                self._schedule_next_agent_message()
            
            await asyncio.sleep(0.1)  # Check every 100ms
    
    async def _user_input_loop(self):
        """Loop to capture user input without blocking."""
        loop = asyncio.get_event_loop()
        
        while self.is_running:
            try:
                # Read user input in a non-blocking way
                user_input = await loop.run_in_executor(None, self._get_input)
                
                if user_input:
                    self.pending_user_messages.append(user_input)
                    self.last_user_input_time = asyncio.get_event_loop().time()
                    
            except Exception as e:
                if self.is_running:  # Only print if not shutting down
                    self.console.print(f"[red]Input error: {e}[/red]")
    
    def _get_input(self) -> Optional[str]:
        """Get input from user (blocking)."""
        try:
            return input()
        except EOFError:
            return None
    
    async def _user_message_processor(self):
        """Process bundled user messages after debounce period."""
        while self.is_running:
            current_time = asyncio.get_event_loop().time()
            
            # Check if we have pending messages and debounce period has passed
            if (self.pending_user_messages and 
                self.last_user_input_time and
                current_time - self.last_user_input_time >= CHAT_SETTINGS["user_input_debounce"]):
                
                # Bundle all pending messages
                bundled_message = " ".join(self.pending_user_messages)
                self.pending_user_messages.clear()
                
                # Display user message
                self._display_message("Boss", bundled_message, "yellow")
                
                # Add to Claude's history
                self.claude_manager.add_user_message(bundled_message, is_boss=True)
                
                # Get response from Claude
                await self._get_and_display_response(f"Boss said: {bundled_message}")
            
            await asyncio.sleep(0.1)
    
    async def _trigger_agent_message(self):
        """Trigger a random agent to message another random agent or Boss."""
        # Pick random speaker
        speaker = random.choice(AGENT_NAMES)
        
        # Pick random target (can be another agent or Boss)
        possible_targets = [name for name in AGENT_NAMES if name != speaker] + ["Boss"]
        target = random.choice(possible_targets)
        
        # Build context for Claude
        context = f"[Random chat moment: {speaker} wants to say something to {target}. Generate their message naturally based on the ongoing conversation.]"
        
        # Get response from Claude
        await self._get_and_display_response(context)
    
    async def _get_and_display_response(self, trigger_context: str):
        """Get response from Claude and display it."""
        # Show typing indicator briefly
        self.console.print("[dim]...[/dim]", end="\r")
        
        # Get response from Claude
        response = await self.claude_manager.get_chat_response(trigger_context)
        
        if response:
            # Parse and display the response (may contain multiple messages)
            await self._parse_and_display_response(response)
    
    async def _parse_and_display_response(self, response: str):
        """Parse Claude's response and display each message with delays."""
        # Split by lines and look for "Name: message" pattern
        lines = response.strip().split("\n")
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Check if line matches "Name: message" format
            if ": " in line:
                parts = line.split(": ", 1)
                if len(parts) == 2:
                    speaker, message = parts
                    speaker = speaker.strip()
                    message = message.strip()
                    
                    # Only display if speaker is a valid agent
                    if speaker in AGENT_NAMES:
                        self._display_message(speaker, message, self._get_agent_color(speaker))
                        
                        # Add delay between messages (1-4 seconds)
                        # Skip delay after the last message
                        if i < len(lines) - 1:
                            delay = random.uniform(1.0, 4.0)
                            await asyncio.sleep(delay)
                        continue
            
            # If not properly formatted, display as-is
            self.console.print(f"[dim]{line}[/dim]")
    
    def _display_message(self, speaker: str, message: str, color: str = "white"):
        """Display a chat message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Format message
        formatted = f"[dim]{timestamp}[/dim] [{color}]{speaker}[/{color}]: {message}"
        self.console.print(formatted)
        
        # Add to history
        self.chat_history.append({
            "timestamp": timestamp,
            "speaker": speaker,
            "message": message
        })
    
    def _get_agent_color(self, agent_name: str) -> str:
        """Get display color for an agent."""
        colors = {
            "Speedrunner": "red",
            "Bloom": "magenta",
            "Solver": "blue",
            "Loader": "cyan",
            "Boss": "bold yellow"
        }
        return colors.get(agent_name, "white")
    
    def _schedule_next_agent_message(self):
        """Schedule the next random agent message."""
        delay = random.uniform(*CHAT_SETTINGS["agent_message_interval"])
        self.next_agent_message_time = asyncio.get_event_loop().time() + delay


async def main():
    """Main entry point."""
    simulator = ChatSimulator()
    await simulator.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass  # Silent exit
        sys.exit(0)
