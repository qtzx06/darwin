import { useState, useEffect, useRef } from 'react';
import './Commentator.css';
import NeuroShaderCanvas from './NeuroShaderCanvas';
import CommentatorOrb from './CommentatorOrb';
import { ElevenLabsVoiceManager } from '../services/elevenlabsService';
import { CommentatorGeminiService } from '../services/commentatorGeminiService';

function Commentator({ query, onBattleStart, isRunning, agentsReady, chatMessages = [], onElevenLabsReady }) {
  const [analyser, setAnalyser] = useState(null);
  const [isSoundActive, setIsSoundActive] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [loadingMessageIndex, setLoadingMessageIndex] = useState(0);
  const [isOutputMuted, setIsOutputMuted] = useState(true); // Voice output (start muted, user must enable)
  const [elevenLabsReady, setElevenLabsReady] = useState(false);
  const [hasSpokenIntro, setHasSpokenIntro] = useState(false);
  const elevenLabsRef = useRef(null);
  const commentatorGeminiRef = useRef(null);
  const lastMessageCountRef = useRef(0); // Track message count to avoid repeats
  const commentaryIntervalRef = useRef(null);

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

  // Initialize ElevenLabs and Gemini when agents are ready
  useEffect(() => {
    const initServices = async () => {
      if (!agentsReady || elevenLabsReady) {
        return;
      }

      try {
        console.log('[Commentator] Initializing services...');

        // Create ElevenLabs manager
        if (!elevenLabsRef.current) {
          elevenLabsRef.current = new ElevenLabsVoiceManager();
        }

        // Create Commentator Gemini service
        if (!commentatorGeminiRef.current) {
          commentatorGeminiRef.current = new CommentatorGeminiService();
        }

        // Set up callbacks
        elevenLabsRef.current.onSpeechStart = () => {
          setIsSoundActive(true);
        };

        elevenLabsRef.current.onSpeechEnd = () => {
          setIsSoundActive(false);
        };

        // Initialize ElevenLabs
        await elevenLabsRef.current.initialize();

        // Get analyser for visualization
        const analyserNode = elevenLabsRef.current.getAnalyser();
        setAnalyser(analyserNode);

        setElevenLabsReady(true);
        console.log('[Commentator] Services initialized successfully');

        // Notify parent that ElevenLabs is ready
        if (onElevenLabsReady) {
          onElevenLabsReady(elevenLabsRef);
        }
      } catch (error) {
        console.error('[Commentator] Failed to initialize services:', error);
      }
    };

    initServices();

    return () => {
      // Cleanup on unmount
      if (elevenLabsRef.current) {
        elevenLabsRef.current.dispose();
      }
      if (commentaryIntervalRef.current) {
        clearInterval(commentaryIntervalRef.current);
      }
    };
  }, [agentsReady]);

  // Speak welcome intro when battle starts
  useEffect(() => {
    if (isRunning && !hasSpokenIntro && elevenLabsReady && query) {
      setHasSpokenIntro(true);

      // Get welcome intro
      const intro = commentatorGeminiRef.current.getWelcomeIntro(query);
      console.log('[Commentator] Speaking intro:', intro);
      elevenLabsRef.current.speak(intro);
    }
  }, [isRunning, hasSpokenIntro, elevenLabsReady, query]);

  // Generate and speak commentary from EVERY chat update (ONLY after battle is complete)
  useEffect(() => {
    if (!elevenLabsReady || !elevenLabsRef.current || !commentatorGeminiRef.current) {
      return;
    }

    // Only generate commentary when there are NEW messages
    if (chatMessages.length === lastMessageCountRef.current || chatMessages.length === 0) {
      return;
    }

    // Check if battle is complete (look for "Battle complete!" in chat)
    const battleComplete = chatMessages.some(msg =>
      msg.text && msg.text.toLowerCase().includes('battle complete')
    );

    // Don't start commentary until battle is complete
    if (!battleComplete) {
      console.log('[Commentator] Waiting for battle to complete before starting commentary...');
      lastMessageCountRef.current = chatMessages.length;
      return;
    }

    const generateAndSpeak = async () => {
      try {
        // Get only NEW messages since last check
        const newMessages = chatMessages.slice(lastMessageCountRef.current);

        // Filter to agent messages AND user messages (commentary on everything!)
        const newInterestingMessages = newMessages.filter(msg => {
          // Include agent banter
          if (msg.type === 'agent' && !msg.text.includes('Battle complete') && !msg.text.includes('[COMPOSER]')) {
            return true;
          }
          // Include user messages (typed in chat or voice)
          if (msg.sender === 'user' || msg.text?.includes('[YOU]')) {
            return true;
          }
          return false;
        });

        if (newInterestingMessages.length === 0) {
          lastMessageCountRef.current = chatMessages.length;
          return;
        }

        console.log('[Commentator] New interesting messages:', newInterestingMessages.map(m => m.text));

        // Generate natural commentary from recent messages
        const commentary = await commentatorGeminiRef.current.generateCommentary(chatMessages);

        if (commentary) {
          console.log('[Commentator] Speaking commentary:', commentary);
          elevenLabsRef.current.speak(commentary);
        }

        lastMessageCountRef.current = chatMessages.length;
      } catch (error) {
        console.error('[Commentator] Failed to generate commentary:', error);
        lastMessageCountRef.current = chatMessages.length;
      }
    };

    // Generate commentary immediately for every new message
    generateAndSpeak();
  }, [chatMessages, elevenLabsReady]);

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

    // Toggle ElevenLabs voice output
    if (elevenLabsRef.current) {
      // If unmuting for the first time, resume AudioContext (requires user gesture)
      if (!newMuted && elevenLabsRef.current.audioContext && elevenLabsRef.current.audioContext.state === 'suspended') {
        await elevenLabsRef.current.audioContext.resume();
        console.log('[Commentator] AudioContext resumed after user gesture');
      }

      elevenLabsRef.current.setMuted(newMuted);
      console.log(`[Commentator] ElevenLabs voice ${newMuted ? 'muted' : 'unmuted'}`);
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
