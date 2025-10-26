import { useEffect, useState, useRef } from 'react';
import { motion } from 'framer-motion';
import './Orchestration.css';
import IridescenceBackground from './IridescenceBackground';
import AgentCard from './AgentCard';
import Commentator from './Commentator';
import TranscriptPanel from './TranscriptPanel';
import ChatInput from './ChatInput';
import HeaderDither from './HeaderDither';
import LogoLoop from './LogoLoop';
import { TbBrandThreejs } from 'react-icons/tb';
import { FaReact, FaPython } from 'react-icons/fa';
import { RiClaudeFill, RiGeminiFill } from 'react-icons/ri';
import { SiTypescript, SiLangchain } from 'react-icons/si';
import livekitLogo from '../assets/livekit-text.svg';

function Orchestration() {
  const [query, setQuery] = useState('');
  const [expandedAgent, setExpandedAgent] = useState(null);
  const containerRef = useRef(null);

  // Logo Loop data
  const logos = [
    { node: <TbBrandThreejs style={{ color: 'white' }} />, title: 'Three.js' },
    { node: <FaReact style={{ color: 'white' }} />, title: 'React' },
    { node: <RiClaudeFill style={{ color: 'white' }} />, title: 'Claude' },
    { node: <SiTypescript style={{ color: 'white' }} />, title: 'TypeScript' },
    { node: <FaPython style={{ color: 'white' }} />, title: 'Python' },
    { node: <SiLangchain style={{ color: 'white' }} />, title: 'LangChain' },
    { node: <RiGeminiFill style={{ color: 'white' }} />, title: 'Gemini' },
    { src: 'https://raw.githubusercontent.com/letta-ai/letta/main/assets/Letta-logo-RGB_GreyonTransparent_cropped_small.png', alt: 'Letta', title: 'Letta' },
    { node: <img src={livekitLogo} alt="LiveKit" style={{ height: '24px', width: 'auto', filter: 'brightness(0) invert(1)' }} />, title: 'LiveKit' },
  ];

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
            <div className="header-text">
              <span className="header-title">DARWIN // </span>
              <span className="header-subtitle">evolve your agents.</span>
            </div>
            {query && (
              <div className="header-query">
                <span className="header-query-label">Query:</span>
                <span className="header-query-text">{query}</span>
              </div>
            )}
            <div className="header-logo-loop">
              <LogoLoop
                logos={logos}
                speed={60}
                direction="left"
                logoHeight={20}
                gap={24}
                pauseOnHover={false}
                fadeOut={true}
              />
            </div>
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
