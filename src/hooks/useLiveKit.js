import { useState, useEffect, useRef } from 'react';
import { Room, RoomEvent } from 'livekit-client';

export function useLiveKit(roomUrl, token) {
  const [room, setRoom] = useState(null);
  const [audioStream, setAudioStream] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const audioContextRef = useRef(null);
  const audioDestinationRef = useRef(null);

  useEffect(() => {
    if (!roomUrl || !token) return;

    let currentRoom = null;

    const connectToRoom = async () => {
      try {
        console.log('🔌 [LiveKit] Connecting to room...');
        console.log('   URL:', roomUrl);
        console.log('   Token:', token?.substring(0, 50) + '...');
        
        // Create new room
        currentRoom = new Room({
          adaptiveStream: true,
          dynacast: true,
        });

        // Set up event listeners
        currentRoom.on(RoomEvent.Connected, () => {
          console.log('✅ [LiveKit] Connected to room!');
          console.log('   Local participant:', currentRoom.localParticipant.identity);
          setIsConnected(true);
        });

        currentRoom.on(RoomEvent.Disconnected, () => {
          console.log('❌ [LiveKit] Disconnected from room');
          setIsConnected(false);
        });

        currentRoom.on(RoomEvent.ParticipantConnected, (participant) => {
          console.log('👤 [LiveKit] Participant joined:', participant.identity);
        });

        currentRoom.on(RoomEvent.TrackSubscribed, (track, publication, participant) => {
          console.log('🎵 [LiveKit] Track subscribed!');
          console.log('   Kind:', track.kind);
          console.log('   From:', participant.identity);
          console.log('   Track SID:', track.sid);
          
          if (track.kind === 'audio') {
            console.log('🔊 [LiveKit] Setting up audio track for playback AND visualization...');
            
            // Create audio context if needed
            if (!audioContextRef.current) {
              audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
              audioDestinationRef.current = audioContextRef.current.createMediaStreamDestination();
              console.log('   Created audio context');
            }

            // Resume audio context if suspended (autoplay policy)
            if (audioContextRef.current.state === 'suspended') {
              audioContextRef.current.resume().then(() => {
                console.log('   ✅ Audio context resumed');
              });
            }

            // Get the MediaStreamTrack from the track
            const mediaStreamTrack = track.mediaStreamTrack;
            console.log('   Got MediaStreamTrack');
            
            // Create a MediaStream with this track
            const mediaStream = new MediaStream([mediaStreamTrack]);
            console.log('   Created MediaStream');
            
            // Create media stream source from the track
            const source = audioContextRef.current.createMediaStreamSource(mediaStream);
            source.connect(audioDestinationRef.current);
            source.connect(audioContextRef.current.destination); // Also play it
            console.log('   Connected to audio context');
            
            // Set the audio stream for visualization
            setAudioStream(audioDestinationRef.current.stream);
            console.log('✅ [LiveKit] Audio stream ready for orb!');
            console.log('   Audio track will now play through speakers AND animate the orb!');
          }
        });

        currentRoom.on(RoomEvent.TrackUnsubscribed, (track) => {
          console.log('🔇 [LiveKit] Track unsubscribed:', track.kind);
          if (track.kind === 'audio') {
            track.detach();
          }
        });

        currentRoom.on(RoomEvent.TrackPublished, (publication, participant) => {
          console.log('📡 [LiveKit] Track published by', participant.identity);
          console.log('   Track:', publication.trackName);
        });

        // Connect to room
        await currentRoom.connect(roomUrl, token);
        console.log('✅ [LiveKit] Room connection established');
        setRoom(currentRoom);
        
      } catch (err) {
        console.error('❌ Error connecting to LiveKit:', err);
        setError(err.message);
      }
    };

    connectToRoom();

    // Cleanup
    return () => {
      if (currentRoom) {
        currentRoom.disconnect();
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, [roomUrl, token]);

  return {
    room,
    audioStream,
    isConnected,
    error,
  };
}
