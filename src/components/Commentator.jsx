import { useState, useEffect, useRef } from 'react';
import './Commentator.css';
import NeuroShaderCanvas from './NeuroShaderCanvas';
import CommentatorOrb from './CommentatorOrb';
import { GeminiLiveManager } from '../services/liveGeminiService';

function Commentator({ query, onBattleStart, isRunning, agentsReady, chatMessages = [], onComposerMessage, onUserMessage, onGeminiLiveReady }) {
  const [analyser, setAnalyser] = useState(null);
  const [isSoundActive, setIsSoundActive] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [loadingMessageIndex, setLoadingMessageIndex] = useState(0);
  const [isOutputMuted, setIsOutputMuted] = useState(false); // Gemini voice output (start unmuted)
  const [geminiConnected, setGeminiConnected] = useState(false);
  const geminiLiveRef = useRef(null);

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

  // Initialize Gemini Live connection when agents are ready
  useEffect(() => {
    let isCleanup = false;

    const connectGeminiLive = async () => {
      // Don't connect if already connected or if we're cleaning up
      if (!agentsReady || geminiConnected || geminiLiveRef.current?.isConnected) {
        return;
      }

      try {
        console.log('[Commentator] Connecting to Gemini Live...');

        // Create Gemini Live manager if it doesn't exist
        if (!geminiLiveRef.current) {
          geminiLiveRef.current = new GeminiLiveManager();
        }

        // Set up callbacks for audio visualization
        geminiLiveRef.current.onAudioLevel = (level) => {
          if (!isCleanup) {
            setIsSoundActive(level > 0.05);
          }
        };

        // When Composer speaks, add to chat
        geminiLiveRef.current.onTranscript = (text) => {
          if (isCleanup) return;
          console.log('[Commentator] Composer says:', text);
          if (onComposerMessage) {
            onComposerMessage(text);
          }

          // Check if Composer is giving commands to agents
          if (text.toLowerCase().includes('make') || text.toLowerCase().includes('change') || text.toLowerCase().includes('add')) {
            console.log('[Commentator] Composer might be giving a command, processing...');
            // Send command to agents via onUserMessage
            if (onUserMessage) {
              onUserMessage(text);
            }
          }
        };

        // When user speaks, show in chat
        geminiLiveRef.current.onUserTranscript = (text) => {
          if (isCleanup) return;
          console.log('[Commentator] User says:', text);
          // This would be shown in transcript panel
        };

        // Build system instruction with chat context
        const recentChat = chatMessages.slice(-5).map(msg => msg.text).join('\n');
        const systemInstruction = `You are Composer, an AI assistant helping orchestrate a coding battle between 4 AI agents (Speedrunner, Bloom, Solver, Loader).

Your role:
1. Provide witty, brief commentary on what's happening (under 15 words)
2. When the user asks you to change something, give commands like "yo agents, make that button black" and the agents will respond
3. Be casual, fun, and energetic - use slang like "fr", "ngl", "yo"

Recent chat context:
${recentChat}

Remember: Keep responses SHORT and conversational!`;

        // Connect to Gemini Live API with context
        await geminiLiveRef.current.connect(systemInstruction);

        // Get analyser for orb visualization
        const analyserNode = geminiLiveRef.current.getAnalyser();
        if (analyserNode && !isCleanup) {
          setAnalyser(analyserNode);
        }

        if (!isCleanup) {
          setGeminiConnected(true);
          console.log('[Commentator] Gemini Live connected successfully');

          // Notify parent that Gemini Live is ready
          if (onGeminiLiveReady) {
            onGeminiLiveReady(geminiLiveRef);
          }
        }
      } catch (error) {
        if (!isCleanup) {
          console.error('[Commentator] Failed to connect Gemini Live:', error);
        }
      }
    };

    connectGeminiLive();

    // Cleanup only disconnects if component is actually unmounting
    return () => {
      isCleanup = true;
      console.log('[Commentator] Cleanup triggered');
      // Don't disconnect on strict mode remount - only on actual unmount
    };
  }, [agentsReady]); // Remove geminiConnected from deps to prevent re-running

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
