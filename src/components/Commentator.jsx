import { useState, useEffect, useRef } from 'react';
import './Commentator.css';
import NeuroShaderCanvas from './NeuroShaderCanvas';
import CommentatorOrb from './CommentatorOrb';

function Commentator() {
  const [analyser, setAnalyser] = useState(null);
  const [isSoundActive, setIsSoundActive] = useState(false);
  const audioContextRef = useRef(null);

  useEffect(() => {
    // Create audio context lazily after user interaction to avoid autoplay warnings
    const initAudioContext = () => {
      if (audioContextRef.current) return;
      
      try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        
        // Resume context if suspended (required by browsers)
        if (audioContext.state === 'suspended') {
          audioContext.resume();
        }
        
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
      } catch (error) {
        // Silently fail - audio context not critical for app functionality
      }
    };

    // Initialize on first user interaction
    const handleUserInteraction = () => {
      initAudioContext();
      document.removeEventListener('click', handleUserInteraction);
      document.removeEventListener('keydown', handleUserInteraction);
      document.removeEventListener('touchstart', handleUserInteraction);
    };

    document.addEventListener('click', handleUserInteraction);
    document.addEventListener('keydown', handleUserInteraction);
    document.addEventListener('touchstart', handleUserInteraction);

    return () => {
      document.removeEventListener('click', handleUserInteraction);
      document.removeEventListener('keydown', handleUserInteraction);
      document.removeEventListener('touchstart', handleUserInteraction);
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, []);

  return (
    <div className="glass-card commentator-card">
      <div className="glass-filter"></div>
      <div className="glass-overlay"></div>
      <div className="glass-specular"></div>
      <div className="glass-content">
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