import { ElevenLabsClient } from '@elevenlabs/elevenlabs-js';

const API_KEY = import.meta.env.VITE_ELEVENLABS_API_KEY;

/**
 * ElevenLabs Voice Manager with TTS and STT for Composer
 */
export class ElevenLabsVoiceManager {
  constructor() {
    this.client = new ElevenLabsClient({ apiKey: API_KEY });
    this.audioContext = null;
    this.analyser = null;
    this.gainNode = null;
    this.isPlaying = false;
    this.isMuted = false;
    this.currentSource = null;
    this.onSpeechStart = null;
    this.onSpeechEnd = null;
    this.onUserTranscript = null; // Callback for user's speech transcription

    // Voice ID - using a fun energetic voice for the composer
    this.voiceId = 'Anr9GtYh2VRXxiPplzxM'; // Custom voice from library

    // Speech recognition state
    this.recognition = null;
    this.isRecording = false;
    this.isMicMuted = true;
  }

  /**
   * Initialize audio context for playback and visualization
   */
  async initialize() {
    try {
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 256;

      // Create gain node for volume control
      this.gainNode = this.audioContext.createGain();
      this.gainNode.gain.value = this.isMuted ? 0.0 : 1.0;

      // Connect: analyser -> gainNode -> speakers
      this.analyser.connect(this.gainNode);
      this.gainNode.connect(this.audioContext.destination);

      console.log('[ElevenLabs] Initialized successfully');
      return true;
    } catch (error) {
      console.error('[ElevenLabs] Failed to initialize:', error);
      throw error;
    }
  }

