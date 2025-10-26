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
