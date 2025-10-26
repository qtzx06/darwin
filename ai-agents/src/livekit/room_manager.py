"""
LiveKit Room Manager - Creates and manages LiveKit rooms for battles
Handles room creation, token generation, and participant management
"""

import asyncio
import time
from typing import Dict, Any, Optional
from livekit import api
from livekit import rtc
from config.livekit_config import livekit_config

class LiveKitRoomManager:
    """Manages LiveKit rooms for voice commentary battles"""
    
    def __init__(self):
        self.config = livekit_config
        self.active_rooms: Dict[str, Dict[str, Any]] = {}
        self.api_client = None
        
        if not self.config.is_configured():
            print("⚠️ LiveKit not configured - voice features disabled")
    
    def _ensure_api_client(self):
        """Initialize API client if not already done"""
        if self.api_client is None and self.config.is_configured():
            self.api_client = api.LiveKitAPI(
                url=self.config.url,
                api_key=self.config.api_key,
                api_secret=self.config.api_secret
            )
    
    def is_available(self) -> bool:
        """Check if LiveKit is available"""
        return self.config.is_configured()
    
    async def create_battle_room(self, project_id: str) -> Dict[str, Any]:
        """Create a new LiveKit room for a battle"""
        if not self.is_available():
            return {
                "success": False,
                "error": "LiveKit not configured",
                "room_name": None,
                "access_token": None
            }
        
        self._ensure_api_client()
        
        try:
            room_name = self.config.get_room_name(project_id)
            
            # Create room via LiveKit API (simplified for now)
            # Note: Rooms are created automatically when first participant joins
            room_info = {"name": room_name}
            
            # Generate access token for commentator
            commentator_token = api.AccessToken(self.config.api_key, self.config.api_secret)
            commentator_token.with_identity("commentator")
            commentator_token.with_name("AI Commentator")
            commentator_token.with_grants(
                api.VideoGrants(
                    room_join=True,
                    room=room_name,
                    can_publish=True,
                    can_subscribe=True
                )
            )
            
            # Store room info
            self.active_rooms[room_name] = {
                "project_id": project_id,
                "room_name": room_name,
                "created_at": time.time(),
                "participants": [],
                "commentator_token": commentator_token.to_jwt(),
                "status": "active"
            }
            
            print(f"✅ Created LiveKit room: {room_name}")
            
            return {
                "success": True,
                "room_name": room_name,
                "commentator_token": commentator_token.to_jwt(),
                "room_url": self.config.url,  # Just base URL, room name passed separately via token
                "message": f"Room {room_name} created successfully"
            }
            
        except Exception as e:
            print(f"❌ Failed to create LiveKit room: {e}")
            return {
                "success": False,
                "error": str(e),
                "room_name": None,
                "access_token": None
            }
    
    async def generate_spectator_token(self, room_name: str, user_name: str) -> Dict[str, Any]:
        """Generate access token for spectator to join room"""
        if not self.is_available():
            return {
                "success": False,
                "error": "LiveKit not configured"
            }
        
        if room_name not in self.active_rooms:
            return {
                "success": False,
                "error": f"Room {room_name} not found"
            }
        
        self._ensure_api_client()
        
        try:
            # Generate spectator token
            spectator_token = api.AccessToken(self.config.api_key, self.config.api_secret)
            spectator_token.with_identity(user_name)
            spectator_token.with_name(user_name)
            spectator_token.with_grants(
                api.VideoGrants(
                    room_join=True,
                    room=room_name,
                    can_publish=False,  # Spectators can't publish
                    can_subscribe=True
                )
            )
            
            # Add participant to room info
            self.active_rooms[room_name]["participants"].append({
                "name": user_name,
                "joined_at": time.time(),
                "role": "spectator"
            })
            
            return {
                "success": True,
                "access_token": spectator_token.to_jwt(),
                "room_url": f"{self.config.url}/{room_name}",
                "message": f"Token generated for {user_name}"
            }
            
        except Exception as e:
            print(f"❌ Failed to generate spectator token: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_room_status(self, room_name: str) -> Dict[str, Any]:
        """Get current room status and participant info"""
        if room_name not in self.active_rooms:
            return {
                "success": False,
                "error": f"Room {room_name} not found"
            }
        
        room_info = self.active_rooms[room_name]
        
        self._ensure_api_client()
        
        try:
            # Get room info from LiveKit API
            room_details = await self.api_client.room.list_rooms(names=[room_name])
            
            if room_details.rooms:
                livekit_room = room_details.rooms[0]
                return {
                    "success": True,
                    "room_name": room_name,
                    "project_id": room_info["project_id"],
                    "status": room_info["status"],
                    "participant_count": len(livekit_room.num_participants),
                    "participants": room_info["participants"],
                    "created_at": room_info["created_at"],
                    "duration": time.time() - room_info["created_at"]
                }
            else:
                return {
                    "success": False,
                    "error": "Room not found in LiveKit"
                }
                
        except Exception as e:
            print(f"❌ Failed to get room status: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def close_room(self, room_name: str) -> Dict[str, Any]:
        """Close a battle room"""
        if room_name not in self.active_rooms:
            return {
                "success": False,
                "error": f"Room {room_name} not found"
            }
        
        self._ensure_api_client()
        
        try:
            # Delete room via LiveKit API
            await self.api_client.room.delete_room(room_name)
            
            # Remove from active rooms
            del self.active_rooms[room_name]
            
            print(f"✅ Closed LiveKit room: {room_name}")
            
            return {
                "success": True,
                "message": f"Room {room_name} closed successfully"
            }
            
        except Exception as e:
            print(f"❌ Failed to close room: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_active_rooms(self) -> Dict[str, Any]:
        """Get list of all active rooms"""
        return {
            "success": True,
            "rooms": list(self.active_rooms.keys()),
            "count": len(self.active_rooms)
        }
    
    async def cleanup_expired_rooms(self):
        """Clean up rooms that have been inactive for too long"""
        current_time = time.time()
        expired_rooms = []
        
        for room_name, room_info in self.active_rooms.items():
            if current_time - room_info["created_at"] > self.config.room_timeout:
                expired_rooms.append(room_name)
        
        for room_name in expired_rooms:
            await self.close_room(room_name)
            print(f"🧹 Cleaned up expired room: {room_name}")
    
    def get_room_for_project(self, project_id: str) -> Optional[str]:
        """Get room name for a specific project"""
        for room_name, room_info in self.active_rooms.items():
            if room_info["project_id"] == project_id:
                return room_name
        return None

# Global room manager instance
room_manager = LiveKitRoomManager()
