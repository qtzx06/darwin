"""
LiveKit Configuration for Voice Commentary
Handles API credentials and room settings for voice-enabled battles
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LiveKitConfig:
    """Configuration for LiveKit voice commentary system"""
    
    def __init__(self):
        # LiveKit API credentials
        self.api_key = os.getenv("LIVEKIT_API_KEY")
        self.api_secret = os.getenv("LIVEKIT_API_SECRET")
        self.url = os.getenv("LIVEKIT_URL", "wss://your-livekit-server.com")
        
        # Voice settings (using LiveKit Inference models)
        self.tts_model = "openai/tts-1"  # LiveKit Inference TTS model
        self.tts_voice = "onyx"   # Deep, energetic voice
        self.stt_model = "openai/whisper-1"  # LiveKit Inference STT model
        
        # Room settings
        self.room_prefix = "darwin-battle"
        self.max_participants = 50
        self.room_timeout = 3600  # 1 hour
        
        # Validate required credentials
        self._validate_config()
    
    def _validate_config(self):
        """Validate that required credentials are present"""
        missing = []
        
        if not self.api_key:
            missing.append("LIVEKIT_API_KEY")
        if not self.api_secret:
            missing.append("LIVEKIT_API_SECRET")
        
        if missing:
            print(f"⚠️ Missing required environment variables: {', '.join(missing)}")
            print("Please add them to your .env file")
            print("\nExample .env file:")
            print("LIVEKIT_API_KEY=your_livekit_api_key")
            print("LIVEKIT_API_SECRET=your_livekit_api_secret")
            print("LIVEKIT_URL=wss://your-livekit-server.com")
    
    def get_room_name(self, project_id: str) -> str:
        """Generate a unique room name for a battle"""
        return f"{self.room_prefix}-{project_id}"
    
    def is_configured(self) -> bool:
        """Check if all required credentials are present"""
        return all([
            self.api_key,
            self.api_secret
        ])
    
    def get_voice_settings(self) -> dict:
        """Get voice configuration settings"""
        return {
            "tts_model": self.tts_model,
            "tts_voice": self.tts_voice,
            "stt_model": self.stt_model
        }
    
    def get_room_settings(self) -> dict:
        """Get room configuration settings"""
        return {
            "max_participants": self.max_participants,
            "timeout": self.room_timeout,
            "prefix": self.room_prefix
        }

# Global config instance
livekit_config = LiveKitConfig()
