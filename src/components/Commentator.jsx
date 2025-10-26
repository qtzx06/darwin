import { useState, useEffect, useRef } from 'react';
import './Commentator.css';
import NeuroShaderCanvas from './NeuroShaderCanvas';
import CommentatorOrb from './CommentatorOrb';
import { VapiVoiceManager } from '../services/vapiService';

function Commentator({ query, onBattleStart, isRunning, agentsReady, chatMessages = [], onComposerMessage, onUserMessage, onVapiReady }) {
  const [analyser, setAnalyser] = useState(null);
  const [isSoundActive, setIsSoundActive] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [loadingMessageIndex, setLoadingMessageIndex] = useState(0);
  const [isOutputMuted, setIsOutputMuted] = useState(false); // Voice output (start unmuted)
  const [vapiConnected, setVapiConnected] = useState(false);
  const vapiRef = useRef(null);
  const assistantId = import.meta.env.VITE_VAPI_ASSISTANT_ID;

  const loadingMessages = [
    'initializing agents...',
    'warming up models...',
    'preparing arena...',
    'configuring workspace...',
    'syncing neural networks...',
    'loading agent personalities...',
    'establishing connections...',
    'calibrating systems...'
  ];

  // Initialize VAPI connection when agents are ready
  useEffect(() => {
    const initVapi = async () => {
      if (!agentsReady || vapiConnected || !assistantId) {
        return;
      }

      try {
        console.log('[Commentator] Initializing VAPI...');

        // Create VAPI manager if it doesn't exist
        if (!vapiRef.current) {
          vapiRef.current = new VapiVoiceManager();
        }

        // Set up callbacks
        vapiRef.current.onTranscript = (text) => {
          console.log('[Commentator] Composer says:', text);
          if (onComposerMessage) {
            onComposerMessage(text);
          }

          // Check if Composer is giving commands to agents
          if (text.toLowerCase().includes('make') || text.toLowerCase().includes('change') || text.toLowerCase().includes('add')) {
            console.log('[Commentator] Composer might be giving a command, processing...');
            if (onUserMessage) {
              onUserMessage(text);
            }
          }
        };

        vapiRef.current.onUserTranscript = (text) => {
          console.log('[Commentator] User says:', text);
        };

        vapiRef.current.onSpeechStart = () => {
          setIsSoundActive(true);
        };

        vapiRef.current.onSpeechEnd = () => {
          setIsSoundActive(false);
        };

        // Initialize VAPI
        await vapiRef.current.initialize(assistantId);

        setVapiConnected(true);
        console.log('[Commentator] VAPI initialized successfully');

        // Notify parent that VAPI is ready
        if (onVapiReady) {
          onVapiReady(vapiRef);
        }
      } catch (error) {
        console.error('[Commentator] Failed to initialize VAPI:', error);
      }
    };

    initVapi();

    return () => {
      // Cleanup on unmount
      if (vapiRef.current) {
        vapiRef.current.stop();
      }
    };
  }, [agentsReady, assistantId]);

  // Cycle loading messages
  useEffect(() => {
    if (!agentsReady && query) {
      const interval = setInterval(() => {
        setLoadingMessageIndex(prev => (prev + 1) % loadingMessages.length);
      }, 1500);
      return () => clearInterval(interval);
    }
  }, [agentsReady, query, loadingMessages.length]);

  const handleStart = () => {
    if (!isRunning && query && agentsReady && onBattleStart) {
      onBattleStart();
    }
  };

  const toggleOutputVolume = async () => {
    const newMuted = !isOutputMuted;
    setIsOutputMuted(newMuted);

    // Toggle Gemini's voice output
    if (geminiLiveRef.current) {
      await geminiLiveRef.current.setOutputMuted(newMuted);
      console.log(`[Commentator] Gemini voice ${newMuted ? 'muted' : 'unmuted'}`);
    }
  };

  return (
    <div className="glass-card commentator-card">
      <div className="glass-filter"></div>
      <div className="glass-overlay"></div>
      <div className="glass-specular"></div>
      <div className="glass-content">
        <div className="commentator-header">
          <div>
            <h3>composer</h3>
            <div className="commentator-description">autonomous agent orchestration</div>
          </div>
          <button
            type="button"
            onClick={toggleOutputVolume}
            className="commentator-volume-button"
          >
            <i className={isOutputMuted ? "fas fa-volume-mute" : "fas fa-volume-up"}></i>
          </button>
        </div>
        <div className="commentator-headshot">
          <NeuroShaderCanvas />
          {analyser && (
            <CommentatorOrb
              analyser={analyser}
              onSoundActiveChange={setIsSoundActive}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default Commentator;
