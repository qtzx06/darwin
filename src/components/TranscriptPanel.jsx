import { useState } from 'react';
import './TranscriptPanel.css';

function TranscriptPanel({ geminiLiveRef }) {
  const [isMicMuted, setIsMicMuted] = useState(true); // Start with mic muted

  const handleMicToggle = async () => {
    const newMuted = !isMicMuted;
    setIsMicMuted(newMuted);

    // Toggle microphone via Gemini Live
    if (geminiLiveRef?.current) {
      await geminiLiveRef.current.setMicMuted(newMuted);
      console.log(`[TranscriptPanel] Microphone ${newMuted ? 'muted' : 'unmuted'}`);
    }
  };

  return (
    <div className="glass-card transcript-card">
      <div className="glass-filter"></div>
      <div className="glass-overlay"></div>
      <div className="glass-specular"></div>
      <div className="glass-content">
        <div className="transcript-header">
          <div>
            <h3>Transcription</h3>
            <div className="transcript-description">live audio commentary stream</div>
          </div>
          <button onClick={handleMicToggle} className="transcript-mute">
            <i className={`fas fa-microphone${isMicMuted ? '-slash' : ''}`}></i>
          </button>
        </div>
        <div className="transcript-box">
          <div className="glass-filter"></div>
          <div className="glass-overlay"></div>
          <div className="glass-specular"></div>
          <div className="transcript-text">
            Live commentary stream will appear here...
          </div>
        </div>
      </div>
    </div>
  );
}

export default TranscriptPanel;
