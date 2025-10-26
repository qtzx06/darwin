"""
Letta Orchestrator Agent
Breaks down tasks into subtasks and coordinates dev agents through shared memory
"""
import asyncio
import aiohttp
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from ..core.shared_memory import SharedMemory
from ..core.message_system import MessageBroker


class LettaOrchestrator:
    """
    Orchestrates the development workflow:
    1. Breaks down user task into subtasks
    2. Posts each subtask to shared memory for dev agents to see
    3. Collects user feedback after each subtask
    4. Coordinates iterations based on feedback
    """
    
    def __init__(
        self,
        letta_agent_id: str,
        letta_client,
        shared_memory: SharedMemory,
        message_broker: MessageBroker,
        dev_agents: List,
        commentator_agent
    ):
        self.agent_id = letta_agent_id
        self.letta_client = letta_client
        self.shared_memory = shared_memory
        self.message_broker = message_broker
        self.dev_agents = dev_agents
        self.commentator = commentator_agent
        
        # Silence mode - only commentator should print
        self.silent = True
        
        # Workflow state
        self.current_project = None
        self.subtasks = []
        self.current_subtask_index = 0
    
    def _print(self, *args, **kwargs):
        """Print only if not in silent mode."""
        if not self.silent:
            print(*args, **kwargs)
    
    def _force_print(self, *args, **kwargs):
        """Always print regardless of silent mode - for user-facing output."""
        print(*args, **kwargs)
    
    async def start_project(self, user_prompt: str) -> Dict[str, Any]:
        """
        Initialize a new project from user prompt.
        Posts project start to shared memory.
        """
        self._force_print(f"\n{'='*70}")
        self._force_print(f"🚀 DARWIN: Starting New Project")
        self._force_print(f"{'='*70}\n")
        self._force_print(f"📋 User Request: {user_prompt}\n")
        
        self.current_project = {
            "prompt": user_prompt,
            "started_at": datetime.now().isoformat(),
            "subtasks": [],
            "feedback_history": []
        }
        
        # Post to shared memory that project is starting
        await self._post_to_shared_memory(
            f"🎬 PROJECT START: {user_prompt}",
            recipient="all"
        )
        
        # Break down task into subtasks using Letta
        self._force_print("🧠 Orchestrator: Breaking down task into subtasks...")
        self.subtasks = await self._break_down_task(user_prompt)
        
        self._force_print(f"\n📊 Identified {len(self.subtasks)} subtasks:")
        for i, subtask in enumerate(self.subtasks, 1):
            self._force_print(f"  {i}. {subtask}")
        self._force_print()
        
        # Store in shared memory
        await self.shared_memory.write("project", self.current_project)
        await self.shared_memory.write("subtasks", self.subtasks)
        
        return {
            "success": True,
            "project": self.current_project,
            "subtasks": self.subtasks
        }
    
    async def _break_down_task(self, user_prompt: str) -> List[str]:
        """
        Use Letta agent to break down task into subtasks.
        """
        try:
            instruction = f"""
You are the Orchestrator. Your job is to break down a user's project request into 3-5 frontend development subtasks.

USER REQUEST:
{user_prompt}

REQUIREMENTS:
- Each subtask should be a distinct, deliverable frontend component or feature
- Subtasks should build on each other progressively
- Think about what the user can review and give feedback on after each step
- Keep subtasks focused on frontend (React, HTML/CSS/JS, UI/UX)

OUTPUT FORMAT:
Return ONLY a JSON array of subtask strings, like:
["Subtask 1 description", "Subtask 2 description", "Subtask 3 description"]

Break down the project now:
"""
            
            response = await self._send_letta_message(instruction)
            
            # Try to parse JSON from response
            try:
                # Look for JSON array in response
                import re
                json_match = re.search(r'\[.*\]', response, re.DOTALL)
                if json_match:
                    subtasks = json.loads(json_match.group())
                    if isinstance(subtasks, list) and len(subtasks) > 0:
                        return subtasks
            except:
                pass
            
            # Fallback: Split by lines and clean up
            lines = [line.strip() for line in response.split('\n') if line.strip()]
            subtasks = []
            for line in lines:
                # Remove numbering, quotes, etc.
                clean = line.strip('0123456789.-"\'[] ')
                if len(clean) > 10:  # Reasonable subtask description
                    subtasks.append(clean)
            
            if len(subtasks) > 0:
                return subtasks[:5]  # Limit to 5 subtasks
            
            # Ultimate fallback
            return [f"Implement {user_prompt}"]
            
        except Exception as e:
            self._print(f"Error breaking down task: {e}")
            return [f"Implement {user_prompt}"]
    
    async def assign_subtask(self, subtask_index: int) -> Dict[str, Any]:
        """
        Assign a subtask to all dev agents via direct messages.
        
        Args:
            subtask_index: Index of subtask to assign (0-based)
            
        Returns:
            Assignment result
        """
        if subtask_index >= len(self.subtasks):
            return {"success": False, "error": "Invalid subtask index"}
        
        subtask = self.subtasks[subtask_index]
        self.current_subtask_index = subtask_index
        
        self._force_print(f"\n{'='*70}")
        self._force_print(f"📋 SUBTASK {subtask_index + 1}/{len(self.subtasks)}")
        self._force_print(f"{'='*70}")
        self._force_print(f"{subtask}\n")
        
        # Send subtask directly to each dev agent via Letta messages
        subtask_message = f"""
📋 NEW SUBTASK ASSIGNED (Subtask {subtask_index + 1}/{len(self.subtasks)}):

{subtask}

Start working on this immediately. Remember to:
1. Discuss with other agents through direct messages
2. Build your component
3. Announce completion when done

The other agents are also working on this simultaneously. May the best implementation win!
"""
        
        # Send to all dev agents in parallel
        async with aiohttp.ClientSession() as session:
            tasks = []
            for agent in self.dev_agents:
                tasks.append(self._send_message_to_agent(session, agent.agent_id, subtask_message))
            
            # Also send to commentator so it knows what's happening
            tasks.append(self._send_message_to_agent(session, self.commentator.agent_id, 
                f"🎬 SUBTASK {subtask_index + 1} STARTED: {subtask}"))
            
            await asyncio.gather(*tasks)
        
        self._force_print("✅ Subtask assigned to all agents\n")
        
        return {
            "success": True,
            "subtask_index": subtask_index,
            "subtask": subtask
        }
    
    async def _send_message_to_agent(self, session, agent_id: str, message: str):
        """Send a direct message to a specific agent."""
        api_token = os.getenv("LETTA_API_TOKEN")
        base_url = "https://api.letta.com"
        
        try:
            async with session.post(
                f"{base_url}/v1/agents/{agent_id}/messages",
                headers={
                    "Authorization": f"Bearer {api_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "messages": [{
                        "role": "user",
                        "content": message
                    }]
                }
            ) as response:
                return response.status == 200
        except Exception as e:
            self._print(f"Error sending message to agent {agent_id[:8]}: {e}")
            return False
    
    async def _post_to_shared_memory(self, message: str, recipient: str = "all"):
        """Post a message to shared memory as the Orchestrator."""
        timestamp = datetime.now().isoformat()
        formatted = f"[{timestamp}] Orchestrator → {recipient}: {message}"
        
        # Append to shared memory conversations
        current_convos = await self.shared_memory.read("conversations") or []
        current_convos.append({
            "timestamp": timestamp,
            "from": "Orchestrator",
            "to": recipient,
            "message": message
        })
        await self.shared_memory.write("conversations", current_convos)
        
        self._print(f"Orchestrator posted: {message[:80]}...")
    
    async def _send_letta_message(self, message: str, max_retries: int = 3) -> str:
        """Send a message to the Letta orchestrator agent with retry logic."""
        import requests
        import time
        
        for attempt in range(max_retries):
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
                
                response = requests.post(url, headers=headers, json=payload)
                
                # Handle rate limit
                if response.status_code == 429:
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) * 10  # 10, 20, 40 seconds
                        self._force_print(f"[yellow]⏳ Rate limited, waiting {wait_time}s...[/yellow]")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        response.raise_for_status()
                
                response.raise_for_status()
                
                data = response.json()
                
                # Extract assistant messages
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
                
                return "\n".join(assistant_messages) if assistant_messages else "No response"
            
            except requests.exceptions.HTTPError as e:
                if attempt < max_retries - 1 and e.response.status_code == 429:
                    continue
                self._print(f"Error sending message to Letta: {e}")
                return f"Error: {str(e)}"
            except Exception as e:
                self._print(f"Error sending message to Letta: {e}")
                return f"Error: {str(e)}"
        
        return "Error: Max retries exceeded"
    
    async def collect_feedback(self) -> Optional[str]:
        """
        Collect user feedback after a subtask completes.
        """
        self._force_print(f"\n{'='*70}")
        self._force_print(f"💬 FEEDBACK TIME")
        self._force_print(f"{'='*70}\n")
        self._force_print("Review the deliverables from all 4 agents.")
        self._force_print("Provide feedback or press Enter to continue:\n")
        
        feedback = input("Your feedback: ").strip()
        
        if feedback:
            # Post feedback to shared memory
            await self._post_to_shared_memory(
                f"📢 USER FEEDBACK: {feedback}",
                recipient="all"
            )
            
            # Store in history
            self.current_project["feedback_history"].append({
                "subtask_index": self.current_subtask_index,
                "feedback": feedback,
                "timestamp": datetime.now().isoformat()
            })
            
            return feedback
        
        return None
