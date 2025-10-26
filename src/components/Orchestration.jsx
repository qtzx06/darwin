import { useEffect, useState, useRef } from 'react';
import { motion } from 'framer-motion';
import './Orchestration.css';
import IridescenceBackground from './IridescenceBackground';
import AgentCard from './AgentCard';
import Commentator from './Commentator';
import TranscriptPanel from './TranscriptPanel';
import ChatInput from './ChatInput';
import HeaderDither from './HeaderDither';

function Orchestration() {
  const [query, setQuery] = useState('');
  const [expandedAgent, setExpandedAgent] = useState(null);
  const containerRef = useRef(null);

  useEffect(() => {
    // Extract query from URL hash
    const hash = window.location.hash;
    const params = new URLSearchParams(hash.split('?')[1]);
    const q = params.get('q');
    if (q) {
      setQuery(decodeURIComponent(q));
    }
  }, []);

  // Spotlight effect mouse tracking
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleMouseMove = (e) => {
      const rect = container.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 100;
      const y = ((e.clientY - rect.top) / rect.height) * 100;
      container.style.setProperty('--mouse-x', `${x}%`);
      container.style.setProperty('--mouse-y', `${y}%`);
    };

    container.addEventListener('mousemove', handleMouseMove);
    return () => container.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const handleExpandAgent = (agentId) => {
    setExpandedAgent(expandedAgent === agentId ? null : agentId);
  };

  const handleClickOutside = () => {
    setExpandedAgent(null);
  };

  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') setExpandedAgent(null);
    };
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, []);

  return (
    <motion.div
      ref={containerRef}
      className="orchestration-container"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <IridescenceBackground />

      {/* Backdrop for clicking outside */}
      {expandedAgent && (
        <div className="expansion-backdrop" onClick={handleClickOutside} />
      )}

      {/* Bento Box Layout */}
      <div className="bento-container">
        {/* Header with Dither Animation */}
        <div className="header-space">
          <HeaderDither />
          <div className="header-content">
            <img src="/favicon.png" alt="Darwin Logo" className="header-logo" />
            <span className="header-title">DARWIN</span>
            <span className="header-subtitle">evolve your agents</span>
          </div>
        </div>

        <div className="bento-grid">
          {/* Agent Cards */}
          <AgentCard
            agentId="speedrunner"
            agentName="Speedrunner"
            isExpanded={expandedAgent === 'speedrunner'}
            onExpand={handleExpandAgent}
          />
          <AgentCard
            agentId="bloom"
            agentName="Bloom"
            isExpanded={expandedAgent === 'bloom'}
            onExpand={handleExpandAgent}
          />
          <AgentCard
            agentId="solver"
            agentName="Solver"
            isExpanded={expandedAgent === 'solver'}
            onExpand={handleExpandAgent}
          />
          <AgentCard
            agentId="loader"
            agentName="Loader"
            isExpanded={expandedAgent === 'loader'}
            onExpand={handleExpandAgent}
          />

          {/* Commentator */}
          <Commentator />

          {/* Chat Input */}
          <ChatInput />

          {/* Transcript */}
          <TranscriptPanel />
        </div>
      </div>
    </motion.div>
  );
}

export default Orchestration;
