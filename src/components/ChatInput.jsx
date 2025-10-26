import { useState, useEffect } from 'react';
import { claudeChatApi } from '../services/api';
import './ChatInput.css';

function ChatInput({ externalMessages = [] }) {
  const [inputValue, setInputValue] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

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

  // Background random message polling
  useEffect(() => {
    const fetchRandomMessage = async () => {
      // Don't fetch if user is currently interacting
      if (isLoading) return;
      
      try {
        const response = await claudeChatApi.getRandomMessage();
        if (response.success && response.message) {
          const msg = response.message;
          const randomMessage = {
            text: msg.message,
            timestamp: msg.timestamp,
            speaker: msg.agent,
            isUser: false
          };
          setMessages(prev => [...prev, randomMessage]);
          console.log(`🎲 Random: ${msg.agent}: ${msg.message}`);
        }
      } catch (error) {
        // Silently fail - random messages are not critical
        console.debug('Random message fetch failed:', error);
      }
    };

    // Fetch random message every 15-25 seconds
    const getRandomInterval = () => Math.random() * 10000 + 15000; // 15-25 seconds
    
    let timeoutId;
    const scheduleNext = () => {
      timeoutId = setTimeout(() => {
        fetchRandomMessage();
        scheduleNext();
      }, getRandomInterval());
    };
    
    // Start the first random message after 5 seconds
    const initialTimeout = setTimeout(() => {
      fetchRandomMessage();
      scheduleNext();
    }, 5000);
    
    return () => {
      clearTimeout(initialTimeout);
      clearTimeout(timeoutId);
    };
  }, [isLoading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (inputValue.trim() && !isLoading) {
      const userMessage = inputValue.trim();
      const userTimestamp = Date.now();
      
      // Add user message immediately
      const newMessage = { 
        text: userMessage, 
        timestamp: userTimestamp,
        speaker: 'Boss',
        isUser: true
      };
      setMessages(prev => [...prev, newMessage]);
      setInputValue('');
      setIsLoading(true);

      try {
        // Send to Claude chat API
        console.log('💬 Sending message to Claude:', userMessage);
        const response = await claudeChatApi.sendMessage(userMessage);
        
        if (response.success && response.messages) {
          // Add agent responses one by one with delays
          console.log('✅ Received', response.messages.length, 'agent responses');
          
          // Process messages sequentially with their delays
          for (let i = 0; i < response.messages.length; i++) {
            const msg = response.messages[i];
            
            // Wait for the specified delay before showing this message
            if (i > 0) {
              await new Promise(resolve => setTimeout(resolve, msg.delay || 1500));
            }
            
            // Add this message to the chat
            const agentMessage = {
              text: msg.message,
              timestamp: msg.timestamp,
              speaker: msg.agent,
              isUser: false
            };
            setMessages(prev => [...prev, agentMessage]);
            console.log(`💬 ${msg.agent}: ${msg.message}`);
          }
        } else {
          console.error('❌ Failed to get responses:', response.error);
          // Add error message
          setMessages(prev => [...prev, {
            text: '⚠️ Failed to get response from agents',
            timestamp: Date.now(),
            speaker: 'System',
            isUser: false
          }]);
        }
      } catch (error) {
        console.error('❌ Chat error:', error);
        setMessages(prev => [...prev, {
          text: '⚠️ Error connecting to chat service',
          timestamp: Date.now(),
          speaker: 'System',
          isUser: false
        }]);
      } finally {
        setIsLoading(false);
      }
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
          <button 
            type="button" 
            onClick={handleSubmit} 
            className="chat-send"
            disabled={isLoading || !inputValue.trim()}
          >
            {isLoading ? (
              <i className="fas fa-spinner fa-spin"></i>
            ) : (
              <i className="fas fa-paper-plane"></i>
            )}
          </button>
        </div>
        <div className="chat-box">
          <div className="glass-filter"></div>
          <div className="glass-overlay"></div>
          <div className="glass-specular"></div>
          <div className="chat-content-wrapper">
            <div className="chat-messages">
              {messages.map((msg) => (
                <div key={msg.timestamp} className={`chat-message ${msg.isUser ? 'user-message' : 'agent-message'}`}>
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
                disabled={isLoading}
              />
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ChatInput;
