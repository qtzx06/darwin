import { useState } from 'react';
import './TranscriptPanel.css';

function TranscriptPanel() {
  const [isMuted, setIsMuted] = useState(false);

  const handleMuteToggle = () => {
    setIsMuted(!isMuted);
    console.log('Mute toggled:', !isMuted);
    // TODO: Handle audio mute/unmute
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
          <button onClick={handleMuteToggle} className="transcript-mute">
            <i className={`fas fa-microphone${isMuted ? '-slash' : ''}`}></i>
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