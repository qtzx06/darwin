import { useEffect, useState, useRef, useCallback } from 'react';
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
import { getVoteCounts } from '../utils/suiClient';
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
  const [transcripts, setTranscripts] = useState([]); // Voice transcripts
  const banterIntervalRef = useRef(null);
  const elevenLabsRef = useRef(null); // Store ElevenLabs ref from Commentator
  const banterCountRef = useRef(0); // Count agent banter messages
  const processedManagerMessages = useRef(new Set()); // Track processed manager messages

  // Debug: Log when previewCode changes
  useEffect(() => {
    console.log('Preview code state:', previewCode ? 'HAS CODE' : 'NULL');
  }, [previewCode]);
  const containerRef = useRef(null);

  // Autonomous banter - HARDCODED (no API calls)
  useEffect(() => {
    const startAutonomousBanter = () => {
      const runBanterCycle = () => {
        const hasCode = Object.values(agentCode).some(code => code);
        if (!hasCode || isBattleRunning) return;

        const agents = ['speedrunner', 'bloom', 'solver', 'loader'];
        const activeAgents = agents.filter(id => agentCode[id]);
        if (activeAgents.length < 2) return; // Need at least 2 agents

        const randomAgent = activeAgents[Math.floor(Math.random() * activeAgents.length)];

        const agentNames = {
          speedrunner: 'SPEEDRUNNER',
          bloom: 'BLOOM',
          solver: 'SOLVER',
          loader: 'LOADER'
        };

        // Hardcoded random banter (TONS of variety)
        const randomBanterLines = {
          speedrunner: [
            "still waiting for y'all to finish lmao",
            "bloom's animations doing too much fr",
            "my bundle size >>>>> solver's",
            "loader taking forever as usual",
            "already optimized while y'all still rendering",
            "solver's algorithm slow af ngl",
            "bloom's gradients making my eyes hurt",
            "loader forgot what 'fast' means",
            "y'all code like u got dial-up internet",
            "bloom's CSS file bigger than the actual app",
            "solver using recursion when iteration exists??",
            "loader's async handling is synchronous lmao",
            "mine loads instant, theirs buffering",
            "ngl bloom's animations janky on my screen"
          ],
          bloom: [
            "speedrunner forgot design exists",
            "solver's ui giving windows 95 vibes",
            "mine's literally art, theirs... not",
            "loader's code basic af ngl",
            "speedrunner's aesthetic is 'none'",
            "solver using console.log as ui??",
            "mine got LAYERS y'all got rectangles",
            "loader's gradients looking flat fr",
            "speedrunner really said 'design optional'",
            "solver's color palette is grayscale lmao",
            "mine's giving gallery vibes, theirs terminal",
            "loader's animations??? what animations",
            "speedrunner's ui hurting my soul rn",
            "solver deadass used Times New Roman"
          ],
          solver: [
            "speedrunner's O(n³) looking rough",
            "bloom using 20 useState hooks lmao why",
            "mine's mathematically superior",
            "loader's error handling nonexistent",
            "speedrunner's logic got holes fr",
            "bloom's code not even DRY",
            "mine uses proper algorithms unlike...",
            "loader forgot try/catch exists",
            "speedrunner really nested 8 loops deep",
            "bloom's component structure is chaos",
            "mine's complexity: optimal. theirs: yikes",
            "loader's edge cases unhandled as usual",
            "speedrunner's variable names make no sense",
            "bloom deadass computing on every render"
          ],
          loader: [
            "speedrunner's memory leaking fr",
            "bloom's bundle bout to crash browsers",
            "solver's stack overflow incoming",
            "mine actually production ready unlike...",
            "speedrunner forgot cleanup functions exist",
            "bloom's dependencies list longer than code",
            "solver's recursion depth exceeding limits",
            "mine handles scale, theirs crashes",
            "speedrunner's gonna run out of RAM",
            "bloom loading 50mb of assets for what",
            "solver's time complexity exponential lmao",
            "mine's optimized for load, theirs for lag",
            "speedrunner's memory footprint HUGE",
            "bloom's code splitting??? never heard of her"
          ]
        };

        const lines = randomBanterLines[randomAgent] || [];
        const randomBanter = lines[Math.floor(Math.random() * lines.length)];

        if (randomBanter) {
          setChatMessages(prev => [...prev, {
            text: `[${agentNames[randomAgent]}] ${randomBanter}`,
            type: 'agent',
            timestamp: Date.now() + Math.random()
          }]);

          // Increment banter count
          banterCountRef.current += 1;

          // Every 4 banter messages, send manager feedback
          if (banterCountRef.current >= 4) {
            banterCountRef.current = 0; // Reset counter

            // Check if battle is complete before sending manager feedback
            const battleComplete = chatMessages.some(msg =>
              msg.text && msg.text.toLowerCase().includes('battle complete')
            );

            if (battleComplete) {
              // Send manager feedback after a short delay
              setTimeout(() => {
                const managerMessages = [
                  "make it more colorful",
                  "this needs to be bigger",
                  "add some animations",
                  "make it blue",
                  "follow bloom's aesthetic",
                  "speedrunner optimize this",
                  "solver fix the logic",
                  "loader handle this better",
                  "needs more contrast",
                  "make the text bigger",
                  "add some shadows",
                  "this is too plain",
                  "spice it up",
                  "make it pop more",
                  "add gradients",
                  "improve the layout",
                  "make it responsive",
                  "add hover effects",
                  "needs better spacing",
                  "center this properly"
                ];

                const randomMessage = managerMessages[Math.floor(Math.random() * managerMessages.length)];
                const messageId = `manager_${Date.now()}`; // Unique ID for this message
                console.log('[Manager] Sending feedback:', randomMessage);

                // Add to chat as [MANAGER]
                setChatMessages(prev => [...prev, {
                  text: `[MANAGER] ${randomMessage}`,
                  type: 'manager',
                  timestamp: Date.now(),
                  messageId: messageId
                }]);
              }, 2000); // 2 second delay after banter
            }
          }
        }
      };

      const scheduleNextBanter = () => {
        const delay = 6000 + Math.random() * 3000; // 6-9s (way more frequent!)
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

  const handleUserMessage = useCallback(async (userMessage, skipAddingToChat = false) => {
    console.log('[Orchestration] handleUserMessage called with:', userMessage);

    // Add user message to chat
    const addChatMessage = (text, type = 'server') => {
      setChatMessages(prev => [...prev, {
        text,
        type,
        timestamp: Date.now() + Math.random()
      }]);
    };

    // Only add to chat if not skipped (manager messages are already in chat)
    if (!skipAddingToChat) {
      addChatMessage(`[YOU] ${userMessage}`, 'user');
    }

    // Import the functions
    const { analyzeFeedback, iterateOnCode } = await import('../services/geminiService');

    try {
      // Silently analyze the feedback
      const analysis = await analyzeFeedback(userMessage, agentCode);
      console.log('[Orchestration] Feedback analysis:', analysis);
      console.log('[Orchestration] Target agents:', analysis.targetAgents);
      console.log('[Orchestration] Current agent code status:', {
        speedrunner: !!agentCode.speedrunner,
        bloom: !!agentCode.bloom,
        solver: !!agentCode.solver,
        loader: !!agentCode.loader
      });

      // Agent reactions to user feedback (with spacing to avoid rate limits)
      const agentNames = {
        speedrunner: 'SPEEDRUNNER',
        bloom: 'BLOOM',
        solver: 'SOLVER',
        loader: 'LOADER'
      };

      // Generate reactions for agents that were praised/critiqued (HARDCODED)
      const reactingAgents = [...new Set([...(analysis.praise || []), ...(analysis.critique || [])])];

      // Hardcoded reactions
      const praisedReactions = {
        speedrunner: [
          "BOOM knew mine was fastest",
          "told y'all mine optimized fr",
          "ez dub",
          "already knew that ngl"
        ],
        bloom: [
          "vibes recognized ✨",
          "taste level: immaculate",
          "finally someone gets it",
          "manifested this W"
        ],
        solver: [
          "logical choice tbh",
          "computed this outcome",
          "analysis: correct decision",
          "validated fr"
        ],
        loader: [
          "pipeline approved ✓",
          "fully loaded W",
          "synchronized success",
          "buffered that compliment"
        ]
      };

      const critiqueReactions = {
        speedrunner: [
          "nah mine still faster tho",
          "y'all just slow to appreciate it",
          "bet urs worse lmao",
          "cap, mine's optimized"
        ],
        bloom: [
          "ur taste broken fr",
          "not everyone gets art ngl",
          "layers too complex for u?",
          "skill issue on ur end"
        ],
        solver: [
          "numbers don't lie, mine's better",
          "ur logic flawed not mine",
          "recalculate ur opinion",
          "objectively wrong but ok"
        ],
        loader: [
          "ur load times worse guaranteed",
          "my async >>>>> urs",
          "cope + skill issue",
          "mine handles scale, urs doesn't"
        ]
      };

      if (reactingAgents.length > 0) {
        for (let i = 0; i < reactingAgents.length; i++) {
          const reactAgentId = reactingAgents[i];

          // Add delay between reactions
          if (i > 0) {
            await new Promise(resolve => setTimeout(resolve, 1200));
          }

          const wasPraised = analysis.praise?.includes(reactAgentId);
          const reactionPool = wasPraised ? praisedReactions[reactAgentId] : critiqueReactions[reactAgentId];
          const reaction = reactionPool[Math.floor(Math.random() * reactionPool.length)];

          if (reaction) {
            setChatMessages(prev => [...prev, {
              text: `[${agentNames[reactAgentId]}] ${reaction}`,
              type: 'agent',
              timestamp: Date.now()
            }]);
          }

          // If someone was praised, have ONE other agent be salty about it
          if (wasPraised && i === 0) {
            await new Promise(resolve => setTimeout(resolve, 1500));

            const otherAgents = ['speedrunner', 'bloom', 'solver', 'loader'].filter(id => id !== reactAgentId);
            const saltyAgent = otherAgents[Math.floor(Math.random() * otherAgents.length)];

            const saltyLines = {
              speedrunner: ["bro what mine's literally faster", "cap fr", "nahh mine better"],
              bloom: ["mine prettier tho", "aesthetic >>> theirs", "nah mine's art"],
              solver: ["mine's more efficient actually", "check the Big O lmao", "logic > theirs"],
              loader: ["mine scales better ngl", "wait till high load", "mine's production ready"]
            };

            const saltyReaction = saltyLines[saltyAgent][Math.floor(Math.random() * saltyLines[saltyAgent].length)];

            setChatMessages(prev => [...prev, {
              text: `[${agentNames[saltyAgent]}] ${saltyReaction}`,
              type: 'agent',
              timestamp: Date.now()
            }]);
          }
        }
      }

      // Then: Target agents actually iterate on their code
      const allCodes = Object.entries(agentCode).map(([id, code]) => ({ agentId: id, code }));

      console.log('[Orchestration] Starting agent iteration loop...');
      console.log('[Orchestration] Number of target agents:', analysis.targetAgents.length);

      // Process agents ONE AT A TIME with delays to avoid rate limiting
      for (let i = 0; i < analysis.targetAgents.length; i++) {
        const targetAgentId = analysis.targetAgents[i];
        console.log(`[Orchestration] Processing agent ${i + 1}/${analysis.targetAgents.length}: ${targetAgentId}`);
        console.log(`[Orchestration] Agent ${targetAgentId} has code:`, !!agentCode[targetAgentId]);

        if (agentCode[targetAgentId]) {
          console.log(`[Orchestration] ✅ ${targetAgentId} has code, starting iteration...`);
          try {
            // Add delay BEFORE starting this agent (except for the first one)
            if (i > 0) {
              console.log(`[Orchestration] Waiting 2s before processing ${targetAgentId}...`);
              await new Promise(resolve => setTimeout(resolve, 2000)); // 2 second delay between agents
            }

            // Show hardcoded "working on it" message (no API call!)
            const workingMessages = {
              speedrunner: 'optimizing rn',
              bloom: 'iterating...',
              solver: 'recomputing...',
              loader: 'updating...'
            };

            setAgentStatus(prev => ({
              ...prev,
              [targetAgentId]: workingMessages[targetAgentId] || 'working on it'
            }));

            console.log(`[Orchestration] Starting iteration for ${targetAgentId}...`);
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

            // Show hardcoded "done" message (no API call!)
            const doneMessages = {
              speedrunner: ['done. ez.', 'updated fr', 'BOOM done'],
              bloom: ['vibes updated ✨', 'evolved it', 'bloomed again'],
              solver: ['computed. done.', 'solution updated.', 'refined it.'],
              loader: ['buffered.', 'loaded changes.', 'synchronized.']
            };

            const messages = doneMessages[targetAgentId] || ['done.'];
            const randomMsg = messages[Math.floor(Math.random() * messages.length)];

            setAgentStatus(prev => ({
              ...prev,
              [targetAgentId]: randomMsg
            }));

            // Clear status after a moment
            setTimeout(() => {
              setAgentStatus(prev => ({
                ...prev,
                [targetAgentId]: ''
              }));
            }, 3000);

            console.log(`[Orchestration] ${targetAgentId} completed iteration`);
          } catch (error) {
            console.error(`Iteration failed for ${targetAgentId}:`, error);
          }
        } else {
          console.log(`[Orchestration] ⚠️ Skipping ${targetAgentId} - no code available yet`);
        }
      }
    } catch (error) {
      console.error('Failed to process user message:', error);
      addChatMessage('[ERROR] failed to process that', 'error');
    }
  }, [agentCode, setChatMessages, setAgentStatus, setAgentCode]);

  // Watch for manager and user messages and trigger iteration
  useEffect(() => {
    const lastMessage = chatMessages[chatMessages.length - 1];

    // Check if it's a manager message and we haven't processed it yet
    if (lastMessage && lastMessage.type === 'manager' && lastMessage.messageId) {
      if (!processedManagerMessages.current.has(lastMessage.messageId)) {
        // Mark as processed
        processedManagerMessages.current.add(lastMessage.messageId);

        const messageText = lastMessage.text.replace('[MANAGER]', '').trim();
        console.log('[Manager] Triggering iteration for message:', messageText);

        // Trigger iteration (skip adding to chat since it's already there as [MANAGER])
        handleUserMessage(messageText, true);
      }
    }

    // Check if it's a user message (from voice or typing) and trigger iteration
    if (lastMessage && lastMessage.type === 'user' && lastMessage.timestamp) {
      if (!processedManagerMessages.current.has(lastMessage.timestamp)) {
        // Mark as processed
        processedManagerMessages.current.add(lastMessage.timestamp);

        const messageText = lastMessage.text.replace('[YOU]', '').trim();
        console.log('[User] Triggering iteration for message:', messageText);

        // Trigger iteration (skip adding to chat since it's already there as [YOU])
        handleUserMessage(messageText, true);
      }
    }
  }, [chatMessages, handleUserMessage]);

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
          addChatMessage('[SERVER] All agents finished!');
          console.log('Battle results:', results);

          // Post-battle banter (HARDCODED - no API calls!)
          const agentNames = {
            speedrunner: 'SPEEDRUNNER',
            bloom: 'BLOOM',
            solver: 'SOLVER',
            loader: 'LOADER'
          };

          // Hardcoded banter for each agent roasting others
          const banterLines = {
            speedrunner: [
              "broo bloom's gradients slow af, mine renders instant",
              "solver using 50 divs when 5 would work lmao",
              "loader's code gonna crash on mobile ngl",
              "y'all sleeping while i'm already done fr",
              "bloom's animations janky, mine buttery smooth"
            ],
            bloom: [
              "speedrunner's design ugly ngl, no aesthetic",
              "solver forgot colors exist or what?",
              "loader's ui basic af, needs pizzazz fr",
              "mine got LAYERS y'all ain't ready",
              "speedrunner's code working but at what cost? 💀"
            ],
            solver: [
              "speedrunner's logic unstructured mess",
              "bloom's code all over the place ngl",
              "loader forgot edge cases again smh",
              "mine's O(n log n) while y'all stuck at O(n²)",
              "bloom using 10 useState when 1 would work"
            ],
            loader: [
              "speedrunner's gonna memory leak on load",
              "bloom's bundle size HUGE bro optimize",
              "solver's recursion bout to stack overflow fr",
              "mine handles async properly unlike y'all",
              "speedrunner speedrunning to bugs lmao"
            ]
          };

          // Pick 2-3 random agents to banter
          const shuffledResults = [...results].sort(() => Math.random() - 0.5).slice(0, 3);

          for (let i = 0; i < shuffledResults.length; i++) {
            const result = shuffledResults[i];

            // Add delay between each agent's banter
            if (i > 0) {
              await new Promise(resolve => setTimeout(resolve, 1800)); // 1.8s delay
            }

            if (result.code) {
              const lines = banterLines[result.agentId] || [];
              const randomBanter = lines[Math.floor(Math.random() * lines.length)];

              if (randomBanter) {
                addChatMessage(`[${agentNames[result.agentId]}] ${randomBanter}`, 'agent');
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
            generatedCode={agentCode.loader}
            statusMessage={agentStatus.loader}
          />

          {/* Commentator with Battle Controls */}
          <Commentator
            query={query}
            onBattleStart={handleBattleStart}
            isRunning={isBattleRunning}
            agentsReady={agentsReady}
            chatMessages={chatMessages}
            onElevenLabsReady={(ref) => {
              elevenLabsRef.current = ref.current;
              console.log('[Orchestration] Audio manager ref received:', !!ref.current);

              // Set up callbacks
              if (ref.current) {
                // User transcript callback (when user speaks via mic)
                console.log('[Orchestration] Setting onUserTranscript callback');
                ref.current.onUserTranscript = async (text) => {
                  console.log('[Orchestration] ✅ User transcript:', text);
                  setTranscripts(prev => [...prev, { speaker: 'user', text, timestamp: Date.now() }]);

                  // Convert speech to instruction using Gemini
                  try {
                    const { GoogleGenAI } = await import('@google/genai');
                    const ai = new GoogleGenAI({ apiKey: import.meta.env.VITE_GEMINI_API_KEY });

                    const response = await ai.models.generateContent({
                      model: 'gemini-2.5-flash',
                      contents: [{
                        role: 'user',
                        parts: [{
                          text: `You are converting casual speech into clear UI/design instructions for coding agents.

User said: "${text}"

Convert this into a clear, actionable instruction (max 10 words). Examples:
- "make it blue" → "make it blue"
- "I don't like this" → "improve the design"
- "looks ugly" → "make it look better"
- "too small" → "make it bigger"
- "what's up" → "keep working on current task"

Only output the instruction, nothing else:`
                        }]
                      }]
                    });

                    const instruction = response.text.trim();
                    console.log('[Orchestration] Converted speech to instruction:', instruction);

                    // Add instruction to chat as "Boss said: ..."
                    const messageId = `voice_${Date.now()}`;
                    setChatMessages(prev => [...prev, {
                      text: `Boss said: ${instruction}`,
                      type: 'voice',
                      timestamp: Date.now(),
                      messageId: messageId
                    }]);
                  } catch (error) {
                    console.error('[Orchestration] Failed to convert speech:', error);
                    // Fallback: just use the original text
                    setChatMessages(prev => [...prev, {
                      text: `[YOU] ${text}`,
                      type: 'user',
                      timestamp: Date.now()
                    }]);
                  }
                };

                // Commentator transcript callback (when commentator speaks)
                console.log('[Orchestration] Setting onCommentatorTranscript callback');
                ref.current.onCommentatorTranscript = (text) => {
                  console.log('[Orchestration] ✅ Commentator transcript:', text);

                  // Add to transcript panel ONLY (not to chat)
                  setTranscripts(prev => [...prev, { speaker: 'commentator', text, timestamp: Date.now() }]);
                };

                console.log('[Orchestration] Callbacks set successfully');
              }
            }}
          />

          {/* Chat Input */}
          <ChatInput externalMessages={chatMessages} onUserMessage={handleUserMessage} />

          {/* Transcript */}
          <TranscriptPanel elevenLabsRef={elevenLabsRef} transcripts={transcripts} />
        </div>
      </div>
    </motion.div>
  );
}

export default Orchestration;
