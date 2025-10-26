import './Commentator.css';

function Commentator() {
  return (
    <div className="glass-card commentator-card">
      <div className="glass-filter"></div>
      <div className="glass-overlay"></div>
      <div className="glass-specular"></div>
      <div className="glass-content">
        <div className="agent-name" style={{ alignSelf: 'center' }}>
          Commentator
        </div>
        <div id="visualizer-container">
          {/* Audio visualizer will go here */}
        </div>
      </div>
    </div>
  );
}

export default Commentator;
