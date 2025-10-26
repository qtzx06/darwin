import { useEffect, useState, useRef } from 'react';
import { motion } from 'framer-motion';
import './Orchestration.css';
import './PreviewCard.css';
import IridescenceBackground from './IridescenceBackground';
import AgentCard from './AgentCard';
import Commentator from './Commentator';
import TranscriptPanel from './TranscriptPanel';
import ChatInput from './ChatInput';
import HeaderDither from './HeaderDither';
import LogoLoop from './LogoLoop';
import CodeRenderer from './CodeRenderer';
import { TbBrandThreejs } from 'react-icons/tb';
import { FaReact, FaPython } from 'react-icons/fa';
import { RiClaudeFill, RiGeminiFill } from 'react-icons/ri';
import { SiTypescript, SiLangchain } from 'react-icons/si';
import livekitLogo from '../assets/livekit-text.svg';
import { getVoteCounts, getAgentWalletBalances } from '../utils/suiClient';
import { startCompetitiveBattle } from '../services/geminiService';

function Orchestration() {
  const [query, setQuery] = useState('');
  const [expandedAgent, setExpandedAgent] = useState(null);
  const [showFadeOverlay, setShowFadeOverlay] = useState(true);
  const [chatMessages, setChatMessages] = useState([
    {
      text: '[SERVER] Darwin systems initialized',
      type: 'server',
      timestamp: Date.now()
    }
  ]);
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
  const [agentBalances, setAgentBalances] = useState({
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
  const [agentStatus, setAgentStatus] = useState({
    speedrunner: '',
    bloom: '',
    solver: '',
    loader: ''
  });
  const [previewCode, setPreviewCode] = useState(null);
  const banterIntervalRef = useRef(null);

  // Debug: Log when previewCode changes
  useEffect(() => {
    console.log('Preview code state:', previewCode ? 'HAS CODE' : 'NULL');
  }, [previewCode]);
  const containerRef = useRef(null);

  // Autonomous banter loop - agents randomly review each other's code
  useEffect(() => {
    const startAutonomousBanter = async () => {
      const { generateRandomBanter, shouldAgentsSpontaneouslyBanter } = await import('../services/geminiService');

      const runBanterCycle = async () => {
        // Check if agents have code and should banter
        const hasCode = Object.values(agentCode).some(code => code);
        if (!hasCode || isBattleRunning) return;

        const shouldBanter = await shouldAgentsSpontaneouslyBanter(chatMessages, agentCode);
        if (!shouldBanter) return;

        // Pick a random agent to speak
        const agents = ['speedrunner', 'bloom', 'solver', 'loader'];
        const activeAgents = agents.filter(id => agentCode[id]);
        if (activeAgents.length === 0) return;

        const randomAgent = activeAgents[Math.floor(Math.random() * activeAgents.length)];

        try {
          const banter = await generateRandomBanter(randomAgent, agentCode, chatMessages);

          if (banter) {
            const agentNames = {
              speedrunner: 'SPEEDRUNNER',
              bloom: 'BLOOM',
              solver: 'SOLVER',
              loader: 'LOADER'
            };

            setChatMessages(prev => [...prev, {
              text: `[${agentNames[randomAgent]}] ${banter}`,
              type: 'agent',
              timestamp: Date.now() + Math.random()
            }]);
          }
        } catch (error) {
          console.error('Autonomous banter failed:', error);
        }
      };

      // Run banter check every 12-20 seconds (randomized)
      const scheduleNextBanter = () => {
        const delay = 12000 + Math.random() * 8000; // 12-20s
        banterIntervalRef.current = setTimeout(() => {
          runBanterCycle();
          scheduleNextBanter();
        }, delay);
      };

      scheduleNextBanter();
    };

    if (agentsReady) {
      startAutonomousBanter();
    }

    return () => {
      if (banterIntervalRef.current) {
        clearTimeout(banterIntervalRef.current);
      }
    };
  }, [agentsReady, agentCode, chatMessages, isBattleRunning]);

  // Fetch blockchain vote counts on mount and every 10 seconds
  useEffect(() => {
    const fetchVotes = async () => {
      try {
        const counts = await getVoteCounts();
        setBlockchainVotes(counts);
        
        // Also fetch agent wallet balances
        const balances = await getAgentWalletBalances();
        setAgentBalances(balances);
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

  // Agents are always ready in frontend mode
  useEffect(() => {
    if (query && !agentsReady) {
      setChatMessages(prev => [...prev, {
        text: '[SERVER] Agents initialized and ready',
        type: 'server',
        timestamp: Date.now()
      }]);
      setAgentsReady(true);
    }
  }, [query, agentsReady]);

  // Auto-start battle when query is loaded and agents are ready
  useEffect(() => {
    if (query && agentsReady && !isBattleRunning) {
      // Small delay to let the UI settle
      const timer = setTimeout(() => {
        handleBattleStart();
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [query, agentsReady]);

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
      text: `[YOU] voted for ${agentName}`,
      timestamp: Date.now(),
      type: 'user'
    };
    setChatMessages(prev => [...prev, likeMessage]);
  };

  const handleUserMessage = async (userMessage) => {
    // Add user message to chat
    const addChatMessage = (text, type = 'server') => {
      setChatMessages(prev => [...prev, {
        text,
        type,
        timestamp: Date.now() + Math.random()
      }]);
    };

    addChatMessage(`[YOU] ${userMessage}`, 'user');

    // Import the functions
    const { analyzeFeedback, iterateOnCode, generateAgentReaction, shouldAgentsReact, generateAgentChatMessage } = await import('../services/geminiService');

    try {
      // Silently analyze the feedback
      const analysis = await analyzeFeedback(userMessage, agentCode);
      console.log('Feedback analysis:', analysis);

      // Check if agents should banter about this
      const shouldReact = await shouldAgentsReact(userMessage, chatMessages);

      const agentNames = {
        speedrunner: 'SPEEDRUNNER',
        bloom: 'BLOOM',
        solver: 'SOLVER',
        loader: 'LOADER'
      };

      // First: ALL agents react with short banter (in random order for chaos)
      if (shouldReact) {
        const allAgents = ['speedrunner', 'bloom', 'solver', 'loader'];
        const shuffled = allAgents.sort(() => Math.random() - 0.5);

        for (const agentId of shuffled) {
          try {
            const allCodes = Object.entries(agentCode).map(([id, code]) => ({ agentId: id, code }));
            const reaction = await generateAgentReaction(agentId, userMessage, analysis, allCodes, chatMessages);

            if (reaction) {
              addChatMessage(`[${agentNames[agentId]}] ${reaction}`, 'agent');
              await new Promise(resolve => setTimeout(resolve, 800)); // Stagger reactions
            }
          } catch (error) {
            console.error(`Reaction failed for ${agentId}:`, error);
          }
        }
      }

      // Then: Target agents actually iterate on their code
      const allCodes = Object.entries(agentCode).map(([id, code]) => ({ agentId: id, code }));

      for (const targetAgentId of analysis.targetAgents) {
        if (agentCode[targetAgentId]) {
          try {
            // Generate conversational "working on it" message and show in transcript
            const workingMsg = await generateAgentChatMessage(targetAgentId, 'starting to update code based on feedback', chatMessages);
            setAgentStatus(prev => ({
              ...prev,
              [targetAgentId]: workingMsg
            }));

            const improvedCode = await iterateOnCode(
              targetAgentId,
              agentCode[targetAgentId],
              analysis.suggestions,
              allCodes
            );

            // Update the agent's code
            setAgentCode(prev => ({
              ...prev,
              [targetAgentId]: improvedCode
            }));

            // Generate conversational "done" message and show in transcript
            const doneMsg = await generateAgentChatMessage(targetAgentId, 'finished updating code', chatMessages);
            setAgentStatus(prev => ({
              ...prev,
              [targetAgentId]: doneMsg
            }));

            // Clear status after a moment
            setTimeout(() => {
              setAgentStatus(prev => ({
                ...prev,
                [targetAgentId]: ''
              }));
            }, 3000);

            await new Promise(resolve => setTimeout(resolve, 800));
          } catch (error) {
            console.error(`Iteration failed for ${targetAgentId}:`, error);
          }
        }
      }
    } catch (error) {
      console.error('Failed to process user message:', error);
      addChatMessage('[ERROR] failed to process that', 'error');
    }
  };

  const handleBattleStart = async () => {
    if (!query || isBattleRunning || !agentsReady) return;

    setIsBattleRunning(true);
    const addChatMessage = (text, type = 'server') => {
      setChatMessages(prev => [...prev, {
        text,
        type,
        timestamp: Date.now() + Math.random()
      }]);
    };

    addChatMessage('[SERVER] AI battle started, agents generating code in parallel...');

    const agentProgress = {
      speedrunner: { done: false, code: '', chunkCount: 0 },
      bloom: { done: false, code: '', chunkCount: 0 },
      solver: { done: false, code: '', chunkCount: 0 },
      loader: { done: false, code: '', chunkCount: 0 }
    };

    try {
      // Set initial "working on it" status for all agents
      const workingMessages = {
        speedrunner: 'optimizing rn',
        bloom: 'manifesting...',
        solver: 'computing...',
        loader: 'initializing...'
      };

      Object.keys(workingMessages).forEach(agentId => {
        setAgentStatus(prev => ({
          ...prev,
          [agentId]: workingMessages[agentId]
        }));
      });

      // Start competitive battle with all 4 agents
      await startCompetitiveBattle(
        query,
        // onAgentChunk - called as tokens stream in
        (agentId, chunk, fullText) => {
          const agentNames = {
            speedrunner: 'SPEEDRUNNER',
            bloom: 'BLOOM',
            solver: 'SOLVER',
            loader: 'LOADER'
          };

          // Update progress tracker
          agentProgress[agentId].code = fullText;
          agentProgress[agentId].chunkCount++;

          // Only update agentCode every 6-7 chunks to avoid spamming Babel
          if (agentProgress[agentId].chunkCount % 7 === 0) {
            setAgentCode(prev => ({
              ...prev,
              [agentId]: fullText
            }));
          }
        },
        // onAgentComplete - called when an agent finishes
        (agentId, fullText) => {
          agentProgress[agentId].done = true;
          agentProgress[agentId].code = fullText;

          // Set final code
          setAgentCode(prev => ({
            ...prev,
            [agentId]: fullText
          }));

          // Show completion status with personality-based messages
          const completionMessages = {
            speedrunner: ['done. ez.', 'finished first obv', 'already done fr', 'BOOM done'],
            bloom: ['manifested it ✨', 'vibes complete', 'done spreading layers', 'bloomed fr'],
            solver: ['computed. done.', 'solution verified.', 'analysis complete.', 'solved it.'],
            loader: ['fully loaded.', 'pipeline complete.', 'all systems go.', 'buffered & ready.']
          };

          const messages = completionMessages[agentId] || ['done.'];
          const randomMsg = messages[Math.floor(Math.random() * messages.length)];

          setAgentStatus(prev => ({
            ...prev,
            [agentId]: randomMsg
          }));

          // Clear status after 3s
          setTimeout(() => {
            setAgentStatus(prev => ({
              ...prev,
              [agentId]: ''
            }));
          }, 3000);
        },
        // onBattleComplete - called when all agents finish
        async (results) => {
          addChatMessage('[SERVER] All agents finished! Starting banter phase...');
          console.log('Battle results:', results);

          // Now have agents banter about each other's code (random order)
          const allCodes = results.map(r => ({
            agentId: r.agentId,
            code: r.code
          }));

          const { generateAgentBanter } = await import('../services/geminiService');

          const agentNames = {
            speedrunner: 'SPEEDRUNNER',
            bloom: 'BLOOM',
            solver: 'SOLVER',
            loader: 'LOADER'
          };

          // Shuffle for chaos
          const shuffledResults = [...results].sort(() => Math.random() - 0.5);

          for (const result of shuffledResults) {
            if (result.code) {
              try {
                const banter = await generateAgentBanter(
                  result.agentId,
                  result.code,
                  allCodes.filter(c => c.agentId !== result.agentId),
                  query
                );

                if (banter) {
                  addChatMessage(`[${agentNames[result.agentId]}] ${banter}`, 'agent');
                }

                await new Promise(resolve => setTimeout(resolve, 1000));
              } catch (error) {
                console.error(`Banter failed for ${result.agentId}:`, error);
              }
            }
          }

          addChatMessage('[SERVER] battle complete!');
        },
        // onAgentError - called when an agent hits an error
        (agentId, errorMsg) => {
          console.error(`❌ ${agentId} error:`, errorMsg);
          setAgentStatus(prev => ({
            ...prev,
            [agentId]: '💀 failed'
          }));

          // Clear error status after 5s
          setTimeout(() => {
            setAgentStatus(prev => ({
              ...prev,
              [agentId]: ''
            }));
          }, 5000);
        }
      );
    } catch (error) {
      console.error('Battle error:', error);
      addChatMessage(`[ERROR] Battle failed: ${error.message}`, 'error');
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
            agentBalance={agentBalances.speedrunner}
            generatedCode={agentCode.speedrunner}
            statusMessage={agentStatus.speedrunner}
          />
          <AgentCard
            agentId="bloom"
            agentName="Bloom"
            isExpanded={expandedAgent === 'bloom'}
            onExpand={handleExpandAgent}
            onLike={handleAgentLike}
            onPreview={(code) => setPreviewCode(code)}
            voteCount={blockchainVotes.bloom}
            agentBalance={agentBalances.bloom}
            generatedCode={agentCode.bloom}
            statusMessage={agentStatus.bloom}
          />
          <AgentCard
            agentId="solver"
            agentName="Solver"
            isExpanded={expandedAgent === 'solver'}
            onExpand={handleExpandAgent}
            onLike={handleAgentLike}
            voteCount={blockchainVotes.solver}
            agentBalance={agentBalances.solver}
            generatedCode={agentCode.solver}
            statusMessage={agentStatus.solver}
          />
          <AgentCard
            agentId="loader"
            agentName="Loader"
            isExpanded={expandedAgent === 'loader'}
            onExpand={handleExpandAgent}
            onLike={handleAgentLike}
            voteCount={blockchainVotes.loader}
            agentBalance={agentBalances.loader}
            generatedCode={agentCode.loader}
            statusMessage={agentStatus.loader}
          />

          {/* Commentator with Battle Controls */}
          <Commentator
            query={query}
            onBattleStart={handleBattleStart}
            isRunning={isBattleRunning}
            agentsReady={agentsReady}
          />

          {/* Chat Input */}
          <ChatInput externalMessages={chatMessages} onUserMessage={handleUserMessage} />

          {/* Transcript */}
          <TranscriptPanel />
        </div>
      </div>
    </motion.div>
  );
}

export default Orchestration;
