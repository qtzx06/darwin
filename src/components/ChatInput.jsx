import { useState, useEffect } from 'react';
import './ChatInput.css';

function ChatInput({ externalMessages = [] }) {
  const [inputValue, setInputValue] = useState('');
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    if (externalMessages.length > 0) {
      setMessages(prev => [...prev, ...externalMessages.slice(prev.length - externalMessages.length)]);
    }
  }, [externalMessages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim()) {
      const newMessage = {
        text: `[YOU] ${inputValue}`,
        type: 'user',
        timestamp: Date.now()
      };
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
              {messages.map((msg) => {
                // Extract [PREFIX] from message text
                const match = msg.text.match(/^\[([^\]]+)\]\s*(.*)/);
                const prefix = match ? match[1] : '';
                const content = match ? match[2] : msg.text;

                return (
                  <div key={msg.timestamp} className={`chat-message chat-message-${msg.type || 'server'}`}>
                    {prefix && <span className="chat-prefix">[{prefix}]</span>}
                    {prefix && ' '}
                    {content}
                  </div>
                );
              })}
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
