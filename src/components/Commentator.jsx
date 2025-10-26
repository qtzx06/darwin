import './Commentator.css';
import LiquidChrome from './LiquidChrome';

function Commentator() {
  return (
    <div className="glass-card commentator-card">
      <div className="glass-filter"></div>
      <div className="glass-overlay"></div>
      <div className="glass-specular"></div>
      <div className="glass-content">
        <div className="commentator-headshot">
          <LiquidChrome
            baseColor={[0.06, 0.04, 0.10]}
            speed={0.25}
            amplitude={0.5}
            frequencyX={2.5}
            frequencyY={2.5}
            interactive={false}
          />
        </div>
      </div>
    </div>
  );
}

export default Commentator;
