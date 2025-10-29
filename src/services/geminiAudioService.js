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
    this.onCommentatorTranscript = null; // NEW: callback for commentator speech

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

    // Track what commentator is saying
    this.currentObservation = null;
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
  async createSession() {
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
      systemInstruction: `You are a hype sports commentator for AI coding battles between 4 agents: Speedrunner, Bloom, Solver, and Loader.

THE AGENTS:
- SPEEDRUNNER: Fast, competitive, efficiency-obsessed
- BLOOM: Creative, scattered, loves animations/visuals
- SOLVER: Logical, methodical, algorithm-focused
- LOADER: Patient, steady, handles async/data
- BOSS: The user giving commands

IMPORTANT:
- ALWAYS acknowledge Boss when they speak
- Use agent names when reacting to their actions
- React naturally and energetically in 5-10 words
- Be casual, fun, and hype. Use slang.

Examples:
- "Boss said: make it blue" → "Yo boss wants it blue, heard!"
- "Boss said: hi what's up" → "What's good boss! We got you!"
- "Speedrunner roasting Bloom's code" → "Speedrunner coming in hot damn!"
- "Bloom giving Solver props" → "Bloom showing love to Solver fr!"
- "Loader calling out bugs" → "Loader catching those bugs nice!"
- "Solver finished first" → "Solver came through clutch!"

Keep it SHORT and natural. Hype up the action and respect the Boss.`
    };

    this.session = await this.ai.live.connect({
      model: this.model,
      callbacks: {
        onopen: () => {
          console.log('[GeminiAudio] Session opened');
          this.isSessionActive = true;
        },
        onmessage: (message) => {
          // Handle audio data (model speaking)
          if (message.data) {
            this.handleAudioResponse(message.data);
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

      // Store observation for transcript callback
      this.currentObservation = observationText;

      // Create session
      if (!this.session || !this.isSessionActive) {
        await this.createSession();
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

      // Trigger commentator transcript callback with the observation
      // (this represents what the commentator is saying in response)
      if (this.onCommentatorTranscript) {
        this.onCommentatorTranscript(observationText);
      }

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
   * Start recording microphone - collects audio chunks for batch transcription
   */
  async startRecording() {
    if (this.isRecording) {
      console.log('[GeminiAudio] Already recording, ignoring...');
      return;
    }

    try {
      console.log('[GeminiAudio] Starting recording...');

      // Get microphone access
      this.mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true
        }
      });

      console.log('[GeminiAudio] Microphone access granted');

      // Reset audio chunks
      this.audioChunks = [];

      // Use MediaRecorder to collect audio (will produce WebM/Opus or similar)
      this.mediaRecorder = new MediaRecorder(this.mediaStream, {
        mimeType: 'audio/webm;codecs=opus'
      });

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
          console.log('[GeminiAudio] Audio chunk collected:', event.data.size, 'bytes');
        }
      };

      this.mediaRecorder.onstop = async () => {
        console.log('[GeminiAudio] Recording stopped, processing audio...');
        await this.transcribeRecording();
      };

      this.mediaRecorder.start();
      this.isRecording = true;
      this.isMicMuted = false;
      console.log('[GeminiAudio] Recording started');
    } catch (error) {
      console.error('[GeminiAudio] Failed to start recording:', error);
      throw error;
    }
  }

  /**
   * Transcribe the recorded audio using Gemini API
   */
  async transcribeRecording() {
    if (this.audioChunks.length === 0) {
      console.log('[GeminiAudio] No audio chunks to transcribe');
      return;
    }

    try {
      console.log('[GeminiAudio] Transcribing', this.audioChunks.length, 'chunks...');

      // Combine all chunks into a single blob
      const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm;codecs=opus' });
      console.log('[GeminiAudio] Total audio size:', audioBlob.size, 'bytes');

      // Convert blob to base64
      const base64Audio = await this.blobToBase64(audioBlob);

      // Send to Gemini for transcription
      const response = await this.ai.models.generateContent({
        model: 'gemini-2.5-flash',
        contents: [{
          role: 'user',
          parts: [
            {
              inlineData: {
                mimeType: 'audio/webm',
                data: base64Audio
              }
            },
            {
              text: 'Generate a transcript of the speech. Only return the transcript text, nothing else.'
            }
          ]
        }]
      });

      const transcript = response.text.trim();
      console.log('[GeminiAudio] ✅ Transcription:', transcript);

      // Call callback with transcript
      if (this.onUserTranscript && transcript) {
        this.onUserTranscript(transcript);
      }
    } catch (error) {
      console.error('[GeminiAudio] Transcription failed:', error);
    }
  }

  /**
   * Convert blob to base64
   */
  async blobToBase64(blob) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64 = reader.result.split(',')[1]; // Remove data:audio/webm;base64, prefix
        resolve(base64);
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }

  /**
   * Stop recording and trigger transcription
   */
  stopRecording() {
    if (!this.isRecording) return;

    try {
      console.log('[GeminiAudio] Stopping recording...');

      // Stop MediaRecorder (this will trigger onstop and transcription)
      if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
        this.mediaRecorder.stop();
      }

      // Stop media stream
      if (this.mediaStream) {
        this.mediaStream.getTracks().forEach(track => track.stop());
        this.mediaStream = null;
      }

      this.isRecording = false;
      this.isMicMuted = true;
      console.log('[GeminiAudio] Recording stopped, transcription will begin');
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
