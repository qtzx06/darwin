import { GoogleGenAI, Modality } from '@google/genai';

const API_KEY = import.meta.env.VITE_GEMINI_API_KEY;

/**
 * Gemini Live API Manager for real-time voice interaction
 */
export class GeminiLiveManager {
  constructor() {
    this.ai = new GoogleGenAI({ apiKey: API_KEY });
    this.session = null;
    this.isConnected = false;
    this.audioContext = null;
    this.analyser = null;
    this.audioWorkletNode = null;
    this.mediaStream = null;
    this.onTranscript = null;
    this.onUserTranscript = null; // User's speech transcription
    this.onAudioLevel = null;
    this.responseQueue = [];
    this.isMicMuted = true; // Microphone mute state (for transcript-mute button)
    this.isOutputMuted = false; // AI voice output mute (for volume button in Commentator)
    this.gainNode = null; // For controlling AI voice volume
  }

  /**
   * Connect to Gemini Live API
   */
  async connect(systemInstruction = 'You are a friendly AI commentator for a coding battle. Provide brief, witty commentary on what the agents are doing. Keep responses under 15 words.') {
    try {
      console.log('[Gemini Live] Connecting to Live API...');

      const config = {
        responseModalities: [Modality.AUDIO],
        systemInstruction,
        voiceConfig: {
          prebuiltVoiceConfig: {
            voiceName: 'Puck' // Fun, energetic voice for commentary
          }
        }
      };

      // Set up callbacks
      const callbacks = {
        onopen: () => {
          console.log('[Gemini Live] Connection opened');
          this.isConnected = true;
        },
        onmessage: (message) => {
          this.handleMessage(message);
        },
        onerror: (error) => {
          console.error('[Gemini Live] Error:', error);
        },
        onclose: (event) => {
          console.log('[Gemini Live] Connection closed:', event.reason);
          this.isConnected = false;
        }
      };

      // Connect to Live API using new native audio model
      this.session = await this.ai.live.connect({
        model: 'gemini-2.5-flash-native-audio-preview-09-2025',
        callbacks,
        config
      });

      console.log('[Gemini Live] Connected successfully');

      // Set up audio context for visualization
      await this.setupAudioVisualization();

      return true;
    } catch (error) {
      console.error('[Gemini Live] Connection failed:', error);
      throw error;
    }
  }

  /**
   * Handle incoming messages from Gemini
   */
  handleMessage(message) {
    this.responseQueue.push(message);

    console.log('[Gemini Live] Message received:', message);

    // If there's audio data, play it and analyze for visualization
    if (message.data) {
      this.playAudioChunk(message.data);
    }

    // Handle Gemini's text response transcripts
    if (message.serverContent?.modelTurn?.parts) {
      const textParts = message.serverContent.modelTurn.parts
        .filter(part => part.text)
        .map(part => part.text)
        .join(' ');

      if (textParts && this.onTranscript) {
        console.log('[Gemini Live] Gemini transcript:', textParts);
        this.onTranscript(textParts);
      }
    }

    // Handle user's speech transcription
    if (message.serverContent?.turnComplete) {
      console.log('[Gemini Live] User turn complete');
    }

    // Check for user transcript in client content
    if (message.clientContent?.turns) {
      for (const turn of message.clientContent.turns) {
        if (turn.role === 'user' && turn.parts) {
          const userText = turn.parts
            .filter(part => part.text)
            .map(part => part.text)
            .join(' ');

          if (userText && this.onUserTranscript) {
            console.log('[Gemini Live] User transcript:', userText);
            this.onUserTranscript(userText);
          }
        }
      }
    }

    // Also check in serverContent for user turns
    if (message.serverContent?.userTurn?.parts) {
      const userText = message.serverContent.userTurn.parts
        .filter(part => part.text)
        .map(part => part.text)
        .join(' ');

      if (userText && this.onUserTranscript) {
        console.log('[Gemini Live] User transcript (from server):', userText);
        this.onUserTranscript(userText);
      }
    }

    // Handle user's speech transcription (from Gemini's understanding)
    if (message.serverContent?.interrupted) {
      console.log('[Gemini Live] User interrupted');
    }

    // Check for user turn transcripts
    if (message.toolCall || message.toolCallCancellation) {
      console.log('[Gemini Live] Tool call:', message);
    }
  }

  /**
   * Set up audio visualization (for the orb)
   */
  async setupAudioVisualization() {
    try {
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 256;

      // Create gain node for volume control (controls Gemini's voice output)
      this.gainNode = this.audioContext.createGain();
      this.gainNode.gain.value = this.isOutputMuted ? 0.0 : 1.0;

      // Create a destination for audio playback that we can also analyze
      const destination = this.audioContext.createMediaStreamDestination();

      // Route: analyser -> gainNode -> destination + speakers
      this.analyser.connect(this.gainNode);
      this.gainNode.connect(destination);
      this.gainNode.connect(this.audioContext.destination);

      // Start monitoring audio levels
      this.startAudioLevelMonitoring();

      console.log('[Gemini Live] Audio visualization setup complete');
    } catch (error) {
      console.error('[Gemini Live] Failed to setup audio visualization:', error);
    }
  }

