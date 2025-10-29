import { useRef, useState, useEffect } from 'react';
import './AgentCard.css';
import LiquidChrome from './LiquidChrome';
import AgentOrb from './AgentOrb';
import BloomOrb from './BloomOrb';
import SolverOrb from './SolverOrb';
import LoaderOrb from './LoaderOrb';
import DecryptedText from './DecryptedText';
import CodeRenderer from './CodeRenderer';
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
  speedrunner: `<thinking>Analyzing execution pipeline...
- Optimize critical path: O(n) -> O(log n)
- Implement parallel processing on batch operations
- Cache frequently accessed data structures
- Eliminate redundant API calls (12 -> 3)

Performance improvements:
  Initial load: 2.4s -> 0.6s (75% reduction)
  Response time: 450ms -> 180ms
  Time to interactive: 3.2s -> 0.9s
  First contentful paint: 1.8s -> 0.4s
  Largest contentful paint: 2.6s -> 0.7s

Bottleneck identified in render loop
Applying memoization strategy...

Database query optimization:
- Index creation on frequently accessed columns
- Query plan optimization: nested loops -> hash joins
- Connection pool size: 10 -> 50
- Query cache hit rate: 45% -> 89%

Bundle size analysis:
- Main bundle: 2.4MB -> 680KB (71% reduction)
- Vendor bundle: 1.8MB -> 420KB
- CSS bundle: 340KB -> 95KB
- Total asset size: 4.54MB -> 1.19MB

Code splitting implementation:
- Route-based chunks: 8 created
- Dynamic imports: 23 locations
- Lazy loading components: 14 implemented
- Initial bundle load: 680KB (down from 2.4MB)

Compression strategy:
- Gzip enabled: 60% size reduction
- Brotli compression: additional 15% savings
- Image optimization: WebP format, 78% smaller
- Font subsetting: 42% reduction

Caching strategy deployed:
- Service worker installed
- Cache-first for static assets
- Network-first for API calls
- Stale-while-revalidate for images
- Cache hit rate: 87%

Performance metrics after optimization:
  Lighthouse score: 98/100
  Core Web Vitals: all green
  Time to interactive: 0.9s
  Total blocking time: 120ms
  Cumulative layout shift: 0.02
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

function parallelProcess(tasks) {
  const workers = new Array(navigator.hardwareConcurrency)
    .fill(null)
    .map(() => new Worker('worker.js'));

  return Promise.all(
    tasks.map((task, i) => {
      const worker = workers[i % workers.length];
      return new Promise(resolve => {
        worker.postMessage(task);
        worker.onmessage = e => resolve(e.data);
      });
    })
  );
}

function debounce(fn, delay) {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
}

const lazyLoadImage = (img) => {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        img.src = img.dataset.src;
        observer.unobserve(img);
      }
    });
  });
  observer.observe(img);
};
</code_execution>`,
  bloom: `<thinking>Distributing data across neural layers...
- Input dimensions: 1024x768
- Hidden layers: [512, 256, 128, 64]
- Activation: ReLU with dropout(0.3)

Analyzing particle distribution patterns:
  Cluster 1: 342 nodes (density: 0.82)
  Cluster 2: 189 nodes (density: 0.64)
  Cluster 3: 276 nodes (density: 0.71)
  Cluster 4: 423 nodes (density: 0.89)
  Cluster 5: 198 nodes (density: 0.56)
  Cluster 6: 312 nodes (density: 0.77)
  Cluster 7: 267 nodes (density: 0.68)

Applying gradient descent optimization...
Learning rate: 0.001
Batch size: 32
Momentum: 0.9
Weight decay: 0.0001

Initializing transformer architecture...
- Attention heads: 8
- Model dimension: 512
- Feed-forward dimension: 2048
- Number of layers: 12

Training metrics after epoch 1:
  Loss: 2.456
  Accuracy: 67.3%
  Validation loss: 2.589
  Learning curve stabilizing...

Training metrics after epoch 2:
  Loss: 1.923
  Accuracy: 73.8%
  Validation loss: 2.102
  Gradient norm: 0.043

Training metrics after epoch 3:
  Loss: 1.567
  Accuracy: 78.2%
  Validation loss: 1.834
  Overfitting check: passed

Computing attention patterns...
Positional encodings applied...
Self-attention mechanism converging...
Cross-attention weights balanced...
</thinking>

<neural_network>
const network = {
  forward: (input) => {
    let activation = input;
    layers.forEach(layer => {
      activation = relu(layer.weights * activation);
    });
    return activation;
  },

  backward: (error, learningRate) => {
    let delta = error;
    layers.reverse().forEach(layer => {
      const gradient = layer.computeGradient(delta);
      layer.updateWeights(gradient, learningRate);
      delta = layer.backpropagate(delta);
    });
  },

  train: (data, epochs) => {
    for (let epoch = 0; epoch < epochs; epoch++) {
      const predictions = this.forward(data);
      const loss = computeLoss(predictions, data.labels);
      this.backward(loss, 0.001);
      console.log(\`Epoch \${epoch + 1}: Loss = \${loss}\`);
    }
  },

  evaluate: (testData) => {
    const predictions = this.forward(testData);
    const accuracy = computeAccuracy(predictions, testData.labels);
    return accuracy;
  }
}

// Advanced activation functions
function relu(x) {
  return Math.max(0, x);
}

function sigmoid(x) {
  return 1 / (1 + Math.exp(-x));
}

function tanh(x) {
  return Math.tanh(x);
}

function softmax(x) {
  const exp = x.map(val => Math.exp(val));
  const sum = exp.reduce((a, b) => a + b, 0);
  return exp.map(val => val / sum);
}
</neural_network>`,
  solver: `<thinking>Analyzing Rubik's cube state...
Current configuration: F2 R U' D L2 B
Solution depth: 18 moves (optimal: 20)

Heuristic search strategy:
- Pattern database lookup: 12ms
- A* algorithm applied
- Pruning inefficient branches
- Admissible heuristic verified
- Consistency property confirmed

State space analysis:
  Total possible states: 43,252,003,274,489,856,000
  Reachable states from current: 2,847,392
  Pruned branches: 1,923,847
  Active search nodes: 923,545
  Memory usage: 47.3 MB

Move sequence generation:
  Step 1: F R U R' U' F' (cross completion)
  Step 2: R U R' U R U2 R' (first pair)
  Step 3: U R U' L' U R' U' L (second pair)
  Step 4: F' U' L' U L F (third pair)
  Step 5: R U R' U' R U R' (fourth pair)
  Step 6: R U R' U R U2 R' (OLL)
  Step 7: R U R' U' R' F R2 U' R' U' R U R' F' (PLL)

Validating solution path...
All moves legal: ✓
Solution optimality: 18 moves (within 10% of optimal)
Execution time: 47ms
Pattern database hits: 142
Cache efficiency: 94%

Alternative solution paths explored:
  Path A: 19 moves (rotation-heavy)
  Path B: 20 moves (fewer rotations)
  Path C: 18 moves (selected - balanced)

Constraint satisfaction verification:
- All corners positioned correctly
- All edges oriented properly
- Parity check: passed
- Final state validation: complete
</thinking>

<algorithm>
function solveCube(state) {
  const visited = new Set();
  const queue = [{ state, moves: [], cost: 0 }];
  const heuristic = (s) => estimateMovesToSolution(s);

  while (queue.length > 0) {
    // Sort by f(n) = g(n) + h(n)
    queue.sort((a, b) =>
      (a.cost + heuristic(a.state)) -
      (b.cost + heuristic(b.state))
    );

    const { state, moves, cost } = queue.shift();
    if (isSolved(state)) return moves;

    for (let move of possibleMoves) {
      const newState = applyMove(state, move);
      const stateHash = hash(newState);

      if (!visited.has(stateHash)) {
        visited.add(stateHash);
        queue.push({
          state: newState,
          moves: [...moves, move],
          cost: cost + 1
        });
      }
    }
  }
  return null;
}

function estimateMovesToSolution(state) {
  // Pattern database heuristic
  const cornerDistance = getCornerDistance(state);
  const edgeDistance = getEdgeDistance(state);
  return Math.max(cornerDistance, edgeDistance);
}

function applyMove(state, move) {
  const newState = JSON.parse(JSON.stringify(state));
  switch(move) {
    case 'F': rotateFace(newState, 'front', 1); break;
    case 'B': rotateFace(newState, 'back', 1); break;
    case 'L': rotateFace(newState, 'left', 1); break;
    case 'R': rotateFace(newState, 'right', 1); break;
    case 'U': rotateFace(newState, 'up', 1); break;
    case 'D': rotateFace(newState, 'down', 1); break;
  }
  return newState;
}
</algorithm>`,
  loader: `<thinking>Synchronizing concurrent operations...
- Active threads: 5
- Queue size: 127 tasks
- Memory usage: 42.3 MB / 256 MB
- CPU utilization: 34%
- Network bandwidth: 2.4 MB/s

Loading sequence initialization:
  Phase 1: Asset prefetch (23 items)
    - Images: 12 items (8.4 MB)
    - Scripts: 7 items (2.1 MB)
    - Styles: 4 items (840 KB)
  Phase 2: Dependency resolution
    - npm packages: 247 resolved
    - Peer dependencies: all satisfied
    - Circular dependencies: 0 detected
  Phase 3: State hydration
    - Redux store: initializing
    - Local storage: 3.2 MB loaded
    - Session storage: 847 KB loaded
  Phase 4: Event binding
    - DOM listeners: 89 attached
    - WebSocket connections: 3 active
    - Service workers: 1 registered

Torus ring coordination:
  Ring 0: rotation(0.02, 0.01, 0.03)
    - Vertices: 2048
    - Triangles: 4096
    - Material: PBR with metalness 0.8
  Ring 1: rotation(-0.01, 0.02, -0.01)
    - Vertices: 2048
    - Triangles: 4096
    - Material: Glass with refraction 1.5
  Ring 2: rotation(0.03, -0.02, 0.01)
    - Vertices: 2048
    - Triangles: 4096
    - Material: Emissive with intensity 2.0

Resource loading progress:
  0-10%: Initializing core systems
  10-25%: Loading critical assets
  25-50%: Processing dependencies
  50-75%: Hydrating application state
  75-90%: Binding event listeners
  90-100%: Finalizing and rendering

Thread pool status:
  Thread 1: Processing images (active)
  Thread 2: Compiling shaders (active)
  Thread 3: Parsing JSON (idle)
  Thread 4: Decompressing assets (active)
  Thread 5: Validating checksums (active)

Network requests:
  Completed: 187
  In progress: 12
  Failed: 0
  Cached: 143
  Average latency: 47ms

Memory allocation:
  Heap size: 42.3 MB
  External memory: 18.7 MB
  Used: 38.9 MB (92%)
  Available: 217.1 MB

All systems nominal, processes running smoothly...
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

class ResourceLoader {
  constructor(options = {}) {
    this.concurrency = options.concurrency || 5;
    this.timeout = options.timeout || 30000;
    this.retries = options.retries || 3;
    this.queue = [];
    this.activeRequests = 0;
  }

  async load(resources) {
    this.queue = [...resources];
    const results = [];

    while (this.queue.length > 0 || this.activeRequests > 0) {
      while (
        this.activeRequests < this.concurrency &&
        this.queue.length > 0
      ) {
        const resource = this.queue.shift();
        this.activeRequests++;

        this.loadResource(resource)
          .then(result => results.push(result))
          .finally(() => this.activeRequests--);
      }

      await new Promise(resolve => setTimeout(resolve, 10));
    }

    return results;
  }

  async loadResource(resource, attempt = 0) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(
        () => controller.abort(),
        this.timeout
      );

      const response = await fetch(resource.url, {
        signal: controller.signal
      });

      clearTimeout(timeoutId);
      return await response.json();
    } catch (error) {
      if (attempt < this.retries) {
        return this.loadResource(resource, attempt + 1);
      }
      throw error;
    }
  }
}
</async_loader>`
};

