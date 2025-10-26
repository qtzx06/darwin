import { useState } from 'react';
import './ChatInput.css';

function ChatInput() {
  const [inputValue, setInputValue] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim()) {
      console.log('Chat message:', inputValue);
      // TODO: Handle chat submission
      setInputValue('');
    }
  };

  return (
    <div className="glass-card chat-input-card">
      <div className="glass-filter"></div>
      <div className="glass-overlay"></div>
      <div className="glass-specular"></div>
      <div className="glass-content">
        <div className="chat-header">
          <div>
            <h3>Chat</h3>
            <div className="chat-description">multi-agent conversation interface</div>
          </div>
          <button type="button" onClick={handleSubmit} className="chat-send">
            <i className="fas fa-paper-plane"></i>
          </button>
        </div>
        <div className="chat-box">
          <div className="glass-filter"></div>
          <div className="glass-overlay"></div>
          <div className="glass-specular"></div>
          <div className="chat-messages">
            {/* Messages will appear here */}
          </div>
          <form onSubmit={handleSubmit} className="chat-form">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="type a message..."
              className="chat-input"
            />
          </form>
        </div>
      </div>
    </div>
  );
}

export default ChatInput;
