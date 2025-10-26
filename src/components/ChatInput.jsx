import { useRef, useState } from 'react';
import './ChatInput.css';

function ChatInput() {
  const cardRef = useRef(null);
  const [inputValue, setInputValue] = useState('');

  const handleMouseMove = (e) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // Calculate tilt based on mouse position
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    const rotateX = (y - centerY) / 20;
    const rotateY = (centerX - x) / 20;

    cardRef.current.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;

    // Specular highlight
    const specular = cardRef.current.querySelector('.glass-specular');
    if (specular) {
      specular.style.background = `radial-gradient(circle at ${x}px ${y}px, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0.05) 30%, rgba(255,255,255,0) 60%)`;
    }
  };

  const handleMouseLeave = () => {
    if (!cardRef.current) return;
    cardRef.current.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';

    const specular = cardRef.current.querySelector('.glass-specular');
    if (specular) {
      specular.style.background = 'none';
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim()) {
      console.log('Chat message:', inputValue);
      // TODO: Handle chat submission
      setInputValue('');
    }
  };

  return (
    <div
      ref={cardRef}
      className="glass-card chat-input-card"
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      <div className="glass-filter"></div>
      <div className="glass-overlay"></div>
      <div className="glass-specular"></div>
      <div className="glass-content">
        <div className="chat-input-content">
          <h3>Chat</h3>
          <form onSubmit={handleSubmit} className="chat-form">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Type a message..."
              className="chat-input"
            />
            <button type="submit" className="chat-submit">
              <i className="fas fa-paper-plane"></i>
            </button>
          </form>
          <div className="chat-messages">
            {/* Messages will appear here */}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ChatInput;
