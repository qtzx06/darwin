"""
Voice Pipeline - TTS/STT using LiveKit Inference
Uses LiveKit's unified model interface instead of direct OpenAI API calls
"""

import asyncio
import os
import requests
from typing import Optional, Union
from livekit.agents import AgentSession
from config.livekit_config import livekit_config

class VoicePipeline:
    """Handles TTS/STT operations using LiveKit Inference"""
    
    def __init__(self):
        self.config = livekit_config
        self.session = None
        
        # Initialize LiveKit AgentSession with Inference models
        if self.config.is_configured():
            self.session = AgentSession(
                # Use LiveKit Inference models instead of direct OpenAI
                stt="openai/whisper-1",  # Speech-to-text
                tts="openai/tts-1",      # Text-to-speech
                llm="openai/gpt-4o-mini" # For any LLM needs
            )
            print("✅ Voice pipeline initialized with LiveKit Inference")
        else:
            print("⚠️ LiveKit not configured - voice features disabled")
    
    def is_available(self) -> bool:
        """Check if voice pipeline is available"""
        return self.session is not None
    
    async def text_to_speech(self, text: str, voice: str = None) -> Optional[bytes]:
        """Convert text to speech using ElevenLabs API"""
        try:
            # Get ElevenLabs API key
            api_key = os.getenv('ELEVENLABS_API_KEY')
            if not api_key:
                print("❌ ElevenLabs API key not found")
                return None
            
            # Use the specified voice or default to a known working voice
            voice_id = voice or "21m00Tcm4TlvDq8ikWAM"  # Rachel voice (free)
            
            # Extract just the voice ID part if it has the full format
            if ":" in voice_id:
                voice_id = voice_id.split(":")[1]
            elif "/" in voice_id:
                voice_id = voice_id.split("/")[-1]
            
            # ElevenLabs API endpoint
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_turbo_v2_5",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            # Make request to ElevenLabs
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                return response.content
            else:
                print(f"❌ ElevenLabs API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ ElevenLabs TTS failed: {e}")
            return None
    
    async def speech_to_text(self, audio_data: Union[bytes, bytes]) -> Optional[str]:
        """Convert speech to text using LiveKit Inference STT"""
        if not self.is_available():
            return None
        
        try:
            # Use LiveKit Inference STT
            text = await self.session.stt.transcribe(audio_data)
            return text.strip()
            
        except Exception as e:
            print(f"❌ STT failed: {e}")
            return None
    
    def get_available_voices(self) -> list:
        """Get list of available TTS voices"""
        return ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    
    def get_voice_settings(self) -> dict:
        """Get current voice configuration"""
        return {
            "tts_model": "openai/tts-1",
            "tts_voice": self.config.tts_voice,
            "stt_model": "openai/whisper-1"
        }

# Global voice pipeline instance
voice_pipeline = VoicePipeline()
