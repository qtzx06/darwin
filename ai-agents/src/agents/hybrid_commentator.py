"""
Hybrid Commentator Agent
Generates progress updates during task execution
"""
from typing import Dict
from datetime import datetime
from pathlib import Path

from ..core.shared_memory import SharedMemory
from ..core.message_system import MessageBroker
from ..core.live_feed import get_live_feed, LiveFeedEvent


class HybridCommentator:
    """
    Commentator reads summaries from all 4 dev agents and synthesizes
    a narrative for the user. Acts as the "sports commentator" of the dev process.
    """
    
    def __init__(
        self,
        letta_agent_id: str,
        letta_client,
        shared_memory: SharedMemory,
        message_broker: MessageBroker,
        logger=None
    ):
        self.agent_id = letta_agent_id
        self.letta_client = letta_client
        self.shared_memory = shared_memory
        self.message_broker = message_broker
        self.logger = logger
        
        # Live feed for real-time commentary
        self.live_feed = get_live_feed()
        self.live_commentary_buffer = []
        
        # Live files for streaming updates
        self.live_dir = Path("live")
        self.live_dir.mkdir(exist_ok=True)
        self.live_commentary_file = self.live_dir / "commentary.txt"
        
        # Clear live file on init
        self.live_commentary_file.write_text("🎙️ DARWIN LIVE COMMENTARY\n" + "="*60 + "\n\n", encoding='utf-8')

        
        # Subscribe to live feed
        self.live_feed.subscribe(self._handle_live_event)
    
    async def generate_progress_commentary(self, subtask_id: int) -> str:
        """
        Generate and print commentary about overall progress based on buffered events.
        Called by orchestrator after each subtask completes.
        """
        try:
            # Count events by type
            events_by_agent = {}
            for event in self.live_commentary_buffer:
                agent = event['agent_name']
                if agent not in events_by_agent:
                    events_by_agent[agent] = []
                events_by_agent[agent].append(event['event_type'])
            
            # Generate simple progress update
            teams_completed = len([a for a in events_by_agent if 'review_complete' in events_by_agent[a]])
            commentary = f"\n📊 Subtask {subtask_id} Progress: {teams_completed}/4 teams completed their work\n"
            
            # Print to console
            print(commentary)
            
            # Write to live file
            self._write_to_live_file(commentary)
            
            return commentary
        except Exception as e:
            return ""
    
    async def _handle_live_event(self, event: LiveFeedEvent):
        """
        Handle incoming live events - just store them for later analysis.
        Commentator reports on OVERALL progress, not individual events.
        """
        try:
            # Just buffer the events for periodic analysis
            self.live_commentary_buffer.append({
                "timestamp": event.timestamp,
                "event_type": event.event_type,
                "agent_name": event.agent_name,
                "content": event.content
            })
        except Exception as e:
            pass  # Silently handle errors
    
    def _write_to_live_file(self, commentary: str):
        """Append commentary to live file for real-time viewing."""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            with open(self.live_commentary_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {commentary}\n")
        except Exception as e:
            pass  # Silently handle file write errors
    
    async def clear_live_buffer(self):
        """Clear live commentary buffer for new subtask."""
        self.live_commentary_buffer.clear()
    
    async def monitor_and_comment_on_teams(self, subtask_id: int, dev_agents: list):
        """
        Actively monitor team conversations and generate commentary.
        Called periodically while teams are working.
        """
        try:
            conversations_dir = Path("live/conversations")
            if not conversations_dir.exists():
                return
            
            commentary_parts = []
            commentary_parts.append(f"\n🎙️ LIVE UPDATE - Subtask {subtask_id}")
            commentary_parts.append(f"{'-'*60}")
            
            # Check each team's live conversation file
            for agent in dev_agents:
                conv_file = conversations_dir / f"{agent.agent_id}_subtask{subtask_id}.txt"
                
                if conv_file.exists():
                    try:
                        content = conv_file.read_text(encoding='utf-8')
                        # Count messages (rough estimate)
                        message_count = content.count('\n\n')
                        
                        # Extract last few lines for context
                        lines = content.strip().split('\n')
                        recent_activity = lines[-3:] if len(lines) >= 3 else lines
                        
                        commentary_parts.append(f"\n{agent.name}:")
                        commentary_parts.append(f"  Messages: ~{message_count}")
                        commentary_parts.append(f"  Recent: {recent_activity[-1][:80]}..." if recent_activity else "  Starting...")
                    except Exception as e:
                        commentary_parts.append(f"\n{agent.name}: (working...)")
            
            commentary = "\n".join(commentary_parts)
            
            # Print and save commentary
            print(commentary)
            self._write_to_live_file(commentary)
            
            return commentary
            
        except Exception as e:
            return ""
    
    async def generate_final_commentary(self, subtask_id: int, dev_agents: list):
        """
        Generate final commentary after all teams complete their work.
        Reads summaries from shared memory and live conversations.
        """
        try:
            commentary_parts = []
            commentary_parts.append(f"\n🎬 FINAL COMMENTARY - Subtask {subtask_id}")
            commentary_parts.append(f"{'='*60}")
            
            # Read each team's result from shared memory
            for agent in dev_agents:
                result = await self.shared_memory.read(f"subtask_{subtask_id}_result_{agent.agent_id}")
                
                if result and result.get("success"):
                    summary = result.get("summary", "No summary")
                    quality_score = result.get("review_result", {}).get("code_quality_score", "N/A")
                    message_count = result.get("autogen_result", {}).get("message_count", 0)
                    
                    commentary_parts.append(f"\n{agent.name}:")
                    commentary_parts.append(f"  Quality: {quality_score}/10")
                    commentary_parts.append(f"  Messages: {message_count}")
                    commentary_parts.append(f"  Summary: {summary[:100]}...")
            
            commentary_parts.append(f"\n{'='*60}")
            commentary_parts.append("All teams have completed! Check deliverables below.")
            
            commentary = "\n".join(commentary_parts)
            
            # Print and save
            print(commentary)
            self._write_to_live_file(commentary)
            
            return commentary
            
        except Exception as e:
            return ""