  /**
   * Speak text using ElevenLabs TTS with streaming
   */
  async speak(text) {
    if (!this.audioContext) {
      await this.initialize();
    }

    try {
      console.log('[ElevenLabs] Speaking:', text);

      if (this.onSpeechStart) {
        this.onSpeechStart();
      }

      this.isPlaying = true;

      // Use the convert endpoint to get full audio
      console.log('[ElevenLabs] Requesting TTS conversion...');
      const response = await this.client.textToSpeech.convert(this.voiceId, {
        text: text,
        model_id: 'eleven_multilingual_v2',
        output_format: 'mp3_44100_128'
      });

      console.log('[ElevenLabs] TTS response received:', response);

      // Convert response to array buffer
      let audioData;
      if (response instanceof ReadableStream) {
        const reader = response.getReader();
        const chunks = [];
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          chunks.push(value);
        }
        const totalLength = chunks.reduce((acc, chunk) => acc + chunk.length, 0);
        audioData = new Uint8Array(totalLength);
        let offset = 0;
        for (const chunk of chunks) {
          audioData.set(chunk, offset);
          offset += chunk.length;
        }
      } else if (response instanceof ArrayBuffer) {
        audioData = new Uint8Array(response);
      } else if (response instanceof Uint8Array) {
        audioData = response;
      } else {
        throw new Error('Unexpected response type: ' + typeof response);
      }

      console.log('[ElevenLabs] Audio data size:', audioData.length);

      // Decode MP3 audio
      const audioBuffer = await this.audioContext.decodeAudioData(audioData.buffer);
      console.log('[ElevenLabs] Audio decoded, duration:', audioBuffer.duration);

      // Create buffer source and connect to analyser
      this.currentSource = this.audioContext.createBufferSource();
      this.currentSource.buffer = audioBuffer;
      this.currentSource.connect(this.analyser);

      // Handle playback end
      this.currentSource.onended = () => {
        this.isPlaying = false;
        if (this.onSpeechEnd) {
          this.onSpeechEnd();
        }
        console.log('[ElevenLabs] Finished speaking');
      };

      // Play audio
      this.currentSource.start();
      console.log('[ElevenLabs] Audio playback started');

    } catch (error) {
      console.error('[ElevenLabs] Failed to speak:', error);
      console.error('[ElevenLabs] Error details:', error.message, error.stack);
      this.isPlaying = false;
      if (this.onSpeechEnd) {
        this.onSpeechEnd();
      }
    }
  }

  /**
   * Stop current speech
   */
  stop() {
    if (this.currentSource && this.isPlaying) {
      try {
        this.currentSource.stop();
        this.currentSource = null;
        this.isPlaying = false;
        console.log('[ElevenLabs] Stopped speaking');
      } catch (error) {
        console.error('[ElevenLabs] Failed to stop:', error);
      }
    }
  }

  /**
   * Set muted state
   */
  setMuted(muted) {
    this.isMuted = muted;
    if (this.gainNode) {
      this.gainNode.gain.value = muted ? 0.0 : 1.0;
      console.log(`[ElevenLabs] Voice ${muted ? 'muted' : 'unmuted'}`);
    }
  }

  /**
   * Get analyser for audio visualization
   */
  getAnalyser() {
    return this.analyser;
  }

  /**
   * Check if currently speaking
   */
  isSpeaking() {
    return this.isPlaying;
  }

  /**
   * Start recording microphone for STT using browser's SpeechRecognition
   */
  async startRecording() {
    if (this.isRecording) return;

    try {
      console.log('[ElevenLabs] Starting speech recognition...');

      // Use browser's native SpeechRecognition API
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

      if (!SpeechRecognition) {
        throw new Error('SpeechRecognition not supported in this browser');
      }

      this.recognition = new SpeechRecognition();
      this.recognition.continuous = true; // Keep listening
      this.recognition.interimResults = false; // Only final results
      this.recognition.lang = 'en-US';

      this.recognition.onstart = () => {
        console.log('[ElevenLabs] Speech recognition started');
        this.isRecording = true;
        this.isMicMuted = false;
      };

      this.recognition.onresult = (event) => {
        const lastResult = event.results[event.results.length - 1];
        if (lastResult.isFinal) {
          const transcript = lastResult[0].transcript;
          console.log('[ElevenLabs] User transcript:', transcript);

          if (this.onUserTranscript && transcript) {
            this.onUserTranscript(transcript);
          }
        }
      };

      this.recognition.onerror = (event) => {
        console.error('[ElevenLabs] Speech recognition error:', event.error);
        if (event.error === 'no-speech') {
          console.log('[ElevenLabs] No speech detected, continuing...');
        }
      };

      this.recognition.onend = () => {
        console.log('[ElevenLabs] Speech recognition ended');
        // Auto-restart if still supposed to be recording
        if (!this.isMicMuted && this.isRecording) {
          console.log('[ElevenLabs] Restarting recognition...');
          try {
            this.recognition.start();
          } catch (error) {
            console.error('[ElevenLabs] Failed to restart recognition:', error);
          }
        }
      };

      this.recognition.start();
      console.log('[ElevenLabs] Speech recognition initialized');
    } catch (error) {
      console.error('[ElevenLabs] Failed to start speech recognition:', error);
      throw error;
    }
  }

  /**
   * Stop recording
   */
  stopRecording() {
    if (!this.isRecording || !this.recognition) return;

    try {
      this.recognition.stop();
      this.isRecording = false;
      this.isMicMuted = true;
      console.log('[ElevenLabs] Speech recognition stopped');
    } catch (error) {
      console.error('[ElevenLabs] Failed to stop recognition:', error);
    }
  }

  /**
   * Transcribe audio using ElevenLabs STT
   * NOTE: STT API might not be available in current SDK version
   */
  async transcribeAudio(audioBlob) {
    try {
      console.log('[ElevenLabs] Transcription not yet implemented - SDK may not support STT');

      // TODO: Implement when ElevenLabs SDK supports STT transcription
      // For now, just log that we received audio
      console.log('[ElevenLabs] Received audio blob of size:', audioBlob.size);

      // Could use browser's native SpeechRecognition API as fallback
      if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        console.log('[ElevenLabs] Could use browser SpeechRecognition as fallback');
      }
    } catch (error) {
      console.error('[ElevenLabs] Failed to transcribe:', error);
    }
  }

  /**
   * Toggle microphone recording
   */
  async setMicMuted(muted) {
    if (muted && this.isRecording) {
      this.stopRecording();
    } else if (!muted && !this.isRecording) {
      await this.startRecording();
    }
    console.log(`[ElevenLabs] Microphone ${muted ? 'muted' : 'unmuted'}`);
  }

  /**
   * Cleanup
   */
  dispose() {
    this.stop();
    if (this.isRecording) {
      this.stopRecording();
    }
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
  }
}
