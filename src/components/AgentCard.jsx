import { useRef, useState, useEffect } from 'react';
import './AgentCard.css';
import LiquidChrome from './LiquidChrome';
import AgentOrb from './AgentOrb';
import BloomOrb from './BloomOrb';
import SolverOrb from './SolverOrb';
import LoaderOrb from './LoaderOrb';

// Track active WebGL contexts to prevent "too many contexts" error
let activeWebGLContexts = 0;
const MAX_WEBGL_CONTEXTS = 8; // Conservative limit

const PERSONALITIES = {
  speedrunner: 'fast, competitive, efficiency-obsessed',
  bloom: 'creative, scattered, pattern-seeking',
  solver: 'logical, methodical, puzzle-driven',
  loader: 'patient, steady, process-oriented'
};

const AGENT_COLORS = {
  speedrunner: [0.08, 0.02, 0.03],  // Very dark red
  bloom: [0.06, 0.04, 0.08],        // Very dark purple
  solver: [0.08, 0.03, 0.06],       // Very dark magenta
  loader: [0.08, 0.05, 0.03]        // Very dark coral/orange
};

const TRANSCRIPTS = {
  speedrunner: 'Analyzing rapid execution patterns and optimization strategies for maximum throughput...',
  bloom: 'Processing distributed data points across neural network manifolds...',
  solver: 'Computing optimal solution paths using advanced heuristic algorithms...',
  loader: 'Loading synchronous operations with concurrent state management...'
};

const EXPANDED_CONTENT = {
  speedrunner: `<thinking>
Analyzing execution pipeline...
- Optimize critical path: O(n) -> O(log n)
- Implement parallel processing on batch operations
- Cache frequently accessed data structures
- Eliminate redundant API calls (12 -> 3)

Performance improvements:
  Initial load: 2.4s -> 0.6s (75% reduction)
  Response time: 450ms -> 180ms

Bottleneck identified in render loop
Applying memoization strategy...
</thinking>

<code_execution>
function optimizeRender() {
  const memoCache = new Map();
  return (data) => {
    const key = JSON.stringify(data);
    if (memoCache.has(key)) return memoCache.get(key);
    const result = expensiveRender(data);
    memoCache.set(key, result);
    return result;
  }
}
</code_execution>`,
  bloom: `<thinking>
Distributing data across neural layers...
- Input dimensions: 1024x768
- Hidden layers: [512, 256, 128, 64]
- Activation: ReLU with dropout(0.3)

Analyzing particle distribution patterns:
  Cluster 1: 342 nodes (density: 0.82)
  Cluster 2: 189 nodes (density: 0.64)
  Cluster 3: 276 nodes (density: 0.71)

Applying gradient descent optimization...
Learning rate: 0.001
Batch size: 32
</thinking>

<neural_network>
const network = {
  forward: (input) => {
    let activation = input;
    layers.forEach(layer => {
      activation = relu(layer.weights * activation);
    });
    return activation;
  }
}
</neural_network>`,
  solver: `<thinking>
Analyzing Rubik's cube state...
Current configuration: F2 R U' D L2 B
Solution depth: 18 moves (optimal: 20)

Heuristic search strategy:
- Pattern database lookup: 12ms
- A* algorithm applied
- Pruning inefficient branches

Move sequence generation:
  Step 1: F R U R' U' F'
  Step 2: R U R' U R U2 R'
  Step 3: U R U' L' U R' U' L

Validating solution path...
</thinking>

<algorithm>
function solveCube(state) {
  const visited = new Set();
  const queue = [{ state, moves: [] }];

  while (queue.length > 0) {
    const { state, moves } = queue.shift();
    if (isSolved(state)) return moves;

    for (let move of possibleMoves) {
      const newState = applyMove(state, move);
      if (!visited.has(hash(newState))) {
        visited.add(hash(newState));
        queue.push({ state: newState, moves: [...moves, move] });
      }
    }
  }
}
</algorithm>`,
  loader: `<thinking>
Synchronizing concurrent operations...
- Active threads: 5
- Queue size: 127 tasks
- Memory usage: 42.3 MB / 256 MB

Loading sequence initialization:
  Phase 1: Asset prefetch (23 items)
  Phase 2: Dependency resolution
  Phase 3: State hydration
  Phase 4: Event binding

Torus ring coordination:
  Ring 0: rotation(0.02, 0.01, 0.03)
  Ring 1: rotation(-0.01, 0.02, -0.01)
  Ring 2: rotation(0.03, -0.02, 0.01)
</thinking>

<async_loader>
async function loadResources() {
  const promises = resources.map(async (resource) => {
    const data = await fetch(resource.url);
    await processResource(data);
    updateProgress(resource.id);
  });

  await Promise.all(promises);
  finalizeLoading();
}
</async_loader>`
};

