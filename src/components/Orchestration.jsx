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
import { getVoteCounts } from '../utils/suiClient';
import { competitiveApi } from '../services/api';

function Orchestration() {
  const [query, setQuery] = useState('');
  const [expandedAgent, setExpandedAgent] = useState(null);
  const [showFadeOverlay, setShowFadeOverlay] = useState(true);
  const [chatMessages, setChatMessages] = useState([]);
  const [voteCounts, setVoteCounts] = useState({
    speedrunner: 0,
    bloom: 0,
    solver: 0,
    loader: 0
  });
  const [blockchainVotes, setBlockchainVotes] = useState({
    speedrunner: 0,
    bloom: 0,
    solver: 0,
    loader: 0
  });
  const [isBattleRunning, setIsBattleRunning] = useState(false);
  const [agentsReady, setAgentsReady] = useState(false);
  const [cachedProjectId, setCachedProjectId] = useState(null);
  const [agentCode, setAgentCode] = useState({
    speedrunner: null,
    bloom: null,
    solver: null,
    loader: null
  });
  const containerRef = useRef(null);

  // Fetch blockchain vote counts on mount and every 10 seconds
  useEffect(() => {
    const fetchVotes = async () => {
      try {
        const counts = await getVoteCounts();
        setBlockchainVotes(counts);
      } catch (error) {
        console.error('Failed to fetch blockchain votes:', error);
      }
    };

    fetchVotes(); // Initial fetch
    const interval = setInterval(fetchVotes, 10000); // Fetch every 10 seconds

    return () => clearInterval(interval);
  }, []);

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

  // Preload agents when query is available
  useEffect(() => {
    if (!query || cachedProjectId) return;

    const preloadAgents = async () => {
      try {
        console.log('🔄 Preloading agents...');

        // Submit project and create agents in background
        const project = await competitiveApi.submitProject(query);
        await competitiveApi.createAgents(project.project_id);

        setCachedProjectId(project.project_id);
        setAgentsReady(true);
        console.log('✅ Agents ready!', project.project_id);
      } catch (error) {
        console.error('Failed to preload agents:', error);
      }
    };

    preloadAgents();
  }, [query, cachedProjectId]);

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

  const handleAgentLike = (agentName, agentId) => {
    // Increment vote count
    setVoteCounts(prev => ({
      ...prev,
      [agentId]: prev[agentId] + 1
    }));

    // Send message to chat
    const likeMessage = {
      text: `user liked ${agentName}'s work`,
      timestamp: Date.now()
    };
    setChatMessages(prev => [...prev, likeMessage]);
  };

  const handleBattleStart = async () => {
    if (!query || isBattleRunning || !agentsReady) return;

    setIsBattleRunning(true);
    const addChatMessage = (text) => {
      setChatMessages(prev => [...prev, {
        text,
        timestamp: Date.now() + Math.random() // Add randomness to prevent duplicate keys
      }]);
    };

    addChatMessage('🔥 AI battle started! Agents are generating code...');

    try {
      // Use cached project ID (agents already created!)
      const projectId = cachedProjectId;
      console.log('Using cached project:', projectId);

      // Orchestrate project into subtasks
      const orchestration = await competitiveApi.orchestrateProject(query);
      console.log('Orchestration:', orchestration);

      if (orchestration.subtasks && orchestration.subtasks.length > 0) {
        const firstSubtask = orchestration.subtasks[0];

        // Start work on first subtask
        await competitiveApi.startWork(projectId, firstSubtask.id);
        console.log('Work started on subtask:', firstSubtask.id);

        // Get results from all agents
        const agentNames = ['One', 'Two', 'Three', 'Four'];
        const results = await competitiveApi.getResults(projectId, agentNames);
        console.log('Agent results:', results);

        if (results.agents && results.agents.length > 0) {
          // Map agent names to our agent IDs
          const agentMap = { 'One': 'speedrunner', 'Two': 'bloom', 'Three': 'solver', 'Four': 'loader' };

          const newAgentCode = {};
          results.agents.forEach(agent => {
            const agentId = agentMap[agent.agent_name];
            if (agentId) {
              newAgentCode[agentId] = agent.code;
            }
          });

          setAgentCode(newAgentCode);
          addChatMessage('✅ Battle complete! Check agent cards for generated code.');
        }
      }
    } catch (error) {
      console.error('Battle error:', error);
      addChatMessage(`❌ Battle failed: ${error.message}`);
    } finally {
      setIsBattleRunning(false);
    }
  };

  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') setExpandedAgent(null);
    };
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, []);

  useEffect(() => {
    // Fade out the black overlay after component mounts
    const timer = setTimeout(() => {
      setShowFadeOverlay(false);
    }, 100); // Small delay to ensure it renders first
    return () => clearTimeout(timer);
  }, []);

  return (
    <motion.div
      ref={containerRef}
      className="orchestration-container"
      initial={{ opacity: 1 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <IridescenceBackground />

      {/* Black fade overlay */}
      <motion.div
        className="fade-overlay"
        initial={{ opacity: 1 }}
        animate={{ opacity: showFadeOverlay ? 1 : 0 }}
        transition={{ duration: 1.5, ease: "easeOut" }}
        style={{ pointerEvents: showFadeOverlay ? 'auto' : 'none' }}
      />

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
            onLike={handleAgentLike}
            voteCount={blockchainVotes.speedrunner}
            generatedCode={agentCode.speedrunner}
          />
          <AgentCard
            agentId="bloom"
            agentName="Bloom"
            isExpanded={expandedAgent === 'bloom'}
            onExpand={handleExpandAgent}
            onLike={handleAgentLike}
            voteCount={blockchainVotes.bloom}
            generatedCode={agentCode.bloom}
          />
          <AgentCard
            agentId="solver"
            agentName="Solver"
            isExpanded={expandedAgent === 'solver'}
            onExpand={handleExpandAgent}
            onLike={handleAgentLike}
            voteCount={blockchainVotes.solver}
            generatedCode={agentCode.solver}
          />
          <AgentCard
            agentId="loader"
            agentName="Loader"
            isExpanded={expandedAgent === 'loader'}
            onExpand={handleExpandAgent}
            onLike={handleAgentLike}
            voteCount={blockchainVotes.loader}
            generatedCode={agentCode.loader}
          />

          {/* Commentator with Battle Controls */}
          <Commentator
            query={query}
            onBattleStart={handleBattleStart}
            isRunning={isBattleRunning}
            agentsReady={agentsReady}
          />

          {/* Chat Input */}
          <ChatInput externalMessages={chatMessages} />

          {/* Transcript */}
          <TranscriptPanel />
        </div>
      </div>
    </motion.div>
  );
}

export default Orchestration;
