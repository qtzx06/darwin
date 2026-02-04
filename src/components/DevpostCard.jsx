import { useState } from 'react';
import './DevpostCard.css';

function DevpostCard() {
  const [showQuack, setShowQuack] = useState(false);

  const handleLogoClick = () => {
    setShowQuack(true);
    setTimeout(() => {
      setShowQuack(false);
    }, 1500);
  };

  return (
    <div className="footer-container">
      <div className="logo-wrapper">
        {showQuack && <div className="quack-text">*quack!*</div>}
        <img
          src="/favicon.png"
          alt="Logo"
          className="footer-logo"
          onClick={handleLogoClick}
          style={{ cursor: 'pointer' }}
        />
      </div>
      <div className="footer-text">
        read the{' '}
        <a href="https://github.com/qtzx06/darwin" target="_blank" rel="noopener noreferrer" className="footer-link">
          github
        </a>
        {' '}or{' '}
        <a href="https://devpost.com/software/darwin-w6fez0" target="_blank" rel="noopener noreferrer" className="footer-link">
          devpost
        </a>
        !
      </div>
    </div>
  );
}

export default DevpostCard;