function AgentCard({ agentId, agentName, isExpanded, onExpand, onLike, code, isWorking, wins, onFetchCode, projectId }) {
  const cardRef = useRef(null);
  const codeDisplayRef = useRef(null);
  const [typedCode, setTypedCode] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  // Extract code from markdown code blocks if present
  const extractCode = (codeString) => {
    if (!codeString) return '';
    
    console.log(`[${agentId}] Extracting from:`, codeString.substring(0, 100));
    
    // Check if code is wrapped in markdown code blocks
    const codeBlockMatch = codeString.match(/```(?:\w+)?\n([\s\S]*?)```/);
    if (codeBlockMatch) {
      console.log(`[${agentId}] Found code block, extracted ${codeBlockMatch[1].length} chars`);
      return codeBlockMatch[1].trim();
    }
    
    console.log(`[${agentId}] No code block found, returning as-is`);
    return codeString;
  };

  const displayCode = extractCode(code);

  // Debug logging - disabled in production
  // console.log(`[${agentId}] code prop:`, code ? `${code.length} chars` : 'empty');
  // console.log(`[${agentId}] displayCode:`, displayCode ? `${displayCode.length} chars` : 'empty');

  // Typing animation effect with auto-scroll
  useEffect(() => {
    if (!displayCode || displayCode === typedCode) return;
    
    setIsTyping(true);
    setTypedCode('');
    
    let currentIndex = 0;
    const typingSpeed = 1; // milliseconds per character (super fast)
    
    const typeInterval = setInterval(() => {
      if (currentIndex < displayCode.length) {
        setTypedCode(displayCode.substring(0, currentIndex + 1));
        currentIndex++;
        
        // Auto-scroll to bottom
        if (codeDisplayRef.current) {
          codeDisplayRef.current.scrollTop = codeDisplayRef.current.scrollHeight;
        }
      } else {
        setIsTyping(false);
        clearInterval(typeInterval);
      }
    }, typingSpeed);
    
    return () => clearInterval(typeInterval);
  }, [displayCode]);

  const handleMouseMove = (e) => {
    if (!cardRef.current || isExpanded) return;
    const rect = cardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // Calculate tilt based on mouse position
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    const rotateX = (y - centerY) / 20;
    const rotateY = (centerX - x) / 20;

    cardRef.current.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;

    // Specular highlight
    const specular = cardRef.current.querySelector('.glass-specular');
    if (specular) {
      specular.style.background = `radial-gradient(circle at ${x}px ${y}px, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0.05) 30%, rgba(255,255,255,0) 60%)`;
    }
  };

  const handleMouseLeave = () => {
    if (!cardRef.current) return;
    cardRef.current.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';

    const specular = cardRef.current.querySelector('.glass-specular');
    if (specular) {
      specular.style.background = 'none';
    }
  };

  const handleNameClick = () => {
    onExpand(agentId);
  };

  const handleThumbsUp = (e) => {
    e.stopPropagation(); // Prevent backdrop click
    console.log('Thumbs up:', agentId);
    onLike(agentName); // Send like message to chat
    onExpand(null); // Close the expanded card
  };

  const handleFetchCode = (e) => {
    e.stopPropagation();
    if (onFetchCode && projectId) {
      onFetchCode(agentId);
    }
  };

  return (
    <div
      ref={cardRef}
      className={`glass-card ${isExpanded ? 'expanded' : ''}`}
      data-agent={agentId}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      <div className="glass-filter"></div>
      <div className="glass-overlay"></div>
      <div className="glass-specular"></div>
      <div className="glass-content">
        <div className="agent-headshot">
          <LiquidChrome
            baseColor={AGENT_COLORS[agentId]}
            speed={0.3}
            amplitude={0.4}
            frequencyX={3}
            frequencyY={3}
            interactive={false}
          />
          {/* WebGL orbs temporarily disabled to prevent context limit issues */}
          {/* Will be re-enabled with proper context management */}
        </div>
        <div className="agent-info">
          <div className="agent-header">
            <div>
              <div className="agent-name" onClick={handleNameClick}>
                {agentName}
                {wins > 0 && <span className="agent-wins"> 🏆 {wins}</span>}
              </div>
              <div className="agent-personality">
                {PERSONALITIES[agentId]}
              </div>
            </div>
            <div className="agent-actions">
              {isExpanded && (
                <button onClick={handleThumbsUp} className="agent-thumbs">
                  <i className="fas fa-thumbs-up"></i>
                </button>
              )}
            </div>
          </div>
          {isWorking && (
            <div className="agent-working-indicator">
              ⚡ Working on task...
            </div>
          )}
          <div className="agent-transcript">
            <div className="glass-filter"></div>
            <div className="glass-overlay"></div>
            <div className="glass-specular"></div>
            {code ? (
              typedCode ? (
                <pre ref={codeDisplayRef} className="agent-transcript-content agent-code-display">
                  {isExpanded ? typedCode : (typedCode.length > 200 ? typedCode.substring(0, 200) + '...' : typedCode)}
                  {isTyping && <span className="typing-cursor">▊</span>}
                </pre>
              ) : (
                <div className="agent-transcript-content">
                  <p>⏳ Loading code...</p>
                </div>
              )
            ) : (
              <div
                className="agent-transcript-content"
                dangerouslySetInnerHTML={{
                  __html: isExpanded ? EXPANDED_CONTENT[agentId] : TRANSCRIPTS[agentId]
                }}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default AgentCard;