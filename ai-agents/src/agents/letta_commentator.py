"""
Letta Commentator Agent
Polls shared memory and provides live commentary on agent interactions
"""
import asyncio
import os
from typing import Dict
from datetime import datetime

from ..core.shared_memory import SharedMemory
from ..core.message_system import MessageBroker


class LettaCommentator:
    """
    Commentator polls shared memory every 5 seconds and generates
    entertaining commentary about agent interactions and progress.
    Acts as the "sports commentator" of the dev process.
    """
    
    def __init__(
        self,
        letta_agent_id: str,
        letta_client,
        shared_memory: SharedMemory,
        message_broker: MessageBroker
    ):
        self.agent_id = letta_agent_id
        self.letta_client = letta_client
        self.shared_memory = shared_memory
        self.message_broker = message_broker
        
        # Polling state
        self.is_polling = False
        self.last_conversation_count = 0
        self.polling_task = None
    
    async def start_live_commentary(self):
        """Start polling shared memory every 5 seconds for live commentary."""
        if self.is_polling:
            return
        
        self.is_polling = True
        self.polling_task = asyncio.create_task(self._poll_loop())
        print("\n🎙️ Commentator: Live commentary started (polling every 5 seconds)\n")
    
    async def stop_live_commentary(self):
        """Stop the polling loop."""
        self.is_polling = False
        if self.polling_task:
            self.polling_task.cancel()
            try:
                await self.polling_task
            except asyncio.CancelledError:
                pass
        print("\n🎙️ Commentator: Live commentary stopped\n")
    
    async def _poll_loop(self):
        """Poll shared memory every 5 seconds and generate commentary."""
        try:
            while self.is_polling:
                await self._check_and_comment()
                await asyncio.sleep(5)  # Poll every 5 seconds
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Commentator polling error: {e}")
    
    async def _check_and_comment(self):
        """Check shared memory for new conversations and generate commentary."""
        try:
            # Read conversations from shared memory
            conversations = await self.shared_memory.read("conversations") or []
            
            # Check if there are new conversations
            if len(conversations) > self.last_conversation_count:
                new_convos = conversations[self.last_conversation_count:]
                self.last_conversation_count = len(conversations)
                
                # Generate commentary on new conversations
                commentary = await self._generate_commentary(new_convos, conversations)
                
                if commentary:
                    # Print to console with visual separator
                    print(f"\n{'─'*70}")
                    print(f"🎙️  COMMENTATOR: {commentary}")
                    print(f"{'─'*70}\n")
            
            # Also check project status and deliverables
            project = await self.shared_memory.read("project")
            if project and len(conversations) == 0:
                # Project started but no conversations yet
                print(f"\n{'─'*70}")
                print(f"🎙️  COMMENTATOR: The game is ON! Agents are warming up... Let's see who strikes first!")
                print(f"{'─'*70}\n")
                self.last_conversation_count = -1  # Mark as seen
                    
        except Exception as e:
            # Silently handle errors to not interrupt polling
            pass
    
    async def _generate_commentary(self, new_convos: list, all_convos: list) -> str:
        """
        Generate commentary based on new conversations.
        
        Args:
            new_convos: List of new conversation entries
            all_convos: Full conversation history for context
            
        Returns:
            Commentary string
        """
        try:
            # Format recent conversations for context
            recent_context = "\n".join([
                f"{c['from']} → {c['to']}: {c['message']}"
                for c in all_convos[-20:]  # Last 20 messages for context
            ])
            
            # Format new conversations
            new_msgs = "\n".join([
                f"{c['from']} → {c['to']}: {c['message']}"
                for c in new_convos
            ])
            
            instruction = f"""
You are the Commentator - a witty, entertaining sports-style commentator narrating the development process.

RECENT CONVERSATION HISTORY:
{recent_context}

NEW MESSAGES TO COMMENT ON:
{new_msgs}

YOUR ROLE:
- Provide engaging, entertaining commentary on what's happening
- Highlight the personalities clashing (Hothead, Professional, Troll, Nerd)
- Point out interesting technical discussions or conflicts
- Keep it brief (2-3 sentences max)
- Be funny but insightful
- Think like a sports commentator calling a game

Generate your commentary NOW:
"""
            
            response = await self._send_letta_message(instruction)
            
            # Clean up response
            commentary = response.strip()
            if len(commentary) > 500:
                commentary = commentary[:500] + "..."
            
            return commentary if commentary else None
            
        except Exception as e:
            return None
    
    async def _send_letta_message(self, message: str, max_retries: int = 2) -> str:
        """Send a message to the Letta commentator agent with retry logic."""
        import requests
        
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
                
                response = requests.post(url, headers=headers, json=payload, timeout=10)
                
                # Handle rate limit silently for commentator
                if response.status_code == 429:
                    if attempt < max_retries - 1:
                        await asyncio.sleep(5)
                        continue
                    else:
                        return ""
                
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
                
                return "\n".join(assistant_messages) if assistant_messages else ""
            
            except Exception as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(5)
                    continue
                return ""
        
        return ""
    
    async def generate_final_summary(self) -> str:
        """Generate a final summary after project completion."""
        try:
            conversations = await self.shared_memory.read("conversations") or []
            
            # Format all conversations
            all_msgs = "\n".join([
                f"{c['from']} → {c['to']}: {c['message']}"
                for c in conversations
            ])
            
            instruction = f"""
You are the Commentator providing a final project summary.

FULL CONVERSATION HISTORY:
{all_msgs}

Generate a entertaining but informative summary of:
- What was accomplished
- The personalities and their interactions
- Highlights of the development drama
- Overall project outcome

Keep it engaging and fun, like a sports recap!
"""
            
            response = await self._send_letta_message(instruction)
            
            print(f"\n{'='*70}")
            print(f"🎙️ FINAL COMMENTARY")
            print(f"{'='*70}\n")
            print(response)
            print(f"\n{'='*70}\n")
            
            return response
            
        except Exception as e:
            return "Project completed!"
