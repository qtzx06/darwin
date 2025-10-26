"""
LiveKit TTS Publisher - Streams ElevenLabs TTS audio to LiveKit room
"""
import asyncio
import os
import requests
from livekit import api, rtc
from io import BytesIO
import numpy as np
import subprocess
import tempfile


class TTSPublisher:
    """Publishes TTS audio to LiveKit room"""
    
    def __init__(self):
        self.livekit_url = os.getenv('LIVEKIT_URL', 'wss://darwin-090g9y58.livekit.cloud')
        self.livekit_api_key = os.getenv('LIVEKIT_API_KEY')
        self.livekit_api_secret = os.getenv('LIVEKIT_API_SECRET')
        self.elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY', 'sk_aa058a975d42a503246daf589cf30d04d4de1e26518acb22')
    
    async def speak_to_room(self, room_name: str, text: str, voice_id: str = 'cgSgspJ2msm6clMCkdW9'):
        """
        Generate TTS audio and stream it to LiveKit room
        
        Args:
            room_name: LiveKit room name
            text: Text to speak
            voice_id: ElevenLabs voice ID
        """
        try:
            print(f"\n{'='*60}")
            print(f"🎙️ STARTING TTS STREAM TO LIVEKIT")
            print(f"{'='*60}")
            print(f"Room: {room_name}")
            print(f"Text: {text[:100]}...")
            print(f"Voice ID: {voice_id}")
            print(f"LiveKit URL: {self.livekit_url}")
            print(f"API Key present: {bool(self.livekit_api_key)}")
            print(f"API Secret present: {bool(self.livekit_api_secret)}")
            
            # Step 1: Generate audio with ElevenLabs
            print(f"\n📝 Step 1: Generating audio with ElevenLabs...")
            audio_data = await self._generate_audio(text, voice_id)
            
            if not audio_data:
                print("❌ Failed to generate audio")
                return False
            
            print(f"✅ Generated {len(audio_data)} bytes of audio")
            
            # Step 2: Create LiveKit room token
            print(f"\n🔑 Step 2: Creating LiveKit token...")
            token = api.AccessToken(self.livekit_api_key, self.livekit_api_secret) \
                .with_identity("tts-bot") \
                .with_name("TTS Publisher Bot") \
                .with_grants(api.VideoGrants(
                    room_join=True,
                    room=room_name,
                    can_publish=True,
                    can_subscribe=False,  # TTS bot doesn't need to subscribe
                )).to_jwt()
            
            print(f"✅ Token created: {token[:50]}...")
            
            # Step 3: Connect to room and publish audio
            print(f"\n🔌 Step 3: Connecting to LiveKit room...")
            room = rtc.Room()
            
            await room.connect(self.livekit_url, token)
            print(f"✅ Connected to room: {room_name}")
            print(f"   Participants: {len(room.remote_participants)}")
            
            # Step 4: Decode MP3 to PCM audio data using ffmpeg
            print(f"\n🎵 Step 4: Decoding MP3 to PCM using ffmpeg...")
            
            # Save MP3 to temp file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as mp3_file:
                mp3_file.write(audio_data)
                mp3_path = mp3_file.name
            
            # Use ffmpeg to convert MP3 to raw PCM (16-bit, 24kHz, mono)
            try:
                result = subprocess.run([
                    'ffmpeg', '-i', mp3_path,
                    '-f', 's16le',  # 16-bit PCM
                    '-acodec', 'pcm_s16le',
                    '-ar', '24000',  # 24kHz sample rate
                    '-ac', '1',  # Mono
                    '-'  # Output to stdout
                ], capture_output=True, check=True)
                
                pcm_bytes = result.stdout
                pcm_data = np.frombuffer(pcm_bytes, dtype=np.int16)
                
                print(f"✅ Decoded {len(pcm_data)} samples at 24kHz")
                print(f"   Duration: {len(pcm_data) / 24000:.2f} seconds")
                
            finally:
                # Clean up temp file
                os.unlink(mp3_path)
            
            # Step 5: Create audio source and track
            print(f"\n🎵 Step 5: Creating audio track...")
            audio_source = rtc.AudioSource(sample_rate=24000, num_channels=1)
            track = rtc.LocalAudioTrack.create_audio_track("commentary", audio_source)
            print(f"✅ Audio track created")
            
            # Publish the track
            print(f"\n📡 Step 6: Publishing track to room...")
            options = rtc.TrackPublishOptions()
            options.source = rtc.TrackSource.SOURCE_MICROPHONE
            
            publication = await room.local_participant.publish_track(track, options)
            print(f"✅ Track published!")
            print(f"   Track SID: {publication.sid}")
            print(f"   Track name: {publication.name}")
            
            # Step 7: Stream PCM data to track
            print(f"\n🎤 Step 7: Streaming audio data...")
            # Stream in chunks (480 samples = 20ms at 24kHz)
            chunk_size = 480
            for i in range(0, len(pcm_data), chunk_size):
                chunk = pcm_data[i:i+chunk_size]
                # Pad last chunk if needed
                if len(chunk) < chunk_size:
                    chunk = np.pad(chunk, (0, chunk_size - len(chunk)))
                # Convert to AudioFrame
                frame = rtc.AudioFrame.create(24000, 1, chunk)
                await audio_source.capture_frame(frame)
                # Small delay to match real-time playback
                await asyncio.sleep(0.02)  # 20ms
            
            print(f"✅ Audio streaming complete!")
            
            # Wait a bit before disconnecting
            print(f"\n⏳ Step 8: Waiting for audio to finish playing...")
            await asyncio.sleep(2)
            
            # Cleanup
            print(f"\n🧹 Step 7: Cleaning up...")
            await room.disconnect()
            print(f"✅ Disconnected from room")
            
            print(f"\n{'='*60}")
            print(f"✅ TTS STREAM COMPLETE")
            print(f"{'='*60}\n")
            
            return True
            
        except Exception as e:
            print(f"\n{'='*60}")
            print(f"❌ ERROR IN TTS STREAM")
            print(f"{'='*60}")
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            print(f"{'='*60}\n")
            return False
    
    async def _generate_audio(self, text: str, voice_id: str) -> bytes:
        """Generate audio using ElevenLabs API"""
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_turbo_v2_5",
                "voice_settings": {
                    "stability": 0.3,
                    "similarity_boost": 0.7,
                    "style": 0.8,
                    "use_speaker_boost": True
                }
            }
            
            # Run in thread pool since requests is blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(url, json=data, headers=headers)
            )
            
            if response.status_code == 200:
                return response.content
            else:
                print(f"❌ ElevenLabs API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error generating audio: {e}")
            return None


# Global instance
tts_publisher = TTSPublisher()
