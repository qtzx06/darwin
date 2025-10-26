import { useState, useEffect, useRef } from 'react';
import './TranscriptPanel.css';

function TranscriptPanel({ roomName, messages = [], onUserQuestion }) {
  const [isListening, setIsListening] = useState(false);
  const [interimTranscript, setInterimTranscript] = useState('');
  const transcriptEndRef = useRef(null);
  const recognitionRef = useRef(null);

  const handleMicToggle = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  const startListening = () => {
    // Check if speech recognition is supported
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('Speech recognition not supported in this browser. Please use Chrome or Edge.');
      return;
    }

    try {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      recognitionRef.current = recognition;

      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        setIsListening(true);
        setInterimTranscript('');
        console.log('🎤 Speech recognition started');
      };

      recognition.onresult = (event) => {
        let interim = '';
        let final = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            final += transcript;
          } else {
            interim += transcript;
          }
        }

        // Show interim results
        if (interim) {
          setInterimTranscript(interim);
        }

        // Process final result
        if (final) {
          const question = final.trim();
          console.log('🗣️ User said:', question);
          setInterimTranscript('');
          setIsListening(false);
          
          // Send question to parent component (Orchestration)
          if (onUserQuestion && question) {
            onUserQuestion(question);
          }
        }
      };

      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        setInterimTranscript('');
        
        if (event.error === 'not-allowed') {
          alert('Microphone access denied. Please enable microphone permissions.');
        }
      };

      recognition.onend = () => {
        setIsListening(false);
        setInterimTranscript('');
        console.log('🎤 Speech recognition ended');
      };

      recognition.start();
    } catch (error) {
      console.error('Error starting speech recognition:', error);
      alert('Failed to start microphone. Please check permissions.');
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }
    setIsListening(false);
    setInterimTranscript('');
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    transcriptEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="glass-card transcript-card">
      <div className="glass-filter"></div>
      <div className="glass-overlay"></div>
      <div className="glass-specular"></div>
      <div className="glass-content">
        <div className="transcript-header">
          <div>
            <h3>Transcription</h3>
            <div className="transcript-description">
              {isListening ? '🎤 Listening...' : 'live audio commentary stream'}
            </div>
          </div>
          <button 
            onClick={handleMicToggle} 
            className={`transcript-mute ${isListening ? 'listening' : ''}`}
            title={isListening ? 'Stop listening' : 'Ask commentator a question'}
          >
            <i className={`fas fa-microphone${isListening ? '' : '-slash'}`}></i>
          </button>
        </div>
        <div className="transcript-box">
          <div className="glass-filter"></div>
          <div className="glass-overlay"></div>
          <div className="glass-specular"></div>
          <div className="transcript-text">
            {messages.length === 0 && !interimTranscript ? (
              <div className="transcript-empty">Live commentary stream will appear here...</div>
            ) : (
              <>
                {messages.map((msg, index) => (
                  <div key={`${msg.timestamp}-${index}`} className="transcript-message">
                    <span className="transcript-speaker">{msg.speaker}:</span>
                    <span className="transcript-content">{msg.text}</span>
                  </div>
                ))}
                {interimTranscript && (
                  <div className="transcript-message interim">
                    <span className="transcript-speaker">You:</span>
                    <span className="transcript-content">{interimTranscript}</span>
                  </div>
                )}
              </>
            )}
            <div ref={transcriptEndRef} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default TranscriptPanel;