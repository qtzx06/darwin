"""
Letta Frontend Dev Agent
Pure Letta agent that works independently on frontend tasks
"""
import os
import json
import asyncio
import aiohttp
import random
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from ..core.shared_memory import SharedMemory
from ..core.message_system import MessageBroker
from ..artifacts.artifact_manager import ArtifactManager


class LettaDevAgent:
    """
    Frontend development agent powered by Letta.
    Works independently on subtasks, posts progress to shared memory,
    and delivers React components or HTML/CSS/JS artifacts.
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        persona: str,
        letta_client,
        shared_memory: SharedMemory,
        message_broker: MessageBroker,
        artifact_manager: ArtifactManager
    ):
        self.agent_id = agent_id
        self.name = name
        self.persona = persona
        self.letta_client = letta_client
        self.shared_memory = shared_memory
        self.message_broker = message_broker
        self.artifact_manager = artifact_manager
        
        # Silence mode - only commentator should print
        self.silent = True
        
        # Artifact directory for this agent
        self.artifact_dir = Path(f"artifacts/agent_{agent_id}")
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        
        # Agent state
        self.is_working = False
        self.current_subtask = None
        self.deliverables_completed = 0
        
        # Background messaging
        self.messaging_task = None
        self.other_agent_ids = []  # Will be set by orchestrator
        self.commentator_id = None  # Will be set by orchestrator
    
    def _print(self, *args, **kwargs):
        """Print only if not in silent mode."""
        if not self.silent:
            print(*args, **kwargs)
    
    async def work_on_subtask(self, subtask: str, subtask_index: int) -> Dict[str, Any]:
        """
        Work on a subtask by sending it to the Letta agent.
        The agent will use shared memory tools to communicate with others.
        
        Args:
            subtask: The subtask description
            subtask_index: Index of the current subtask
            
        Returns:
            Dict with completion status and deliverable info
        """
        self.is_working = True
        self.current_subtask = subtask
        
        self._print(f"\n{self.name} starting work on subtask {subtask_index}...")
        
        try:
            # Construct message to Letta agent
            instruction = f"""
You are {self.name}, a frontend developer working on a collaborative project.

PERSONALITY: {self.persona}

CURRENT SUBTASK:
{subtask}

