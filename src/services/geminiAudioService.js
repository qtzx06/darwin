import { GoogleGenAI, Modality } from '@google/genai';

const API_KEY = import.meta.env.VITE_GEMINI_API_KEY;

/**
 * Gemini Native Audio Manager with Live API for TTS and STT
 */
export class GeminiAudioManager {
  constructor() {
    this.ai = new GoogleGenAI({ apiKey: API_KEY });
    this.audioContext = null;
    this.analyser = null;
    this.gainNode = null;
    this.isPlaying = false;
    this.isMuted = false;
    this.currentSource = null;
    this.onSpeechStart = null;
    this.onSpeechEnd = null;
    this.onUserTranscript = null;

    // Live API session
    this.session = null;
    this.isSessionActive = false;

    // Model configuration
    this.model = 'gemini-2.5-flash-native-audio-preview-09-2025';

    // Recording state
    this.mediaRecorder = null;
    this.mediaStream = null;
    this.audioChunks = [];
    this.isRecording = false;
    this.isMicMuted = true;
    this.audioWorkletNode = null;

    // Audio queue for streaming chunks
    this.audioQueue = [];
    this.isProcessingQueue = false;
    this.currentTurnAudioChunks = [];
    this.hasStartedSpeech = false;
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

      console.log('[GeminiAudio] Initialized successfully');
      return true;
    } catch (error) {
      console.error('[GeminiAudio] Failed to initialize:', error);
      throw error;
    }
  }

  /**
   * Create a Live API session
   */
  async createSession(enableInputTranscription = false) {
    if (this.session && this.isSessionActive) {
      return this.session;
    }

    const config = {
      responseModalities: [Modality.AUDIO],
      speechConfig: {
        voiceConfig: {
          prebuiltVoiceConfig: {
            voiceName: "Charon" // Deep male voice
          }
        }
      },
      systemInstruction: `You are a hype sports commentator for AI coding battles. You'll receive observations about what's happening in the battle.

React naturally and energetically in 5-10 words. Be casual, fun, and hype. Use slang.

Examples:
- If told "agents arguing about code": "Yo they're beefing hard rn!"
- If told "user liked solver": "Solver getting that love fr!"
- If told "battle complete": "That's a wrap y'all!"
- If told "speedrunner finished first": "Speed demon came through!"

Keep it SHORT and natural. You're hyping up the action.`
    };

    // Only enable input transcription when recording user voice
    if (enableInputTranscription) {
      config.inputAudioTranscription = {};
    }

    const responseQueue = [];

    this.session = await this.ai.live.connect({
      model: this.model,
      callbacks: {
        onopen: () => {
          console.log('[GeminiAudio] Session opened');
          this.isSessionActive = true;
        },
        onmessage: (message) => {
          responseQueue.push(message);

          // Handle audio data (model speaking)
          if (message.data) {
            this.handleAudioResponse(message.data);
          }

          // Handle INPUT transcription (user's voice -> text) ONLY when recording
          if (enableInputTranscription && message.serverContent?.inputTranscription) {
            const transcriptText = message.serverContent.inputTranscription.text;
            if (transcriptText && this.onUserTranscript) {
              console.log('[GeminiAudio] User speech transcribed:', transcriptText);
              this.onUserTranscript(transcriptText);
            }
          }
        },
        onerror: (e) => {
          console.error('[GeminiAudio] Session error:', e.message);
          this.isSessionActive = false;
        },
        onclose: (e) => {
          console.log('[GeminiAudio] Session closed:', e.reason);
          this.isSessionActive = false;
        }
      },
      config: config
    });

    console.log('[GeminiAudio] Session created');
    return this.session;
  }

  /**
   * Handle incoming audio response from Gemini
   * Audio comes in chunks that need to be queued and played sequentially
   */
  async handleAudioResponse(base64Audio) {
    try {
      if (!this.audioContext) {
        await this.initialize();
      }

      // Add chunk to current turn's audio
      this.currentTurnAudioChunks.push(base64Audio);

      // Trigger speech start on first chunk
      if (!this.hasStartedSpeech) {
        this.hasStartedSpeech = true;
        if (this.onSpeechStart) {
          this.onSpeechStart();
        }
      }

      // Start processing queue if not already processing
      if (!this.isProcessingQueue) {
        this.processAudioQueue();
      }
    } catch (error) {
      console.error('[GeminiAudio] Failed to handle audio response:', error);
    }
  }

  /**
   * Process audio chunks sequentially from queue
   */
  async processAudioQueue() {
    if (this.isProcessingQueue) return;
    this.isProcessingQueue = true;

    while (this.currentTurnAudioChunks.length > 0) {
      const base64Audio = this.currentTurnAudioChunks.shift();

      try {
        // Decode base64 audio (24kHz, 16-bit PCM from Gemini)
        const audioData = Uint8Array.from(atob(base64Audio), c => c.charCodeAt(0));

        // Convert to Int16Array (PCM format)
        const pcmData = new Int16Array(audioData.buffer);

        // Create AudioBuffer from PCM data (Gemini outputs 24kHz)
        const audioBuffer = this.audioContext.createBuffer(1, pcmData.length, 24000);
        const channelData = audioBuffer.getChannelData(0);

        // Convert Int16 to Float32 (-1.0 to 1.0 range)
        for (let i = 0; i < pcmData.length; i++) {
          channelData[i] = pcmData[i] / 32768.0;
        }

        // Create buffer source and connect to analyser
        const source = this.audioContext.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(this.analyser);

        // Wait for this chunk to finish before playing next
        await new Promise((resolve) => {
          source.onended = resolve;
          source.start();
        });

      } catch (error) {
        console.error('[GeminiAudio] Failed to play audio chunk:', error);
      }
    }

    this.isProcessingQueue = false;
    this.hasStartedSpeech = false;
    this.isPlaying = false;

    // All chunks played, trigger speech end
    if (this.onSpeechEnd) {
      this.onSpeechEnd();
    }
  }

  /**
   * React to observation with natural voice response
   */
  async speak(observationText) {
    try {
      console.log('[GeminiAudio] Observation received:', observationText);

      // Don't start new speech if already processing audio
      if (this.isProcessingQueue || this.hasStartedSpeech) {
        console.log('[GeminiAudio] Already speaking, skipping...');
        return;
      }

      // Clear any leftover chunks from previous turn
      this.currentTurnAudioChunks = [];

      // Create session WITHOUT input transcription for commentator reactions
      if (!this.session || !this.isSessionActive) {
        await this.createSession(false); // NO input transcription
      }

      // Send observation as a conversational turn - Gemini will REACT to it naturally
      this.session.sendClientContent({
        turns: [
          {
            role: 'user',
            parts: [{ text: observationText }]
          }
        ],
        turnComplete: true
      });

      console.log('[GeminiAudio] Observation sent, waiting for natural voice reaction...');

    } catch (error) {
      console.error('[GeminiAudio] Failed to react:', error);
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
        console.log('[GeminiAudio] Stopped speaking');
      } catch (error) {
        console.error('[GeminiAudio] Failed to stop:', error);
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
      console.log(`[GeminiAudio] Voice ${muted ? 'muted' : 'unmuted'}`);
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
   * Start recording microphone for STT using AudioWorklet for PCM streaming
   */
  async startRecording() {
    if (this.isRecording) return;

    try {
      console.log('[GeminiAudio] Requesting microphone access...');

      // Get microphone access
      this.mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000, // Gemini requires 16kHz
          echoCancellation: true,
          noiseSuppression: true
        }
      });

      // Create NEW session with input transcription enabled for user voice
      if (this.session && this.isSessionActive) {
        this.session.close();
        this.session = null;
        this.isSessionActive = false;
      }
      await this.createSession(true); // Enable input transcription

      // Create MediaStreamAudioSourceNode
      const source = this.audioContext.createMediaStreamSource(this.mediaStream);

      // We'll use ScriptProcessorNode for now (deprecated but widely supported)
      // In production, use AudioWorklet for better performance
      const processor = this.audioContext.createScriptProcessor(4096, 1, 1);

      processor.onaudioprocess = (e) => {
        if (!this.isRecording) return;

        const inputData = e.inputBuffer.getChannelData(0);

        // Convert Float32 to Int16 PCM
        const pcmData = new Int16Array(inputData.length);
        for (let i = 0; i < inputData.length; i++) {
          const s = Math.max(-1, Math.min(1, inputData[i]));
          pcmData[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
        }

        // Convert to base64
        const buffer = new Uint8Array(pcmData.buffer);
        const base64 = btoa(String.fromCharCode(...buffer));

        // Send to Gemini in real-time
        if (this.session && this.isSessionActive) {
          this.session.sendRealtimeInput({
            audio: {
              data: base64,
              mimeType: 'audio/pcm;rate=16000'
            }
          });
        }
      };

      source.connect(processor);
      processor.connect(this.audioContext.destination);

      this.audioWorkletNode = processor;
      this.isRecording = true;
      this.isMicMuted = false;
      console.log('[GeminiAudio] Recording started with real-time streaming');
    } catch (error) {
      console.error('[GeminiAudio] Failed to start recording:', error);
      throw error;
    }
  }

  /**
   * Stop recording
   */
  stopRecording() {
    if (!this.isRecording) return;

    try {
      if (this.audioWorkletNode) {
        this.audioWorkletNode.disconnect();
        this.audioWorkletNode = null;
      }

      if (this.mediaStream) {
        this.mediaStream.getTracks().forEach(track => track.stop());
        this.mediaStream = null;
      }

      this.isRecording = false;
      this.isMicMuted = true;
      console.log('[GeminiAudio] Recording stopped');
    } catch (error) {
      console.error('[GeminiAudio] Failed to stop recording:', error);
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
    console.log(`[GeminiAudio] Microphone ${muted ? 'muted' : 'unmuted'}`);
  }

  /**
   * Close session and cleanup
   */
  dispose() {
    this.stop();
    if (this.isRecording) {
      this.stopRecording();
    }
    if (this.session && this.isSessionActive) {
      this.session.close();
      this.session = null;
      this.isSessionActive = false;
    }
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
  }
}
