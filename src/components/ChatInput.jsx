import { useState, useEffect, useRef } from 'react';
import './ChatInput.css';

function ChatInput({ externalMessages = [], onUserMessage }) {
  const [inputValue, setInputValue] = useState('');
  const [messages, setMessages] = useState([]);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (externalMessages.length > 0) {
      setMessages(externalMessages);
    }
  }, [externalMessages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim() && onUserMessage) {
      // Send message to parent
      onUserMessage(inputValue.trim());
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
              {messages.map((msg, idx) => {
                // Extract [PREFIX] from message text
                const match = msg.text.match(/^\[([^\]]+)\]\s*(.*)/);
                const prefix = match ? match[1] : '';
                const content = match ? match[2] : msg.text;

                return (
                  <div key={`${msg.timestamp}-${idx}`} className={`chat-message chat-message-${msg.type || 'server'}`}>
                    {prefix && <span className="chat-prefix">[{prefix}]</span>}
                    {prefix && ' '}
                    {content}
                  </div>
                );
              })}
              <div ref={messagesEndRef} />
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
