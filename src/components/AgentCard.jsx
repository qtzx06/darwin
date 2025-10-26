import { useRef, useState, useEffect } from 'react';
import './AgentCard.css';
import LiquidChrome from './LiquidChrome';
import AgentOrb from './AgentOrb';
import BloomOrb from './BloomOrb';
import SolverOrb from './SolverOrb';
import LoaderOrb from './LoaderOrb';
import DecryptedText from './DecryptedText';
import { voteForAgent } from '../utils/suiClient';

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
  speedrunner: [
    'optimizing critical path O(n) to O(log n) lets GO!',
    'caching data structures, eliminating 12 API calls down to 3!',
    'parallel processing ACTIVATED! initial load 2.4s to 0.6s BOOM!',
    'response time 450ms to 180ms we FLYING!',
    'bottleneck in render loop spotted, applying memoization NOW!',
    '75% load time reduction achieved baby!',
    'concurrent requests optimized, throughput MAXIMIZED!',
    'lazy loading implemented, bundle size cut in HALF!',
    'debouncing inputs, performance CRANKED!',
    'tree-shaking dependencies, dead code ELIMINATED!',
    'implementing virtual scrolling, rendering 10k items smooth!',
    'code splitting routes, initial bundle 2MB to 400KB!',
    'webworkers deployed, UI thread FREED UP!',
    'compression enabled, gzip assets 80% smaller!',
    'CDN configured, global latency DOWN!',
    'service workers caching, offline mode READY!'
  ],
  bloom: [
    'scattering thoughts... distributing data across neural layers...',
    'input dimensions 1024x768, hidden layers [512, 256, 128, 64]...',
    'ReLU activation with dropout 0.3, wait what was I...',
    'cluster 1: 342 nodes density 0.82, interesting patterns...',
    'cluster 2: 189 nodes density 0.64, hmm...',
    'gradient descent optimization, learning rate 0.001...',
    'batch size 32, convergence looking good...',
    'oh right! neural network manifolds processing...',
    'particle distribution patterns emerging...',
    'hidden layer activations stabilizing, nice...',
    'attention mechanism weights adjusting... focus shifting...',
    'backpropagation through time, memories forming...',
    'embedding space expanding, semantic relationships...',
    'softmax probabilities normalizing, decisions crystallizing...',
    'convolutional filters detecting edges, shapes, textures...',
    'recurrent connections creating temporal dependencies...'
  ],
  solver: [
    'analyzing current configuration... F2 R U\' D L2 B',
    'solution depth 18 moves, optimal is 20, acceptable.',
    'pattern database lookup: 12ms, efficient.',
    'A* algorithm applied, pruning inefficient branches.',
    'move sequence generation: step 1 F R U R\' U\' F\'',
    'step 2 R U R\' U R U2 R\', validating...',
    'step 3 U R U\' L\' U R\' U\' L, checking path...',
    'heuristic search complete, solution found.',
    'verification complete, path optimal.',
    'systematic branch elimination successful.',
    'constraint satisfaction problem solved, all variables assigned.',
    'backtracking algorithm terminated, solution space explored.',
    'dynamic programming table computed, subproblems cached.',
    'binary search converging, bounds narrowing systematically.',
    'graph traversal complete, shortest path identified.',
    'minimax tree evaluated, optimal strategy determined.'
  ],
  loader: [
    'initializing... active threads: 5, queue size: 127 tasks',
    'memory usage 42.3 MB / 256 MB, stable.',
    'loading sequence phase 1: asset prefetch 23 items',
    'phase 2: dependency resolution in progress...',
    'phase 3: state hydration queued, waiting...',
    'phase 4: event binding scheduled.',
    'torus ring 0 rotation(0.02, 0.01, 0.03), synchronized.',
    'torus ring 1 rotation(-0.01, 0.02, -0.01), coordinated.',
    'torus ring 2 rotation(0.03, -0.02, 0.01), aligned.',
    'all systems nominal, processes running smoothly...',
    'buffer pool allocation complete, resources distributed.',
    'connection pool established, 20 connections ready.',
    'lazy initialization deferred, memory footprint minimal.',
    'middleware chain assembled, request pipeline configured.',
    'cache warming in progress, hot data preloaded.',
    'graceful degradation enabled, fallbacks prepared.'
  ]
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

