import { Room, RoomEvent, Track } from 'livekit-client';

const LIVEKIT_URL = import.meta.env.VITE_LIVEKIT_URL;

/**
 * Generate access token for LiveKit room via backend
 */
async function generateToken(roomName, participantName) {
  try {
    // Call backend to generate token - use port 3001 where server runs
    const response = await fetch('http://localhost:3001/api/livekit/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        roomName,
        participantName,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('[LiveKit] Token generation failed:', response.status, errorText);
      throw new Error(`Failed to generate token: ${response.status}`);
    }

    const data = await response.json();
    console.log('[LiveKit] Token response:', data);
    console.log('[LiveKit] Token type:', typeof data.token);
    console.log('[LiveKit] Token value:', data.token);

    // Make sure we return just the token string
    const token = typeof data.token === 'string' ? data.token : JSON.stringify(data.token);
    console.log('[LiveKit] Returning token:', token);
    return token;
  } catch (error) {
    console.error('[LiveKit] Token generation failed:', error);
    throw error;
  }
}

/**
 * LiveKit room manager for voice commentary
 */
export class LiveKitVoiceManager {
  constructor() {
    this.room = null;
    this.isConnected = false;
    this.isMuted = false;
    this.agentAudioLevel = 0;
    this.onAgentSpeaking = null;
    this.onAgentTranscript = null;
    this.audioContext = null;
    this.analyser = null;
  }

  /**
   * Connect to LiveKit room
   */
  async connect(roomName, participantName) {
    try {
      console.log(`[LiveKit] Connecting to room: ${roomName} as ${participantName}`);

      // Generate token - MUST await this!
      const token = await generateToken(roomName, participantName);
      console.log('[LiveKit] Token received, connecting to room...');

      // Create room instance
      this.room = new Room({
        adaptiveStream: true,
        dynacast: true,
      });

      // Set up event listeners
      this.setupEventListeners();

      // Connect to room
      await this.room.connect(LIVEKIT_URL, token);

      this.isConnected = true;
      console.log('[LiveKit] Connected successfully');

      return this.room;
    } catch (error) {
      console.error('[LiveKit] Connection failed:', error);
      throw error;
    }
  }

  /**
   * Set up room event listeners
   */
  setupEventListeners() {
    // When agent speaks, detect audio track
    this.room.on(RoomEvent.TrackSubscribed, (track, publication, participant) => {
      console.log(`[LiveKit] Track subscribed:`, {
        participant: participant.identity,
        trackKind: track.kind,
        trackSource: track.source,
      });

      // Check if this is an agent's audio track
      if (track.kind === Track.Kind.Audio && participant.identity.includes('agent')) {
        console.log('[LiveKit] Agent audio track detected');
        this.setupAgentAudioAnalysis(track);
      }
    });

    // Handle participant connection
    this.room.on(RoomEvent.ParticipantConnected, (participant) => {
      console.log(`[LiveKit] Participant connected: ${participant.identity}`);
    });

    // Handle data messages (for transcripts)
    this.room.on(RoomEvent.DataReceived, (payload, participant) => {
      try {
        const decoder = new TextDecoder();
        const message = decoder.decode(payload);
        const data = JSON.parse(message);

        console.log('[LiveKit] Data received:', data);

        // Handle transcript data
        if (data.type === 'transcript' && this.onAgentTranscript) {
          this.onAgentTranscript(data.text, data.isFinal || false);
        }
      } catch (error) {
        console.error('[LiveKit] Failed to parse data:', error);
      }
    });

    // Handle disconnection
    this.room.on(RoomEvent.Disconnected, () => {
      console.log('[LiveKit] Disconnected from room');
      this.isConnected = false;
    });
  }

  /**
   * Set up audio analysis for agent's voice (for visualizer)
   */
  setupAgentAudioAnalysis(audioTrack) {
    try {
      // Get media stream from track
      const mediaStream = new MediaStream([audioTrack.mediaStreamTrack]);

      // Create audio context and analyser
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 256;

      // Connect audio source
      const source = this.audioContext.createMediaStreamSource(mediaStream);
      source.connect(this.analyser);

      // Start analyzing audio levels
      this.startAudioLevelMonitoring();

      console.log('[LiveKit] Agent audio analysis setup complete');
    } catch (error) {
      console.error('[LiveKit] Failed to setup audio analysis:', error);
    }
  }

  /**
   * Monitor audio levels for visualizer
   */
  startAudioLevelMonitoring() {
    const bufferLength = this.analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const updateLevel = () => {
      if (!this.analyser || !this.isConnected) return;

      this.analyser.getByteFrequencyData(dataArray);

      // Calculate average audio level
      const sum = dataArray.reduce((a, b) => a + b, 0);
      const average = sum / bufferLength;
      this.agentAudioLevel = average / 255; // Normalize to 0-1

      // Notify callback if agent is speaking
      if (this.onAgentSpeaking && this.agentAudioLevel > 0.05) {
        this.onAgentSpeaking(this.agentAudioLevel);
      }

      requestAnimationFrame(updateLevel);
    };

    updateLevel();
  }

  /**
   * Enable/disable microphone
   */
  async setMicrophoneEnabled(enabled) {
    if (!this.room) {
      console.warn('[LiveKit] Room not connected');
      return;
    }

    try {
      await this.room.localParticipant.setMicrophoneEnabled(enabled);
      this.isMuted = !enabled;
      console.log(`[LiveKit] Microphone ${enabled ? 'enabled' : 'disabled'}`);
    } catch (error) {
      console.error('[LiveKit] Failed to toggle microphone:', error);
    }
  }

  /**
   * Send data message to agent
   */
  sendMessage(message) {
    if (!this.room || !this.isConnected) {
      console.warn('[LiveKit] Cannot send message, not connected');
      return;
    }

    try {
      const encoder = new TextEncoder();
      const data = encoder.encode(JSON.stringify(message));
      this.room.localParticipant.publishData(data, { reliable: true });
      console.log('[LiveKit] Message sent:', message);
    } catch (error) {
      console.error('[LiveKit] Failed to send message:', error);
    }
  }

  /**
   * Get current audio level (for visualizer)
   */
  getAudioLevel() {
    return this.agentAudioLevel;
  }

  /**
   * Disconnect from room
   */
  async disconnect() {
    if (this.room) {
      await this.room.disconnect();
      this.room = null;
      this.isConnected = false;

      if (this.audioContext) {
        this.audioContext.close();
        this.audioContext = null;
        this.analyser = null;
      }

      console.log('[LiveKit] Disconnected');
    }
  }
}
