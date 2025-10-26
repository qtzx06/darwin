import { useState, useEffect } from 'react';
import './ChatInput.css';

function ChatInput({ externalMessages = [] }) {
  const [inputValue, setInputValue] = useState('');
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    if (externalMessages.length > 0) {
      // Only add new messages
      const newMessages = externalMessages.filter(
        extMsg => !messages.some(msg => msg.timestamp === extMsg.timestamp)
      );
      if (newMessages.length > 0) {
        setMessages(prev => [...prev, ...newMessages]);
      }
    }
  }, [externalMessages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim()) {
      const newMessage = { text: inputValue, timestamp: Date.now() };
      setMessages(prev => [...prev, newMessage]);
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
          <div className="chat-content-wrapper">
            <div className="chat-messages">
              {messages.map((msg) => (
                <div key={msg.timestamp} className={`chat-message ${msg.speaker ? 'agent-message' : 'user-message'}`}>
                  {msg.speaker && <span className="message-speaker">{msg.speaker}:</span>}
                  <span className="message-text">{msg.text}</span>
                  {msg.emotion !== undefined && (
                    <span className="message-emotion" title={`Emotion: ${msg.emotion}`}>
                      {msg.emotion > 0.7 ? '🔥' : msg.emotion > 0.4 ? '😤' : '😐'}
                    </span>
                  )}
                </div>
              ))}
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
    </div>
  );
}

export default ChatInput;
