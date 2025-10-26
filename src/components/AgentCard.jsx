import { useRef } from 'react';
import './AgentCard.css';

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

function AgentCard({ agentId, agentName, isExpanded, onExpand }) {
  const cardRef = useRef(null);

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
        <div className="agent-name" onClick={handleNameClick}>
          {agentName}
        </div>
        <div className="icon-wrapper">
          <canvas id={agentId} className="agent-canvas"></canvas>
        </div>
        <div className="agent-transcript">
          <div className="glass-filter"></div>
          <div className="glass-overlay"></div>
          <div className="glass-specular"></div>
          <div
            className="agent-transcript-content"
            dangerouslySetInnerHTML={{
              __html: isExpanded ? EXPANDED_CONTENT[agentId] : TRANSCRIPTS[agentId]
            }}
          />
        </div>
      </div>
    </div>
  );
}

export default AgentCard;
