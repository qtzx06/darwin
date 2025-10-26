import { useState } from 'react';
import './BattleControl.css';

function BattleControl({ query, onBattleStart, isRunning }) {
  const [isHovered, setIsHovered] = useState(false);

  const handleStart = () => {
    if (!isRunning && query) {
      onBattleStart();
    }
  };

  return (
    <div className="glass-card battle-control-card">
      <div className="glass-filter"></div>
      <div className="glass-overlay"></div>
      <div className="glass-specular"></div>
      <div className="glass-content">
        <div className="battle-header">
          <div>
            <h3>AI Battle</h3>
            <div className="battle-description">competitive code generation arena</div>
          </div>
          <button
            type="button"
            onClick={handleStart}
            disabled={isRunning || !query}
            className={`battle-button ${isRunning ? 'running' : ''}`}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
          >
            {isRunning ? (
              <>
                <i className="fas fa-circle-notch fa-spin"></i>
                <span>Running</span>
              </>
            ) : (
              <>
                <i className="fas fa-rocket"></i>
                <span>{isHovered ? 'Let them cook' : 'Start Battle'}</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

export default BattleControl;
