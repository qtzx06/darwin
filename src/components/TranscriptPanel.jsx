import { useState } from 'react';
import './TranscriptPanel.css';

function TranscriptPanel({ elevenLabsRef, transcripts = [] }) {
  const [isMicMuted, setIsMicMuted] = useState(true); // Start with mic muted

  const handleMicToggle = async () => {
    const newMuted = !isMicMuted;
    setIsMicMuted(newMuted);

    // Toggle microphone via ElevenLabs
    if (elevenLabsRef?.current) {
      await elevenLabsRef.current.setMicMuted(newMuted);
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
            {transcripts.length === 0 ? (
              <div style={{ opacity: 0.5 }}>
                {isMicMuted ? 'Click mic button to start...' : 'Listening...'}
              </div>
            ) : (
              transcripts.map((t, i) => (
                <div key={i} style={{ marginBottom: '8px' }}>
                  <span style={{ color: '#f0b0d0', fontWeight: 'bold' }}>
                    [{t.speaker === 'user' ? 'YOU' : 'COMPOSER'}]
                  </span>{' '}
                  {t.text}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default TranscriptPanel;