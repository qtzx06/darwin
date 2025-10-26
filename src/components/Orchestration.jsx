import { useState, useEffect, useRef } from 'react';
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
import { competitiveApi, livekitApi, apiUtils } from '../services/api';

function Orchestration() {
  const [query, setQuery] = useState('');
  const [projectId, setProjectId] = useState(null);
  const [subtasks, setSubtasks] = useState([]);
  const [currentSubtask, setCurrentSubtask] = useState(null);
  const [agentResults, setAgentResults] = useState([]);
  const [winner, setWinner] = useState(null);
  const [projectStatus, setProjectStatus] = useState(null);
  const [expandedAgent, setExpandedAgent] = useState(null);
  const [showFadeOverlay, setShowFadeOverlay] = useState(true);
  const [chatMessages, setChatMessages] = useState([]);
  const [transcriptMessages, setTranscriptMessages] = useState([]);
  const [roomName, setRoomName] = useState(null);
  const [isWorkflowRunning, setIsWorkflowRunning] = useState(false);
  const [workflowStarted, setWorkflowStarted] = useState(false);
  const [currentAudio, setCurrentAudio] = useState(null);
  const [agentData, setAgentData] = useState({
    speedrunner: { code: '', isWorking: false, wins: 0 },
    bloom: { code: '', isWorking: false, wins: 0 },
    solver: { code: '', isWorking: false, wins: 0 },
    loader: { code: '', isWorking: false, wins: 0 }
  });
  const [commentary, setCommentary] = useState('');
  const [waitingForWinner, setWaitingForWinner] = useState(false);
  const [selectedWinner, setSelectedWinner] = useState(null);
  const [winnerReason, setWinnerReason] = useState('');
  const [currentRoundResults, setCurrentRoundResults] = useState(null);
  const containerRef = useRef(null);
  const winnerResolveRef = useRef(null);

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
    // Extract query and projectId from URL hash
    const hash = window.location.hash;
    const params = new URLSearchParams(hash.split('?')[1]);
    const q = params.get('q');
    const pid = params.get('projectId');
    if (q) {
      setQuery(decodeURIComponent(q));
    }
    if (pid) {
      setProjectId(pid);
    }
  }, []);

  useEffect(() => {
    if (!projectId) return;

    const createRoom = async () => {
      try {
        const response = await livekitApi.createBattleRoom(projectId);
        setRoomName(response.room_name);
      } catch (error) {
        console.error('Error creating battle room:', error);
      }
    };

    createRoom();
  }, [projectId]);

  // Audio context for orb visualization
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const audioSourceRef = useRef(null);
  
  // Initialize audio context once
  useEffect(() => {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    audioContextRef.current = audioContext;
    
    const analyser = audioContext.createAnalyser();
    analyser.fftSize = 512;
    analyserRef.current = analyser;
    
    console.log('🎙️ Audio context initialized for orb visualization');
    
    return () => {
      audioContext.close();
    };
  }, []);

  // Simple audio playback function with orb reactivity
  const playCommentatorAudio = async (text, voiceId = 'gnPxliFHTp6OK6tcoA6i') => {
    try {
      console.log('🎤 Playing commentator audio:', text);
      
      const response = await fetch('http://localhost:5003/api/livekit/speak-text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, voice_id: voiceId })
      });

      if (response.ok) {
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        
        // Connect audio to analyser for orb visualization
        if (audioContextRef.current && analyserRef.current) {
          try {
            // Disconnect previous source if exists
            if (audioSourceRef.current) {
              audioSourceRef.current.disconnect();
            }
            
            const source = audioContextRef.current.createMediaElementSource(audio);
            source.connect(analyserRef.current);
            analyserRef.current.connect(audioContextRef.current.destination);
            audioSourceRef.current = source;
            console.log('✅ Audio connected to orb visualizer');
          } catch (err) {
            // If MediaElementSource already exists, just play the audio
            console.log('⚠️ Using existing audio connection');
          }
        }
        
        setCurrentAudio(audio);
        
        audio.onended = () => {
          URL.revokeObjectURL(audioUrl);
          setCurrentAudio(null);
          console.log('✅ Audio finished playing');
        };
        
        await audio.play();
        console.log('🔊 Audio is playing and orb should react!');
      } else {
        console.error('❌ TTS API error:', response.status);
      }
    } catch (error) {
      console.error('❌ Error playing audio:', error);
    }
  };

  // Only orchestrate (get subtasks) automatically - don't run the workflow yet
  useEffect(() => {
    if (!projectId || !query || subtasks.length > 0) return;

    const orchestrateOnly = async () => {
      try {
        console.log('🎯 Orchestrating project:', query);
        const orchestrationResult = await competitiveApi.orchestrateProject(query);
        setSubtasks(orchestrationResult.subtasks);
        console.log('✅ Subtasks created:', orchestrationResult.subtasks);
      } catch (error) {
        console.error('❌ Error orchestrating project:', error);
      }
    };

    orchestrateOnly();
  }, [projectId, query, subtasks.length]);

  // Manual workflow execution - triggered by button click
  const startBattle = async () => {
    if (!projectId || !subtasks.length || isWorkflowRunning) return;

    setIsWorkflowRunning(true);
    setWorkflowStarted(true);

    try {
      console.log('🔥 Starting battle with', subtasks.length, 'subtasks');

      // Run competitive rounds for each subtask
      for (const subtask of subtasks) {
        setCurrentSubtask(subtask);
        // STEP 1: Get pre-battle trash talk from agents (before work starts!)
        try {
          const reactions = await livekitApi.getAgentReaction(
            roomName,
            'round_start',
            {
              agent_stats: { /* simplified for now */ },
              total_rounds: subtasks.length,
              current_round: subtask.id
            }
          );
          
          // Add trash talk to chat immediately
          if (reactions.agent_responses) {
            reactions.agent_responses.forEach(reaction => {
              const chatMessage = {
                text: reaction.response_text,
                speaker: reaction.agent_name,
                timestamp: Date.now(),
                emotion: reaction.emotion_level
              };
              setChatMessages(prev => [...prev, chatMessage]);
            });
          }
        } catch (err) {
          console.error('Could not get pre-battle reactions:', err);
        }

        // STEP 2: Get LLM-generated commentary (intro to the round) + trigger voice
        try {
          const commentaryResult = await competitiveApi.getCommentary(projectId, subtask.id);
          const commentaryText = commentaryResult.commentary || 'Battle is heating up!';
          setCommentary(commentaryText);
          
          // Trigger LiveKit voice commentary
          if (roomName) {
            try {
              // Get commentary from Letta
              console.log('📝 Getting commentary from Letta:', commentaryText);
              const commentatorResponse = await livekitApi.askCommentator(roomName, commentaryText);
              
              // Use the actual response text
              const spokenText = commentatorResponse.response_text || commentaryText;
              console.log('🗣️ Commentator will say:', spokenText);
              
              // Add to transcript
              const transcriptMessage = {
                text: spokenText,
                speaker: 'Commentator',
                timestamp: Date.now()
              };
              setTranscriptMessages(prev => [...prev, transcriptMessage]);
              
              // Play audio (same as simple_frontend.html)
              await playCommentatorAudio(spokenText);
              
            } catch (audioErr) {
              console.error('Could not get commentary:', audioErr);
              // Fallback: add original text to transcript
              const transcriptMessage = {
                text: commentaryText,
                speaker: 'Commentator',
                timestamp: Date.now()
              };
              setTranscriptMessages(prev => [...prev, transcriptMessage]);
            }
          } else {
            // No room, just add original commentary to transcript
            const transcriptMessage = {
              text: commentaryText,
              speaker: 'Commentator',
              timestamp: Date.now()
            };
            setTranscriptMessages(prev => [...prev, transcriptMessage]);
          }
        } catch (err) {
          console.error('Could not get commentary:', err);
        }

        // STEP 3: NOW start the actual work
        
        // Mark all agents as working
        setAgentData(prev => ({
          speedrunner: { ...prev.speedrunner, isWorking: true },
          bloom: { ...prev.bloom, isWorking: true },
          solver: { ...prev.solver, isWorking: true },
          loader: { ...prev.loader, isWorking: true }
        }));

        await competitiveApi.startWork(projectId, subtask.id);

        // Get results (agents do their work)
        const results = await competitiveApi.getResults(projectId);
        setAgentResults(results.agents);
        
        // Mark agents as done working
        ['speedrunner', 'bloom', 'solver', 'loader'].forEach(agentId => {
          setAgentData(prev => ({
            ...prev,
            [agentId]: {
              ...prev[agentId],
              isWorking: false
            }
          }));
        });

        // STEP 4: After work is done, fetch code and get post-battle reactions in parallel
        await Promise.all([
          // Fetch code for all agents
          (async () => {
            for (const agentId of ['speedrunner', 'bloom', 'solver', 'loader']) {
              await fetchAgentCode(agentId);
            }
          })(),

          // Get post-battle reactions
          (async () => {
            try {
              const postReactions = await livekitApi.getAgentReaction(
                roomName,
                'code_submitted',
                {
                  agent_stats: { /* simplified for now */ },
                  total_rounds: subtasks.length
                }
              );
              
              // Add post-battle reactions to chat
              if (postReactions.agent_responses) {
                postReactions.agent_responses.forEach(reaction => {
                  const chatMessage = {
                    text: reaction.response_text,
                    speaker: reaction.agent_name,
                    timestamp: Date.now(),
                    emotion: reaction.emotion_level
                  };
                  setChatMessages(prev => [...prev, chatMessage]);
                });
              }
            } catch (err) {
              console.error('Could not get post-battle reactions:', err);
            }
          })()
        ]);

        // Store results and wait for user to select winner
        setCurrentRoundResults(results);
        setWaitingForWinner(true);

        // Wait for user selection using promise
        await new Promise((resolve) => {
          winnerResolveRef.current = resolve;
        });
      }

      // Get final project status
      const status = await competitiveApi.getProjectStatus(projectId);
      setProjectStatus(status);
      console.log('🎉 Project complete:', status);

    } catch (error) {
      console.error('❌ Error running competitive workflow:', error);
    } finally {
      setIsWorkflowRunning(false);
    }
  };

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

  const handleAgentLike = (agentName) => {
    const likeMessage = {
      text: `user liked ${agentName}'s work`,
      timestamp: Date.now()
    };
    setChatMessages(prev => [...prev, likeMessage]);
  };

  const handleUserQuestion = async (question) => {
    if (!roomName || !question) return;
    
    try {
      console.log('🗣️ User asked:', question);
      
      // Add user question to transcript immediately
      const userMessage = {
        text: question,
        speaker: 'You',
        timestamp: Date.now()
      };
      setTranscriptMessages(prev => [...prev, userMessage]);
      
      // Get commentator's response
      const response = await livekitApi.askCommentator(roomName, question);
      const answerText = response.response_text || response.message;
      
      console.log('🎙️ Commentator responds:', answerText);
      
      // Add commentator response to transcript
      const commentatorMessage = {
        text: answerText,
        speaker: 'Commentator',
        timestamp: Date.now()
      };
      setTranscriptMessages(prev => [...prev, commentatorMessage]);
      
      // Play audio response
      await playCommentatorAudio(answerText);
      
    } catch (error) {
      console.error('❌ Error asking commentator:', error);
      
      // Add error message to transcript
      const errorMessage = {
        text: 'Sorry, I couldn\'t process that question.',
        speaker: 'System',
        timestamp: Date.now()
      };
      setTranscriptMessages(prev => [...prev, errorMessage]);
    }
  };

  const fetchAgentCode = async (agentId) => {
    if (!projectId) return;
    
    try {
      const agentName = apiUtils.mapAgentIdToName(agentId);
      console.log(`📥 Fetching code for ${agentName}...`);
      
      const result = await competitiveApi.retrieveCode(projectId, agentName);
      console.log(`📦 API Response:`, result);
      
      if (result.success && result.code) {
        console.log(`📝 Code length: ${result.code.length} characters`);
        console.log(`📝 Code preview:`, result.code.substring(0, 100));
        
        setAgentData(prev => ({
          ...prev,
          [agentId]: {
            ...prev[agentId],
            code: result.code
          }
        }));
        console.log(`✅ Code retrieved and set for ${agentName}`);
      } else {
        console.warn(`⚠️ No code in response for ${agentName}`, result);
      }
    } catch (error) {
      console.error(`❌ Error fetching code for ${agentId}:`, error);
    }
  };

  const handleSelectWinner = (agentId) => {
    setSelectedWinner(agentId);
  };

  const handleConfirmWinner = async () => {
    if (!selectedWinner || !winnerReason.trim()) {
      alert('Please select a winner and provide a reason');
      return;
    }

    // Convert frontend ID to backend name
    const winnerName = apiUtils.mapAgentIdToName(selectedWinner);
    
    // Update winner's win count
    setAgentData(prev => ({
      ...prev,
      [selectedWinner]: {
        ...prev[selectedWinner],
        wins: prev[selectedWinner].wins + 1
      }
    }));

    // Store winner info for the workflow to continue
    setWinner(winnerName);
    setWaitingForWinner(false);
    
    // Continue the workflow
    await continueWorkflow(winnerName, winnerReason);
  };

  const continueWorkflow = async (winnerName, reason) => {
    try {
      await competitiveApi.selectWinner(projectId, winnerName, reason);
      console.log('🏆 Winner selected:', winnerName, 'Reason:', reason);

      // Complete the round
      const winnerCode = currentRoundResults.agents.find(a => a.agent_name === winnerName)?.code || 'dummy_code';
      await competitiveApi.completeRound(projectId, winnerName, winnerCode, currentSubtask.id);
      console.log('✅ Round completed for subtask:', currentSubtask.id);

      // Reset selection state
      setSelectedWinner(null);
      setWinnerReason('');
      setCurrentRoundResults(null);
      setWaitingForWinner(false);

      // Resolve the promise to continue workflow
      if (winnerResolveRef.current) {
        winnerResolveRef.current();
        winnerResolveRef.current = null;
      }

    } catch (error) {
      console.error('❌ Error completing round:', error);
      setWaitingForWinner(false);
      if (winnerResolveRef.current) {
        winnerResolveRef.current();
        winnerResolveRef.current = null;
      }
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

      {/* Winner Selection Modal */}
      {waitingForWinner && (
        <div className="winner-selection-modal">
          <div className="winner-modal-content">
            <h2 className="winner-modal-title">🏆 Select Round Winner</h2>
            <p className="winner-modal-subtitle">
              Review the agents' work and choose the best solution
            </p>

            <div className="winner-agents-grid">
              {['speedrunner', 'bloom', 'solver', 'loader'].map((agentId) => (
                <div
                  key={agentId}
                  className={`winner-agent-option ${selectedWinner === agentId ? 'selected' : ''}`}
                  onClick={() => handleSelectWinner(agentId)}
                >
                  <div className="winner-agent-name">
                    {agentId === 'speedrunner' && 'Speedrunner'}
                    {agentId === 'bloom' && 'Bloom'}
                    {agentId === 'solver' && 'Solver'}
                    {agentId === 'loader' && 'Loader'}
                  </div>
                  <div className="winner-agent-personality">
                    {agentId === 'speedrunner' && 'Fast & Competitive'}
                    {agentId === 'bloom' && 'Creative & Pattern-seeking'}
                    {agentId === 'solver' && 'Logical & Methodical'}
                    {agentId === 'loader' && 'Patient & Process-oriented'}
                  </div>
                  {selectedWinner === agentId && (
                    <div className="winner-checkmark">✓</div>
                  )}
                </div>
              ))}
            </div>

            <div className="winner-reason-section">
              <label className="winner-reason-label">
                Why did you choose this agent?
              </label>
              <textarea
                className="winner-reason-input"
                placeholder="e.g., Best code quality, most efficient solution, cleanest implementation..."
                value={winnerReason}
                onChange={(e) => setWinnerReason(e.target.value)}
                rows={3}
              />
            </div>

            <button
              className="winner-confirm-btn"
              onClick={handleConfirmWinner}
              disabled={!selectedWinner || !winnerReason.trim()}
            >
              Confirm Winner & Continue
            </button>
          </div>
        </div>
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
            
            {/* Start Battle Button */}
            {subtasks.length > 0 && !workflowStarted && (
              <div className="start-battle-container">
                <button 
                  className="start-battle-btn"
                  onClick={startBattle}
                  disabled={isWorkflowRunning}
                >
                  {isWorkflowRunning ? '⚔️ Battle in Progress...' : '🔥 Start Battle'}
                </button>
                
                <div className="subtasks-preview">
                  {subtasks.length} subtasks ready
                </div>
              </div>
            )}
            
            {/* Battle Status */}
            {workflowStarted && (
              <div className="battle-status">
                {isWorkflowRunning ? (
                  <span className="status-running">⚔️ Battle in progress...</span>
                ) : (
                  <span className="status-complete">✅ Battle complete!</span>
                )}
                {currentSubtask && (
                  <span className="current-task">
                    Current: {currentSubtask.title}
                  </span>
                )}
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
            code={agentData.speedrunner.code}
            isWorking={agentData.speedrunner.isWorking}
            wins={agentData.speedrunner.wins}
            onFetchCode={fetchAgentCode}
            projectId={projectId}
          />
          <AgentCard
            agentId="bloom"
            agentName="Bloom"
            isExpanded={expandedAgent === 'bloom'}
            onExpand={handleExpandAgent}
            onLike={handleAgentLike}
            code={agentData.bloom.code}
            isWorking={agentData.bloom.isWorking}
            wins={agentData.bloom.wins}
            onFetchCode={fetchAgentCode}
            projectId={projectId}
          />
          <AgentCard
            agentId="solver"
            agentName="Solver"
            isExpanded={expandedAgent === 'solver'}
            onExpand={handleExpandAgent}
            onLike={handleAgentLike}
            code={agentData.solver.code}
            isWorking={agentData.solver.isWorking}
            wins={agentData.solver.wins}
            onFetchCode={fetchAgentCode}
            projectId={projectId}
          />
          <AgentCard
            agentId="loader"
            agentName="Loader"
            isExpanded={expandedAgent === 'loader'}
            onExpand={handleExpandAgent}
            onLike={handleAgentLike}
            code={agentData.loader.code}
            isWorking={agentData.loader.isWorking}
            wins={agentData.loader.wins}
            onFetchCode={fetchAgentCode}
            projectId={projectId}
          />

          {/* Commentator */}
          <Commentator analyser={analyserRef.current} />

          {/* Chat Input */}
          <ChatInput externalMessages={chatMessages} />

          {/* Transcript */}
          <TranscriptPanel 
            roomName={roomName} 
            messages={transcriptMessages}
            onUserQuestion={handleUserQuestion}
          />
        </div>
      </div>
    </motion.div>
  );
}

export default Orchestration;