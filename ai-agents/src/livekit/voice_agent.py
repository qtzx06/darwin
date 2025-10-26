"""
Voice Agent - Individual agent voice wrapper for personality-driven responses.
"""

import asyncio
import time
from typing import Dict, Any, Optional
from letta_client import Letta
from src.livekit.agent_voices import get_agent_voice_config, get_agent_prompt_template, calculate_emotion_level

class VoiceAgent:
    """Individual agent voice wrapper for personality-driven responses."""
    
    def __init__(self, agent_name: str, letta_agent_id: str, letta_client: Letta):
        self.agent_name = agent_name
        self.letta_agent_id = letta_agent_id
        self.client = letta_client
        self.voice_config = get_agent_voice_config(agent_name)
        
    async def react_to_event(self, event_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate SHORT personality-driven reaction to event.
        
        Args:
            event_type: Type of event (code_submitted, won_round, lost_round, etc.)
            context: Battle context and event details
            
        Returns:
            Dict with response_text and emotion_level
        """
        try:
            # Build personality-specific prompt
            prompt_template = get_agent_prompt_template(self.agent_name, event_type)
            full_prompt = f"{prompt_template}\n\nContext: {context}"
            
            # Send message to Letta agent
            response = self.client.agents.messages.create(
                agent_id=self.letta_agent_id,
                messages=[{"role": "user", "content": full_prompt}]
            )
            
            # Extract response content
            response_text = f"Agent {self.agent_name} reacts..."
            for msg in response.messages:
                if hasattr(msg, 'content'):
                    response_text = msg.content.strip()
                    break
            
            # Calculate emotion level based on battle state
            battle_state = {
                "agent_stats": context.get("agent_stats", {}),
                "total_rounds": context.get("total_rounds", 1),
                "event_type": event_type
            }
            emotion_level = calculate_emotion_level(self.agent_name, battle_state)
            
            return {
                "agent_name": self.agent_name,
                "response_text": response_text,
                "emotion_level": emotion_level,
                "voice_id": self.voice_config["voice_id"],
                "timestamp": time.time()
            }
            
        except Exception as e:
            print(f"❌ Agent {self.agent_name} reaction error: {e}")
            return {
                "agent_name": self.agent_name,
                "response_text": f"Agent {self.agent_name}: 'Battle time!'",
                "emotion_level": 0.5,
                "voice_id": self.voice_config["voice_id"],
                "timestamp": time.time()
            }
    
    async def answer_question(self, question: str, battle_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Answer user question with personality.
        
        Args:
            question: User's question
            battle_context: Current battle state
            
        Returns:
            Dict with response_text and emotion_level
        """
        try:
            # Build personality-specific prompt
            prompt_template = get_agent_prompt_template(self.agent_name, "user_question")
            full_prompt = f"{prompt_template}\n\nQuestion: {question}\n\nContext: {battle_context}"
            
            # Send message to Letta agent
            response = self.client.agents.messages.create(
                agent_id=self.letta_agent_id,
                messages=[{"role": "user", "content": full_prompt}]
            )
            
            # Extract response content
            response_text = f"Agent {self.agent_name} is thinking..."
            for msg in response.messages:
                if hasattr(msg, 'content'):
                    response_text = msg.content.strip()
                    break
            
            # Calculate emotion level based on battle state
            battle_state = {
                "agent_stats": battle_context.get("agent_stats", {}),
                "total_rounds": battle_context.get("total_rounds", 1),
                "event_type": "user_question"
            }
            emotion_level = calculate_emotion_level(self.agent_name, battle_state)
            
            return {
                "agent_name": self.agent_name,
                "response_text": response_text,
                "emotion_level": emotion_level,
                "voice_id": self.voice_config["voice_id"],
                "timestamp": time.time()
            }
            
        except Exception as e:
            print(f"❌ Agent {self.agent_name} question error: {e}")
            return {
                "agent_name": self.agent_name,
                "response_text": f"Agent {self.agent_name}: 'Ready to battle!'",
                "emotion_level": 0.5,
                "voice_id": self.voice_config["voice_id"],
                "timestamp": time.time()
            }
    
    def get_voice_settings(self, emotion_level: float) -> Dict[str, Any]:
        """
        Get ElevenLabs voice settings with emotion control.
        
        Args:
            emotion_level: Emotion level (0.0-1.0) for style parameter
            
        Returns:
            Dict with ElevenLabs voice settings
        """
        return {
            "stability": 0.3,
            "similarity_boost": 0.7,
            "style": emotion_level,  # Dynamic emotion based on battle state
            "use_speaker_boost": True
        }
    
    def get_color(self) -> str:
        """Get agent's color for UI display."""
        return self.voice_config["color"]
    
    def get_personality(self) -> str:
        """Get agent's personality type."""
        return self.voice_config["personality"]
    
    def get_speech_style(self) -> str:
        """Get agent's speech style description."""
        return self.voice_config["speech_style"]
