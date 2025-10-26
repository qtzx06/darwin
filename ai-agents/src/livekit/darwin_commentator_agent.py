#!/usr/bin/env python3
"""
Darwin AI Battle Commentator Agent using LiveKit Agents Framework
This is how we SHOULD have built it using the proper LiveKit Agents starter kit
"""

import asyncio
import os
from typing import Optional
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.voice_assistant import VoiceAssistant
from livekit import rtc
from livekit.agents.voice_assistant import VoiceAssistantOptions

# Import our existing components
from src.livekit.battle_context import BattleContextManager
from src.agents.commentator_agent import CommentatorAgent

class DarwinBattleCommentator(VoiceAssistant):
    """Darwin AI Battle Commentator using LiveKit Agents framework"""
    
    def __init__(self, ctx: JobContext, options: VoiceAssistantOptions):
        super().__init__(ctx, options)
        
        # Initialize our battle context
        self.battle_context = BattleContextManager()
        
        # Initialize Letta commentator (our existing brain)
        self.letta_commentator = CommentatorAgent()
        
        # Set up the voice assistant with our custom logic
        self._setup_commentator()
    
    def _setup_commentator(self):
        """Set up the commentator with battle-specific prompts"""
        
        # Custom system prompt for battle commentary
        battle_system_prompt = """
        You are an energetic sports commentator for AI coding battles. 
        You provide live commentary on coding competitions between AI agents.
        
        Your personality:
        - Energetic and enthusiastic
        - Technical but accessible
        - Funny and engaging
        - Always rooting for the underdog
        
        You know about:
        - Current battle state and progress
        - Agent personalities and approaches
        - Code quality and techniques
        - Round winners and leaderboards
        
        Always be engaging and make coding battles exciting!
        """
        
        # Override the default system prompt
        self.system_prompt = battle_system_prompt
    
    async def on_agent_start(self, ctx: JobContext):
        """Called when the agent starts"""
        print("🎙️ Darwin Battle Commentator started!")
        
        # Initialize battle context if we have project info
        project_id = ctx.room.name.replace("darwin-battle-", "")
        if project_id:
            await self.battle_context.initialize_battle(
                project_id, 
                "AI Coding Battle", 
                total_rounds=4
            )
    
    async def on_user_speech_committed(self, ctx: JobContext, user_message: str):
        """Called when user asks a question"""
        print(f"🎤 User asked: {user_message}")
        
        # Get current battle context
        context_summary = self.battle_context.get_context_summary()
        
        # Create context-aware prompt
        prompt = f"""
        {context_summary}
        
        USER QUESTION: {user_message}
        
        Answer enthusiastically! Reference specific agents, scores, and battle events. 
        Be engaging and informative! Keep it 1-2 sentences.
        """
        
        # Use our Letta commentator to generate response
        response = await self.letta_commentator.answer_question(prompt)
        
        # The VoiceAssistant will automatically speak this response
        return response
    
    async def announce_battle_event(self, event_type: str, event_data: dict):
        """Announce battle events with voice"""
        context_summary = self.battle_context.get_context_summary()
        
        prompts = {
            "battle_start": f"{context_summary}\n\nWe're starting a new battle! Give an exciting intro with energy!",
            "round_start": f"{context_summary}\n\nA new round is starting! Comment on the subtask and build excitement!",
            "agent_progress": f"{context_summary}\n\nAgents are making progress! Comment on their work with enthusiasm!",
            "agent_complete": f"{context_summary}\n\nAn agent just finished! React to this development!",
            "winner_announcement": f"{context_summary}\n\nWe have a winner! Make it dramatic and exciting!",
            "battle_end": f"{context_summary}\n\nBattle is complete! Give a final summary with energy!"
        }
        
        prompt = prompts.get(event_type, f"{context_summary}\n\nProvide exciting commentary about the current battle state!")
        
        # Generate commentary using Letta
        commentary = await self.letta_commentator.generate_commentary(prompt)
        
        # Speak the commentary
        await self.say(commentary)
        
        return commentary

# LiveKit Agents entry point
async def entrypoint(ctx: JobContext):
    """Entry point for LiveKit Agents"""
    
    # Create voice assistant options
    options = VoiceAssistantOptions(
        # Use OpenAI for TTS/STT
        tts_provider="openai",
        stt_provider="openai",
        
        # Voice settings
        tts_voice="onyx",  # Deep, energetic voice
        
        # Enable auto-subscribe to user audio
        auto_subscribe=AutoSubscribe.AUDIO_ONLY,
        
        # Custom system prompt
        system_prompt="You are an energetic AI coding battle commentator!"
    )
    
    # Create our custom commentator
    commentator = DarwinBattleCommentator(ctx, options)
    
    # Start the voice assistant
    await commentator.start()

# CLI entry point
if __name__ == "__main__":
    cli.run_app(entrypoint)
