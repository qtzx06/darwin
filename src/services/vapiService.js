import Vapi from '@vapi-ai/web';

const PUBLIC_KEY = import.meta.env.VITE_VAPI_PUBLIC_KEY;

/**
 * VAPI Voice Manager for Composer AI voice assistant
 */
export class VapiVoiceManager {
  constructor() {
    this.vapi = null;
    this.isActive = false;
    this.isMicMuted = true;
    this.onTranscript = null;
    this.onUserTranscript = null;
    this.onSpeechStart = null;
    this.onSpeechEnd = null;
  }

  /**
   * Initialize VAPI with assistant
   */
  async initialize(assistantId) {
    try {
      console.log('[VAPI] Initializing with assistant:', assistantId);

      this.vapi = new Vapi(PUBLIC_KEY);

      // Set up event listeners
      this.vapi.on('call-start', () => {
        console.log('[VAPI] Call started');
        this.isActive = true;
      });

      this.vapi.on('call-end', () => {
        console.log('[VAPI] Call ended');
        this.isActive = false;
      });

      this.vapi.on('speech-start', () => {
        console.log('[VAPI] AI started speaking');
        if (this.onSpeechStart) {
          this.onSpeechStart();
        }
      });

      this.vapi.on('speech-end', () => {
        console.log('[VAPI] AI stopped speaking');
        if (this.onSpeechEnd) {
          this.onSpeechEnd();
        }
      });

      this.vapi.on('message', (message) => {
        console.log('[VAPI] Message:', message);

        // Handle transcripts
        if (message.type === 'transcript') {
          const text = message.transcript;
          const role = message.role; // 'user' or 'assistant'

          if (role === 'user' && this.onUserTranscript) {
            console.log('[VAPI] User said:', text);
            this.onUserTranscript(text);
          } else if (role === 'assistant' && this.onTranscript) {
            console.log('[VAPI] Composer said:', text);
            this.onTranscript(text);
          }
        }
      });

      this.vapi.on('error', (error) => {
        console.error('[VAPI] Error:', error);
      });

      console.log('[VAPI] Initialized successfully');
      return true;
    } catch (error) {
      console.error('[VAPI] Failed to initialize:', error);
      throw error;
    }
  }

  /**
   * Start voice conversation
   */
  async start(assistantId) {
    try {
      if (!this.vapi) {
        await this.initialize(assistantId);
      }

      console.log('[VAPI] Starting call with assistant:', assistantId);
      await this.vapi.start(assistantId);
      this.isMicMuted = false;
      return true;
    } catch (error) {
      console.error('[VAPI] Failed to start call:', error);
      throw error;
    }
  }

  /**
   * Stop voice conversation
   */
  async stop() {
    try {
      if (this.vapi && this.isActive) {
        console.log('[VAPI] Stopping call');
        await this.vapi.stop();
        this.isActive = false;
        this.isMicMuted = true;
      }
    } catch (error) {
      console.error('[VAPI] Failed to stop call:', error);
    }
  }

  /**
   * Toggle microphone mute
   */
  async setMicMuted(muted) {
    try {
      if (!this.vapi) return;

      if (muted && this.isActive) {
        await this.stop();
      } else if (!muted && !this.isActive) {
        // Need assistant ID to start
        console.log('[VAPI] Cannot start - need assistant ID');
      }

      this.isMicMuted = muted;
      console.log(`[VAPI] Microphone ${muted ? 'muted' : 'unmuted'}`);
    } catch (error) {
      console.error('[VAPI] Failed to toggle mic:', error);
    }
  }

  /**
   * Send a text message to the assistant
   */
  sendMessage(text) {
    if (this.vapi && this.isActive) {
      console.log('[VAPI] Sending message:', text);
      this.vapi.send({
        type: 'add-message',
        message: {
          role: 'user',
          content: text
        }
      });
    }
  }

  /**
   * Check if currently in call
   */
  isCallActive() {
    return this.isActive;
  }
}