  /**
   * Play audio chunk from Gemini response
   */
  async playAudioChunk(base64Audio) {
    try {
      if (!this.audioContext) return;

      // Decode base64 audio data
      const binaryString = atob(base64Audio);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }

      // Convert to Int16Array (16-bit PCM)
      const int16Array = new Int16Array(bytes.buffer);

      // Convert to Float32Array for Web Audio API
      const float32Array = new Float32Array(int16Array.length);
      for (let i = 0; i < int16Array.length; i++) {
        float32Array[i] = int16Array[i] / 32768.0; // Normalize to -1.0 to 1.0
      }

      // Create audio buffer (Gemini outputs at 24kHz)
      const audioBuffer = this.audioContext.createBuffer(1, float32Array.length, 24000);
      audioBuffer.getChannelData(0).set(float32Array);

      // Create buffer source and connect to analyser
      const source = this.audioContext.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(this.analyser);

      // Play audio
      source.start();

    } catch (error) {
      console.error('[Gemini Live] Failed to play audio chunk:', error);
    }
  }

  /**
   * Monitor audio levels for visualizer
   */
  startAudioLevelMonitoring() {
    if (!this.analyser) return;

    const bufferLength = this.analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const updateLevel = () => {
      if (!this.analyser || !this.isConnected) return;

      this.analyser.getByteFrequencyData(dataArray);

      // Calculate average audio level
      const sum = dataArray.reduce((a, b) => a + b, 0);
      const average = sum / bufferLength;
      const normalizedLevel = average / 255; // Normalize to 0-1

      // Notify callback if there's significant audio
      if (this.onAudioLevel && normalizedLevel > 0.05) {
        this.onAudioLevel(normalizedLevel);
      }

      requestAnimationFrame(updateLevel);
    };

    updateLevel();
  }

  /**
   * Set up microphone input
   */
  async setupMicrophone() {
    try {
      // Request microphone access
      this.mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true
        }
      });

      console.log('[Gemini Live] Microphone access granted');

      // Set up audio processing for sending to Gemini
      await this.setupAudioProcessing();

      return true;
    } catch (error) {
      console.error('[Gemini Live] Failed to setup microphone:', error);
      throw error;
    }
  }

  /**
   * Set up audio processing to send mic input to Gemini
   */
  async setupAudioProcessing() {
    if (!this.audioContext) {
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }

    const source = this.audioContext.createMediaStreamSource(this.mediaStream);

    // Create script processor to capture audio data
    const bufferSize = 4096;
    const processor = this.audioContext.createScriptProcessor(bufferSize, 1, 1);

    processor.onaudioprocess = (event) => {
      if (this.isMicMuted || !this.isConnected) return;

      const inputData = event.inputBuffer.getChannelData(0);

      // Convert float32 to int16 PCM
      const int16Data = new Int16Array(inputData.length);
      for (let i = 0; i < inputData.length; i++) {
        const s = Math.max(-1, Math.min(1, inputData[i]));
        int16Data[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
      }

      // Convert to base64
      const uint8Data = new Uint8Array(int16Data.buffer);
      const base64Audio = btoa(String.fromCharCode.apply(null, uint8Data));

      // Send to Gemini
      this.sendAudio(base64Audio);
    };

    source.connect(processor);
    processor.connect(this.audioContext.destination);

    console.log('[Gemini Live] Audio processing setup complete');
  }

  /**
   * Send audio to Gemini
   */
  sendAudio(base64Audio) {
    if (!this.session || !this.isConnected) {
      console.warn('[Gemini Live] Cannot send audio - not connected');
      return;
    }

    try {
      console.log('[Gemini Live] Sending audio chunk, length:', base64Audio.length);
      this.session.sendRealtimeInput({
        audio: {
          data: base64Audio,
          mimeType: 'audio/pcm;rate=16000'
        }
      });
    } catch (error) {
      console.error('[Gemini Live] Failed to send audio:', error);
    }
  }

  /**
   * Send text message to Gemini
   */
  sendText(text) {
    if (!this.session || !this.isConnected) {
      console.warn('[Gemini Live] Cannot send text, not connected');
      return;
    }

    try {
      this.session.sendRealtimeInput({
        text: text
      });
      console.log('[Gemini Live] Sent text:', text);
    } catch (error) {
      console.error('[Gemini Live] Failed to send text:', error);
    }
  }

  /**
   * Toggle Gemini's voice OUTPUT (what you hear from Gemini)
   */
  async setOutputMuted(muted) {
    console.log(`[Gemini Live] Setting output muted to: ${muted}`);
    this.isOutputMuted = muted;

    if (this.gainNode) {
      this.gainNode.gain.value = muted ? 0.0 : 1.0;
      console.log(`[Gemini Live] Gemini voice ${muted ? 'muted' : 'unmuted'}`);
    }

    return true;
  }

  /**
   * Toggle microphone INPUT (your mic that Gemini hears)
   */
  async setMicMuted(muted) {
    console.log(`[Gemini Live] Setting mic muted to: ${muted}`);

    if (!muted && !this.mediaStream) {
      // Request microphone permission when unmuting for the first time
      console.log('[Gemini Live] Requesting microphone permission...');
      try {
        await this.setupMicrophone();
        this.isMicMuted = false;
        console.log('[Gemini Live] Microphone unmuted and ready');
        return true;
      } catch (error) {
        console.error('[Gemini Live] Failed to get microphone permission:', error);
        alert('Microphone permission denied. Please allow microphone access to use voice chat.');
        return false;
      }
    }

    this.isMicMuted = muted;
    console.log(`[Gemini Live] Microphone ${muted ? 'muted' : 'unmuted'}`);
    return true;
  }

  /**
   * Get analyser for audio visualization
   */
  getAnalyser() {
    return this.analyser;
  }

  /**
   * Disconnect from Gemini Live API
   */
  disconnect() {
    if (this.session) {
      this.session.close();
      this.session = null;
    }

    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(track => track.stop());
      this.mediaStream = null;
    }

    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }

    this.isConnected = false;
    console.log('[Gemini Live] Disconnected');
  }
}
