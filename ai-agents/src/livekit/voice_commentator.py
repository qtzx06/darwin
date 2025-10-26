"""
Voice Commentator - Connects Letta CommentatorAgent with LiveKit voice
The "nervous system" that bridges intelligent commentary with voice output
"""

import asyncio
import time
from typing import Dict, Any, Optional, Union
from livekit import rtc
from src.livekit.battle_context import BattleContextManager
from src.livekit.voice_pipeline import voice_pipeline
from config.livekit_config import livekit_config

class VoiceCommentator:
    """Wraps Letta CommentatorAgent with voice capabilities"""
    
    def __init__(self, letta_commentator, battle_context: BattleContextManager, room: rtc.Room):
        # Core components
        self.brain = letta_commentator  # Your existing Letta CommentatorAgent
        self.context = battle_context   # BattleContextManager for rich context
        self.room = room               # LiveKit room for audio streaming
        
        # Voice pipeline
        self.voice = voice_pipeline
        
        # Transcript for frontend
        self.transcript = []
        
        # Voice settings
        self.commentator_voice = "onyx"  # Deep, energetic voice
        
        print(f"🎙️ Voice Commentator initialized with Letta agent: {letta_commentator.agent_id}")
    
    async def speak_commentary(self, trigger_event: str, custom_text: str = None) -> Optional[str]:
        """
        Generate and speak commentary for a battle event
        
        Flow: Event → Context → Letta → Text → TTS → Audio
        """
        try:
            # Step 1: Get current battle context
            battle_state = self.context.get_snapshot()
            
            # Step 2: Generate commentary text
            if custom_text:
                commentary_text = custom_text
            else:
                commentary_text = await self._generate_commentary(trigger_event, battle_state)
            
            # Step 3: Speak it via LiveKit
            await self._speak(commentary_text)
            
            return commentary_text
            
        except Exception as e:
            print(f"❌ Voice commentary failed: {e}")
            return None
    
    async def handle_user_question(self, question_text: str) -> Optional[str]:
        """
        User asks question → Letta answers with context
        
        Flow: Question → Context → Letta → Text → TTS → Audio
        """
        try:
            # Step 1: Add question to transcript
            await self._add_to_transcript("User", question_text)
            
            # Step 2: Get current battle context
            battle_state = self.context.get_snapshot()
            
            # Step 3: Ask Letta brain to answer
            answer_text = await self._answer_question(question_text, battle_state)
            
            # Step 4: Speak it via LiveKit
            await self._speak(answer_text)
            
            return answer_text
            
        except Exception as e:
            print(f"❌ User question handling failed: {e}")
            return None
    
    async def _generate_commentary(self, event: str, context: Dict[str, Any]) -> str:
        """Ask Letta to generate commentary for specific events"""
        
        # Build context-rich prompt
        context_summary = self.context.get_context_summary()
        
        prompts = {
            "battle_start": f"{context_summary}\n\nWe're starting a new battle! Give an exciting intro with energy!",
            "round_start": f"{context_summary}\n\nA new round is starting! Comment on the subtask and build excitement!",
            "agent_progress": f"{context_summary}\n\nAgents are making progress! Comment on their work with enthusiasm!",
            "agent_complete": f"{context_summary}\n\nAn agent just finished! React to this development!",
            "winner_announcement": f"{context_summary}\n\nWe have a winner! Make it dramatic and exciting!",
            "battle_end": f"{context_summary}\n\nBattle is complete! Give a final summary with energy!"
        }
        
        prompt = prompts.get(event, f"{context_summary}\n\nProvide exciting commentary about the current battle state!")
        
        # Call Letta API (your existing agent)
        response = self.brain.client.agents.messages.create(
            agent_id=self.brain.agent_id,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Extract text
        for msg in response.messages:
            if hasattr(msg, 'content'):
                return msg.content.strip()
        
        return "The battle continues with excitement!"
    
    async def _answer_question(self, question: str, context: Dict[str, Any]) -> str:
        """Ask Letta to answer user question with battle context"""
        
        context_summary = self.context.get_context_summary()
        
        prompt = f"""
You are an energetic sports commentator for an AI coding battle. Answer this user question with enthusiasm and specific battle details.

{context_summary}

USER QUESTION: {question}

Answer enthusiastically! Reference specific agents, scores, and battle events. Be engaging and informative!
Keep it 1-2 sentences.
"""
        
        # Call Letta (using existing answer_question method if it exists)
        if hasattr(self.brain, 'answer_question'):
            response = await self.brain.answer_question(prompt)
        else:
            # Fallback to direct API call
            response = self.brain.client.agents.messages.create(
                agent_id=self.brain.agent_id,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract response
            for msg in response.messages:
                if hasattr(msg, 'content'):
                    response = msg.content.strip()
                    break
        
        return response if isinstance(response, str) else "Great question! The battle is heating up!"
    
    async def _speak(self, text: str):
        """Convert text to speech and broadcast to LiveKit room"""
        try:
            # Add to transcript
            await self._add_to_transcript("Commentator", text)
            
            # Convert to speech
            audio_bytes = await self.voice.text_to_speech(text, self.commentator_voice)
            
            if audio_bytes:
                # Publish to LiveKit room
                # Note: This is a simplified version - actual LiveKit audio publishing
                # would require proper audio track creation
                print(f"🎙️ Speaking: {text}")
                # TODO: Implement actual LiveKit audio publishing
                # audio_track = LocalAudioTrack.from_bytes(audio_bytes)
                # await self.room.local_participant.publish_track(audio_track)
            else:
                print(f"⚠️ TTS failed for: {text}")
                
        except Exception as e:
            print(f"❌ Speech failed: {e}")
    
    async def _add_to_transcript(self, speaker: str, text: str):
        """Add message to transcript"""
        self.transcript.append({
            "speaker": speaker,
            "text": text,
            "timestamp": time.time(),
            "time_formatted": time.strftime('%H:%M:%S', time.localtime())
        })
        
        # Keep transcript manageable (last 100 messages)
        if len(self.transcript) > 100:
            self.transcript = self.transcript[-100:]
    
    def get_transcript(self) -> list:
        """Get current transcript for frontend"""
        return self.transcript.copy()
    
    def get_latest_messages(self, count: int = 10) -> list:
        """Get latest N messages from transcript"""
        return self.transcript[-count:] if self.transcript else []
    
    async def announce_round_start(self, subtask_title: str, round_num: int):
        """Announce start of new round"""
        announcement = f"Round {round_num} is starting! We're working on: {subtask_title}. Let's see what our agents can do!"
        await self.speak_commentary("round_start", announcement)
    
    async def announce_agent_progress(self, agent_name: str, progress_message: str):
        """Announce agent progress"""
        announcement = f"{agent_name} is making moves! {progress_message}"
        await self.speak_commentary("agent_progress", announcement)
    
    async def announce_winner(self, winner_name: str, reason: str):
        """Announce round winner"""
        announcement = f"And the winner is... {winner_name}! {reason}. What a round!"
        await self.speak_commentary("winner_announcement", announcement)
    
    async def announce_battle_end(self, final_stats: Dict[str, Any]):
        """Announce battle completion"""
        # Get final leaderboard
        context = self.context.get_snapshot()
        leaderboard = self.context._format_leaderboard(context)
        
        announcement = f"Battle complete! Final results: {leaderboard}. What an incredible competition!"
        await self.speak_commentary("battle_end", announcement)
    
    def is_ready(self) -> bool:
        """Check if voice commentator is ready"""
        return (
            self.brain is not None and
            self.context is not None and
            self.room is not None and
            self.voice.is_available()
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get voice commentator status"""
        return {
            "ready": self.is_ready(),
            "letta_agent_id": self.brain.agent_id if self.brain else None,
            "voice_available": self.voice.is_available(),
            "transcript_length": len(self.transcript),
            "commentator_voice": self.commentator_voice,
            "room_connected": self.room is not None
        }
