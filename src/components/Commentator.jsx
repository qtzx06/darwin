import { useState, useEffect, useRef } from 'react';
import './Commentator.css';
import NeuroShaderCanvas from './NeuroShaderCanvas';
import CommentatorOrb from './CommentatorOrb';
import { GeminiAudioManager } from '../services/geminiAudioService';
import { CommentatorGeminiService } from '../services/commentatorGeminiService';

function Commentator({ query, onBattleStart, isRunning, agentsReady, chatMessages = [], onElevenLabsReady }) {
  const [analyser, setAnalyser] = useState(null);
  const [isSoundActive, setIsSoundActive] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [loadingMessageIndex, setLoadingMessageIndex] = useState(0);
  const [isOutputMuted, setIsOutputMuted] = useState(true); // Voice output (start muted, user must enable)
  const [audioReady, setAudioReady] = useState(false);
  const [hasSpokenIntro, setHasSpokenIntro] = useState(false);
  const audioManagerRef = useRef(null);
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

  // Initialize Gemini Audio and Gemini when agents are ready
  useEffect(() => {
    const initServices = async () => {
      if (!agentsReady || audioReady) {
        return;
      }

      try {
        console.log('[Commentator] Initializing services...');

        // Create Gemini Audio manager
        if (!audioManagerRef.current) {
          audioManagerRef.current = new GeminiAudioManager();
        }

        // Create Commentator Gemini service
        if (!commentatorGeminiRef.current) {
          commentatorGeminiRef.current = new CommentatorGeminiService();
        }

        // Set up callbacks
        audioManagerRef.current.onSpeechStart = () => {
          setIsSoundActive(true);
        };

        audioManagerRef.current.onSpeechEnd = () => {
          setIsSoundActive(false);
        };

        // Set up commentator transcript callback (handled by parent via onElevenLabsReady)

        // Initialize Gemini Audio
        await audioManagerRef.current.initialize();

        // Get analyser for visualization
        const analyserNode = audioManagerRef.current.getAnalyser();
        setAnalyser(analyserNode);

        setAudioReady(true);
        console.log('[Commentator] Services initialized successfully');

        // Notify parent that audio is ready
        if (onElevenLabsReady) {
          onElevenLabsReady(audioManagerRef);
        }
      } catch (error) {
        console.error('[Commentator] Failed to initialize services:', error);
      }
    };

    initServices();

    return () => {
      // Cleanup on unmount
      if (audioManagerRef.current) {
        audioManagerRef.current.dispose();
      }
      if (commentaryIntervalRef.current) {
        clearInterval(commentaryIntervalRef.current);
      }
    };
  }, [agentsReady]);

  // Speak welcome intro when battle starts
  useEffect(() => {
    if (isRunning && !hasSpokenIntro && audioReady && query) {
      setHasSpokenIntro(true);

      // Get welcome intro
      const intro = commentatorGeminiRef.current.getWelcomeIntro(query);
      console.log('[Commentator] Speaking intro:', intro);
      audioManagerRef.current.speak(intro);
    }
  }, [isRunning, hasSpokenIntro, audioReady, query]);

  // Generate and speak commentary ONLY for user messages after battle complete
  useEffect(() => {
    if (!audioReady || !audioManagerRef.current || !commentatorGeminiRef.current) {
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

        // React to AGENT BANTER and USER messages
        const interestingMessages = newMessages.filter(msg => {
          // Include agent banter (agents talking to each other)
          if (msg.type === 'agent' && !msg.text?.includes('[COMPOSER]') && !msg.text?.includes('Battle complete')) {
            return true;
          }
          // Include user messages (typed in chat or voice)
          if (msg.sender === 'user' || msg.text?.includes('[YOU]')) {
            return true;
          }
          return false;
        });

        if (interestingMessages.length === 0) {
          lastMessageCountRef.current = chatMessages.length;
          return;
        }

        // Don't speak if already speaking (prevent stuttering)
        if (audioManagerRef.current.isProcessingQueue || audioManagerRef.current.hasStartedSpeech) {
          console.log('[Commentator] Already speaking, skipping...');
          return;
        }

        console.log('[Commentator] New interesting messages:', interestingMessages.map(m => m.text));

        // PRIORITIZE USER MESSAGES - if user said something, ONLY react to that
        const userMessages = interestingMessages.filter(msg => msg.sender === 'user' || msg.text?.includes('[YOU]'));

        let messagesToCommentOn;
        if (userMessages.length > 0) {
          // User said something - ONLY comment on the user's message
          messagesToCommentOn = userMessages[userMessages.length - 1]; // Latest user message
          console.log('[Commentator] User message detected, prioritizing:', messagesToCommentOn.text);
        } else if (interestingMessages.length > 3) {
          // Too many agent messages backed up - skip to latest one only
          messagesToCommentOn = interestingMessages[interestingMessages.length - 1];
          console.log('[Commentator] Backlog detected, skipping to latest message:', messagesToCommentOn.text);
        } else {
          // Normal flow - comment on first new message
          messagesToCommentOn = interestingMessages[0];
        }

        // Update count to skip processed messages
        lastMessageCountRef.current = chatMessages.length;

        // Generate observation of what's happening
        const observation = await commentatorGeminiRef.current.generateCommentaryForMessage(messagesToCommentOn, chatMessages);

        if (observation) {
          console.log('[Commentator] Observation:', observation);
          // Send observation to voice AI to react naturally
          console.log('[Commentator] Sending to voice AI to react...');
          audioManagerRef.current.speak(observation);
        }
      } catch (error) {
        console.error('[Commentator] Failed to generate commentary:', error);
      }
    };

    // Generate commentary for user messages only
    generateAndSpeak();
  }, [chatMessages, audioReady]);

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

    // Toggle Gemini Audio voice output
    if (audioManagerRef.current) {
      // If unmuting for the first time, resume AudioContext (requires user gesture)
      if (!newMuted && audioManagerRef.current.audioContext && audioManagerRef.current.audioContext.state === 'suspended') {
        await audioManagerRef.current.audioContext.resume();
        console.log('[Commentator] AudioContext resumed after user gesture');
      }

      audioManagerRef.current.setMuted(newMuted);
      console.log(`[Commentator] Gemini Audio voice ${newMuted ? 'muted' : 'unmuted'}`);
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
