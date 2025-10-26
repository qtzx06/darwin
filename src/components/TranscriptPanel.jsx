import './TranscriptPanel.css';

function TranscriptPanel() {
  return (
    <div className="glass-card transcript-card">
      <div className="glass-filter"></div>
      <div className="glass-overlay"></div>
      <div className="glass-specular"></div>
      <div className="glass-content">
        <div className="transcript-content">
          <h3>Transcript</h3>
          <div className="transcript-text">
            Live commentary stream will appear here...
          </div>
        </div>
      </div>
    </div>
  );
}

export default TranscriptPanel;
