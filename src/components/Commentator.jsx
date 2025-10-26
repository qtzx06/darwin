import { useState, useEffect, useRef } from 'react';
import './Commentator.css';
import NeuroShaderCanvas from './NeuroShaderCanvas';
import CommentatorOrb from './CommentatorOrb';

function Commentator({ query, onBattleStart, isRunning, agentsReady }) {
  const [analyser, setAnalyser] = useState(null);
  const [isSoundActive, setIsSoundActive] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [loadingMessageIndex, setLoadingMessageIndex] = useState(0);
  const audioContextRef = useRef(null);

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

  useEffect(() => {
    // Create audio context and analyser
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    audioContextRef.current = audioContext;

    const analyserNode = audioContext.createAnalyser();
    analyserNode.fftSize = 512;

    // Create a silent oscillator to keep the audio context active
    const oscillator = audioContext.createOscillator();
    oscillator.frequency.value = 0;
    oscillator.connect(analyserNode);
    analyserNode.connect(audioContext.destination);
    oscillator.start();

    setAnalyser(analyserNode);

    return () => {
      oscillator.stop();
      audioContext.close();
    };
  }, []);

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

  return (
    <div className="glass-card commentator-card">
      <div className="glass-filter"></div>
      <div className="glass-overlay"></div>
      <div className="glass-specular"></div>
      <div className="glass-content">
        <div className="commentator-header">
          <div>
            <h3>
              {!agentsReady && query ? loadingMessages[loadingMessageIndex] : 'Start Hunger Games'}
            </h3>
            <div className="commentator-description">competitive code generation arena</div>
          </div>
          <button
            type="button"
            onClick={handleStart}
            disabled={isRunning || !query || !agentsReady}
            className={`commentator-battle-button ${isRunning ? 'running' : !agentsReady ? 'loading' : ''}`}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
          >
            {isRunning ? (
              <i className="fas fa-circle-notch fa-spin"></i>
            ) : !agentsReady ? (
              <i className="fas fa-circle-notch fa-spin"></i>
            ) : (
              <i className="fas fa-rocket"></i>
            )}
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