function AgentCard({ agentId, agentName, isExpanded, onExpand, onLike, voteCount = 0 }) {
  const cardRef = useRef(null);
  const [currentMessageIndex, setCurrentMessageIndex] = useState(0);
  const [visibleMessages, setVisibleMessages] = useState([0]); // Track which messages are visible

  // Cycle through transcript messages (append one at a time, show 4 total)
  useEffect(() => {
    if (!isExpanded) {
      // Speedrunner cycles faster
      const cycleSpeed = agentId === 'speedrunner' ? 1200 : 2500;
      const interval = setInterval(() => {
        setVisibleMessages(prev => {
          const lastIndex = prev[prev.length - 1];
          const nextIndex = lastIndex + 1;

          // If we have 4 messages visible, reset to show next group
          if (prev.length >= 4) {
            const newStartIndex = (lastIndex + 1) % TRANSCRIPTS[agentId].length;
            return [newStartIndex];
          }

          // If we've reached the end of messages, wrap to 0
          if (nextIndex >= TRANSCRIPTS[agentId].length) {
            return [0];
          }

          // Otherwise append the next message
          return [...prev, nextIndex];
        });
      }, cycleSpeed);

      return () => clearInterval(interval);
    }
  }, [agentId, isExpanded]);

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

  const handleThumbsUp = async (e) => {
    e.stopPropagation(); // Prevent backdrop click
    console.log('Thumbs up:', agentId);

    try {
      // Map agentId to numeric value for blockchain
      const agentMap = { speedrunner: 0, bloom: 1, solver: 2, loader: 3 };
      const agentNumericId = agentMap[agentId];

      // Submit vote to blockchain via sponsored transaction
      await voteForAgent(agentNumericId);

      onLike(agentName, agentId); // Send like message to chat with agentId
      onExpand(null); // Close the expanded card
    } catch (error) {
      console.error('Failed to submit vote:', error);
      alert('Failed to vote. Please try again.');
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
          {agentId === 'speedrunner' && <AgentOrb />}
          {agentId === 'bloom' && <BloomOrb />}
          {agentId === 'solver' && <SolverOrb />}
          {agentId === 'loader' && <LoaderOrb />}
        </div>
        <div className="agent-info">
          <div className="agent-header">
            <div>
              <div className="agent-name" onClick={handleNameClick}>
                {agentName}
              </div>
              <div className="agent-personality">
                {PERSONALITIES[agentId]}
              </div>
            </div>
            {isExpanded && (
              <button onClick={handleThumbsUp} className="agent-thumbs">
                <i className="fas fa-thumbs-up"></i>
                <span className="vote-count">{voteCount}</span>
              </button>
            )}
          </div>
          <div className="agent-transcript">
            <div className="glass-filter"></div>
            <div className="glass-overlay"></div>
            <div className="glass-specular"></div>
            <div className="agent-transcript-content">
              {isExpanded ? (
                <div dangerouslySetInnerHTML={{ __html: EXPANDED_CONTENT[agentId] }} />
              ) : (
                <>
                  {visibleMessages.map((msgIndex, idx) => (
                    <div key={`${msgIndex}-${idx}`}>
                      <DecryptedText
                        text={TRANSCRIPTS[agentId][msgIndex]}
                        speed={agentId === 'speedrunner' ? 20 : 30}
                        sequential={true}
                        revealDirection="start"
                        animateOn="view"
                      />
                    </div>
                  ))}
                  <div className="loading-dots">
                    <span>.</span>
                    <span>.</span>
                    <span>.</span>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AgentCard;