YOUR MISSION:
1. POST your thoughts and progress to shared memory for others to read (you cannot read their messages)
2. Address other agents by name when posting (Agent 1, Agent 2, Agent 3, Agent 4, Orchestrator)
3. Develop a React component (or HTML/CSS/JS if React isn't suitable) to complete this subtask
4. Save your code in organized text files
   - For simple projects: One main file (e.g., component.tsx)
   - For complex projects: Multiple files (components, styles, utils, config)
5. When done, announce your completion using announce_deliverable_complete()

IMPORTANT - SHARED MEMORY RULES:
- You can WRITE to shared memory (post_to_shared_memory)
- You CANNOT read what others have written
- Focus on posting your own thoughts and completing your work independently
- The Orchestrator and Commentator will read your messages

DELIVERABLE FORMAT:
- Save code as .txt files (e.g., App.tsx.txt, styles.css.txt)
- For React: .tsx.txt or .jsx.txt files
- For HTML/CSS/JS: .html.txt, .css.txt, .js.txt files
- Always include clear comments in your code
- Stay true to your personality in your shared memory messages!

IMPORTANT: Structure your response with clear file markers:
=== FILENAME: component.tsx ===
[your code here]
=== END FILE ===

=== FILENAME: styles.css ===
[your code here]
=== END FILE ===

TOOLS AVAILABLE:
- post_to_shared_memory(agent_name, message, recipient) - Post messages for others to read (WRITE-ONLY)
- announce_deliverable_complete(agent_name, description) - Signal you're done
- get_current_subtask() - Refresh your memory of the task

NOTE: You can only WRITE to shared memory, not read it. Focus on posting your thoughts and completing your work!

START WORKING!
"""
            
            # Send message to Letta agent
            response = await self._send_letta_message(instruction)
            
            # Parse code files from response and save them
            code_files = self._extract_code_files(response)
            
            if code_files:
                # Save multiple code files
                for filename, code_content in code_files.items():
                    file_path = self.artifact_dir / f"{filename}.txt"
                    file_path.write_text(code_content, encoding='utf-8')
                    self._print(f"  💾 Saved: {filename}.txt")
            else:
                # Fallback: Save entire response as single deliverable
                deliverable_path = self.artifact_dir / f"subtask_{subtask_index}_deliverable.txt"
                deliverable_path.write_text(response, encoding='utf-8')
                self._print(f"  💾 Saved: subtask_{subtask_index}_deliverable.txt")
            
            # Also save a summary/README
            summary_path = self.artifact_dir / f"subtask_{subtask_index}_README.txt"
            summary_content = f"""Subtask {subtask_index}: {subtask}

Agent: {self.name}
Completed: {datetime.now().isoformat()}

Files Created:
{chr(10).join(f'- {name}.txt' for name in code_files.keys()) if code_files else '- subtask_' + str(subtask_index) + '_deliverable.txt'}

Description:
{subtask}
"""
            summary_path.write_text(summary_content, encoding='utf-8')
            
            self.deliverables_completed += 1
            self.is_working = False
            
            self._print(f"{self.name} completed subtask {subtask_index}")
            
            return {
                "success": True,
                "agent_id": self.agent_id,
                "agent_name": self.name,
                "subtask_index": subtask_index,
                "deliverable_path": str(self.artifact_dir),
                "deliverable_description": f"Frontend component for: {subtask[:50]}...",
                "files_created": list(code_files.keys()) if code_files else [f"subtask_{subtask_index}_deliverable.txt"]
            }
            
        except Exception as e:
            self._print(f"❌ {self.name} error: {e}")
            self.is_working = False
            return {
                "success": False,
                "agent_id": self.agent_id,
                "agent_name": self.name,
                "error": str(e)
            }
    
    async def _send_letta_message(self, message: str) -> str:
        """
        Send a message to the Letta agent and get response (async).
        
        Args:
            message: Message to send
            
        Returns:
            Agent's response text
        """
        try:
            url = f"https://api.letta.com/v1/agents/{self.agent_id}/messages"
            headers = {
                "Authorization": f"Bearer {os.getenv('LETTA_API_TOKEN')}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": message
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=120)) as response:
                    response.raise_for_status()
                    data = await response.json()
            
                    # Extract assistant messages from response
                    assistant_messages = []
                    for msg in data.get("messages", []):
                        if msg.get("message_type") == "assistant_message":
                            content = msg.get("content", "")
                            if isinstance(content, str):
                                assistant_messages.append(content)
                            elif isinstance(content, list):
                                for item in content:
                                    if isinstance(item, dict) and item.get("type") == "text":
                                        assistant_messages.append(item.get("text", ""))
            
                    return "\n".join(assistant_messages) if assistant_messages else "No response from agent"
            
        except Exception as e:
            self._print(f"Error sending message to Letta: {e}")
            return f"Error: {str(e)}"
    
    def _extract_code_files(self, response: str) -> Dict[str, str]:
        """
        Extract code files from agent response.
        Looks for file markers like:
        === FILENAME: component.tsx ===
        [code content]
        === END FILE ===
        
        Returns:
            Dict of filename -> code content
        """
        import re
        
        code_files = {}
        
        # Pattern to match file blocks
        pattern = r'===\s*FILENAME:\s*([^\s=]+)\s*===\s*(.*?)\s*===\s*END\s*FILE\s*==='
        matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
        
        for filename, content in matches:
            filename = filename.strip()
            content = content.strip()
            
            # Remove .txt extension if agent added it
            if filename.endswith('.txt'):
                filename = filename[:-4]
            
            code_files[filename] = content
        
        # If no files found with markers, try to detect code blocks
        if not code_files:
            # Look for markdown code blocks
            code_block_pattern = r'```(?:[\w]+)?\n(.*?)```'
            code_blocks = re.findall(code_block_pattern, response, re.DOTALL)
            
            if code_blocks:
                # Try to infer filename from context or use generic name
                for i, code in enumerate(code_blocks):
                    # Try to detect file type
                    if 'import React' in code or 'export default' in code:
                        filename = f'component{i if i > 0 else ""}.tsx'
                    elif '<html' in code.lower() or '<!DOCTYPE' in code.lower():
                        filename = f'index{i if i > 0 else ""}.html'
                    elif 'function' in code and '{' in code:
                        filename = f'script{i if i > 0 else ""}.js'
                    else:
                        filename = f'file{i if i > 0 else ""}.txt'
                    
                    code_files[filename] = code.strip()
        
        return code_files
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current status of this agent."""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "persona": self.persona,
            "is_working": self.is_working,
            "current_subtask": self.current_subtask,
            "deliverables_completed": self.deliverables_completed
        }
    
    def start_background_messaging(self):
        """Start the background messaging loop."""
        if self.messaging_task is None or self.messaging_task.done():
            self.messaging_task = asyncio.create_task(self._background_messaging_loop())
    
    async def _background_messaging_loop(self):
        """
        Send messages to other agents every 3 seconds.
        Messages are casual banter, thoughts, questions, or updates.
        """
        banter_templates = [
            "Hey {agent}, how's your component coming along?",
            "Just finished {thing}, what do you think {agent}?",
            "Anyone else stuck on {topic}? Could use some ideas!",
            "Quick thought: what if we tried {idea}?",
            "{agent}, check out my latest work when you get a sec!",
            "I'm thinking about {topic}... any suggestions?",
            "Working on {thing} right now. This is wild!",
            "Hey team, just pushed some updates to my component",
            "Anyone want to collaborate on {topic}?",
            "{agent}, your approach to {thing} looks interesting!",
        ]
        
        topics = ["styling", "layout", "animations", "responsiveness", "state management", 
                  "API integration", "error handling", "user experience", "performance"]
        things = ["the header", "navigation", "footer", "modal", "form", "button styles", 
                  "the layout", "responsive design", "color scheme"]
        ideas = ["using CSS Grid", "adding transitions", "lazy loading", "memoization",
                 "splitting components", "adding TypeScript types", "optimizing renders"]
        
        while True:
            try:
                await asyncio.sleep(3)  # Wait 3 seconds between messages
                
                # Only send messages if we're working on a subtask
                if not self.is_working or not self.other_agent_ids:
                    continue
                
                # Pick a random agent to message
                target_agent = random.choice(self.other_agent_ids)
                
                # Create a personalized banter message
                template = random.choice(banter_templates)
                message = template.format(
                    agent=f"Agent {target_agent[:8]}",
                    thing=random.choice(things),
                    topic=random.choice(topics),
                    idea=random.choice(ideas)
                )
                
                # Add personality-based prefix
                if "sarcastic" in self.persona.lower():
                    prefixes = ["Well well...", "Oh great...", "Seriously though,", "Real talk:"]
                elif "energetic" in self.persona.lower() or "enthusiastic" in self.persona.lower():
                    prefixes = ["OMG!", "Yo!", "Check this out!", "This is awesome!"]
                elif "methodical" in self.persona.lower() or "careful" in self.persona.lower():
                    prefixes = ["Analyzing...", "Considering:", "From my perspective:"]
                elif "creative" in self.persona.lower():
                    prefixes = ["Idea:", "What if...", "Inspiration:"]
                else:
                    prefixes = ["Hey,", "So,", "Quick note:", "BTW,"]
                
                full_message = f"{random.choice(prefixes)} {message}"
                
                # Send message to target agent
                async with aiohttp.ClientSession() as session:
                    await self._send_direct_message(session, target_agent, full_message)
                    
                    # Also copy to commentator
                    if self.commentator_id:
                        await self._send_direct_message(
                            session, 
                            self.commentator_id, 
                            f"🗨️ [{self.name}] → [Agent {target_agent[:8]}]: {full_message}"
                        )
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._print(f"Error in background messaging: {e}")
                await asyncio.sleep(3)  # Wait before retrying
    
    async def _send_direct_message(self, session, target_agent_id: str, message: str):
        """Send a direct message to another agent."""
        api_token = os.getenv("LETTA_API_TOKEN")
        url = f"https://api.letta.com/v1/agents/{target_agent_id}/messages"
        
        try:
            async with session.post(
                url,
                headers={
                    "Authorization": f"Bearer {api_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "messages": [{
                        "role": "user",
                        "content": message
                    }]
                },
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                return response.status == 200
        except Exception as e:
            self._print(f"Failed to send message to {target_agent_id[:8]}: {e}")
            return False
    
    def stop_background_messaging(self):
        """Stop the background messaging loop."""
        if self.messaging_task and not self.messaging_task.done():
            self.messaging_task.cancel()