function AgentCard({ agentId, agentName, isExpanded, onExpand, onLike, onPreview, voteCount = 0, generatedCode = null, statusMessage = '' }) {
  const cardRef = useRef(null);
  const [currentMessageIndex, setCurrentMessageIndex] = useState(0);
  const [visibleMessages, setVisibleMessages] = useState([0]); // Track which messages are visible
  const [displayedCode, setDisplayedCode] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  // Typing animation for generated code
  useEffect(() => {
    if (!generatedCode) return;

    setDisplayedCode('');
    setIsTyping(true);
    let currentIndex = 0;

    const typingInterval = setInterval(() => {
      if (currentIndex < generatedCode.length) {
        setDisplayedCode(generatedCode.slice(0, currentIndex + 1));
        currentIndex++;
      } else {
        setIsTyping(false);
        clearInterval(typingInterval);
      }
    }, 5); // Type 1 character every 5ms

    return () => clearInterval(typingInterval);
  }, [generatedCode]);

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
            {isExpanded ? (
              <div className="agent-split-view">
                <div className="agent-code-side">
                  {generatedCode ? (
                    <pre className="agent-generated-code">
                      {displayedCode}
                      {isTyping && <span className="typing-cursor">▋</span>}
                    </pre>
                  ) : (
                    <pre className="agent-generated-code" dangerouslySetInnerHTML={{ __html: EXPANDED_CONTENT[agentId] }} />
                  )}
                </div>
                <div className="agent-preview-side">
                  <CodeRenderer code={generatedCode} onClose={null} />
                </div>
              </div>
            ) : (
              <div className="agent-transcript-content">
                {visibleMessages.map((msgIndex, idx) => (
                  <div key={`${msgIndex}-${idx}`} className="transcript-message">
                    {TRANSCRIPTS[agentId][msgIndex]}
                  </div>
                ))}
                <div className="loading-dots">
                  <span>.</span>
                  <span>.</span>
                  <span>.</span>
                </div>
                {statusMessage && (
                  <div className="agent-status-message">
                    {statusMessage}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default AgentCard;
