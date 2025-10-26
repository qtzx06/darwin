# Darwin AI Battle Arena - API ↔ UI Integration Guide

## 🎯 Understanding the Complete Flow

Your system has **beautiful UI components** but they're not fully connected to the **backend APIs**. Here's how everything should work together:

---

## 📊 Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION.JSX                        │
│  (Main Controller - manages the entire battle flow)        │
└────────────┬────────────────────────────────────────────────┘
             │
             ├─► AgentCard (x4) - Shows agent status & code
             ├─► Commentator - AI commentary on battle
             ├─► ChatInput - User interaction
             └─► TranscriptPanel - Voice transcript
```

---

## 🔄 Complete API Flow (What SHOULD Happen)

### Phase 1: Project Setup
```javascript
// 1. User submits prompt on landing page
const projectId = apiUtils.generateProjectId();

// 2. Orchestrate project (breaks into subtasks)
const result = await competitiveApi.orchestrateProject(query);
// Returns: { subtasks: [{id: 1, title: "...", description: "..."}] }

// 3. Create LiveKit room for voice
const room = await livekitApi.createBattleRoom(projectId);
// Returns: { room_name: "darwin-battle-project_123" }
```

### Phase 2: Battle Execution (Per Subtask)
```javascript
// FOR EACH SUBTASK:

// 1. Start work on subtask
await competitiveApi.startWork(projectId, subtask.id);

// 2. Get agent results (their code submissions)
const results = await competitiveApi.getResults(projectId);
// Returns: {
//   agents: [
//     { agent_name: "One", code: "...", personality: "..." },
//     { agent_name: "Two", code: "...", personality: "..." },
//     ...
//   ]
// }

// 3. Get agent reactions to the event
const reactions = await livekitApi.getAgentReaction(
  roomName,
  'code_submitted',
  { agent_stats: {...}, total_rounds: 4 }
);
// Returns: {
//   agent_responses: [
//     { agent_name: "One", response_text: "...", emotion_level: 0.2 },
//     ...
//   ]
// }

// 4. Select winner
await competitiveApi.selectWinner(projectId, winnerName, reason);

// 5. Complete round
await competitiveApi.completeRound(projectId, winnerName, code, subtask.id);
```

---

## 🎨 UI Component Integration

### 1. **AgentCard.jsx** - Agent Display

**Current State:** Shows static content with hardcoded transcripts

**Should Connect To:**
```javascript
// In Orchestration.jsx, pass real agent data:
<AgentCard
  agentId="speedrunner"
  agentName="Speedrunner"
  agentData={agentResults.find(a => a.agent_name === 'One')}
  currentSubtask={currentSubtask}
  isWorking={isWorkflowRunning}
  code={agentCode}  // From getResults()
  reaction={agentReaction}  // From getAgentReaction()
/>
```

**What AgentCard Should Display:**
- ✅ Agent's current code (from `/api/get-results`)
- ✅ Agent's reaction text (from `/api/livekit/agent-reaction`)
- ✅ Working status (from state)
- ✅ Win count (from `/api/agent-stats`)

### 2. **Commentator.jsx** - AI Commentary

**Current State:** Just shows visual orb

**Should Connect To:**
```javascript
// In Commentator.jsx:
const [commentary, setCommentary] = useState('');

useEffect(() => {
  if (subtaskId) {
    // Get commentary for current subtask
    competitiveApi.getCommentary(projectId, subtaskId)
      .then(result => setCommentary(result.commentary));
  }
}, [subtaskId]);

// Also connect to voice:
const handleAskCommentator = async (question) => {
  const response = await livekitApi.askCommentator(roomName, question);
  // Play audio response
  const audioBlob = await livekitApi.speakText(
    response.response_text,
    'gnPxliFHTp6OK6tcoA6i'  // Commentator voice ID
  );
  playAudio(audioBlob);
};
```

### 3. **ChatInput.jsx** - User Interaction

**Current State:** Accepts messages but doesn't send to API

**Should Connect To:**
```javascript
// In ChatInput.jsx:
const handleSendMessage = async (message) => {
  // Determine mode (commentary vs agent)
  if (currentMode === 'commentary') {
    // Ask commentator
    const response = await livekitApi.askCommentator(roomName, message);
    const audioBlob = await livekitApi.speakText(response.response_text);
    playAudio(audioBlob);
  } else if (selectedAgent) {
    // Ask specific agent
    const response = await livekitApi.askAgent(roomName, selectedAgent, message);
    const audioBlob = await livekitApi.speakText(
      response.response_text,
      agentVoiceIds[selectedAgent]
    );
    playAudio(audioBlob);
  }
};
```

### 4. **TranscriptPanel.jsx** - Voice Transcript

**Current State:** Empty or static

**Should Connect To:**
```javascript
// In TranscriptPanel.jsx:
const [transcript, setTranscript] = useState([]);

useEffect(() => {
  const interval = setInterval(async () => {
    if (roomName) {
      const result = await livekitApi.getTranscript(roomName);
      setTranscript(result.transcript);
    }
  }, 2000);  // Poll every 2 seconds

  return () => clearInterval(interval);
}, [roomName]);

// Display transcript:
{transcript.map(msg => (
  <div key={msg.timestamp} className={`message ${msg.speaker.toLowerCase()}`}>
    <span className="time">{msg.time_formatted}</span>
    <span className="speaker">{msg.speaker}:</span>
    <span className="text">{msg.text}</span>
  </div>
))}
```

---

## 🔥 Enhanced Orchestration.jsx (Complete Integration)

Here's how your `Orchestration.jsx` should work with ALL components connected:

```javascript
const startBattle = async () => {
  setIsWorkflowRunning(true);
  setWorkflowStarted(true);

  try {
    // Get agent voice config
    const voiceConfig = await livekitApi.getAgentConfig();
    setAgentVoiceIds(voiceConfig.agent_config);

    // Run competitive rounds
    for (const subtask of subtasks) {
      setCurrentSubtask(subtask);

      // 1. Start work
      await competitiveApi.startWork(projectId, subtask.id);

      // 2. Get progress messages (for UI updates)
      const progress = await competitiveApi.getProgressMessages(projectId);
      updateAgentProgress(progress);

      // 3. Get results
      const results = await competitiveApi.getResults(projectId);
      setAgentResults(results.agents);

      // 4. Update each AgentCard with their code
      results.agents.forEach(agent => {
        updateAgentCard(agent.agent_name, {
          code: agent.code,
          status: 'completed'
        });
      });

      // 5. Get agent reactions
      const reactions = await livekitApi.getAgentReaction(
        roomName,
        'code_submitted',
        {
          agent_stats: await competitiveApi.getAgentStats(projectId),
          total_rounds: subtasks.length
        }
      );

      // 6. Display reactions in AgentCards
      reactions.agent_responses.forEach(reaction => {
        updateAgentCard(reaction.agent_name, {
          reaction: reaction.response_text,
          emotion: reaction.emotion_level
        });
      });

      // 7. Get commentary
      const commentary = await competitiveApi.getCommentary(projectId, subtask.id);
      setCommentatorText(commentary.commentary);

      // 8. Select winner
      const winnerName = selectBestAgent(results.agents);
      setWinner(winnerName);
      await competitiveApi.selectWinner(projectId, winnerName, 'Best code quality');

      // 9. Get winner reaction
      const winnerReaction = await livekitApi.getAgentReaction(
        roomName,
        'won_round',
        { winner: winnerName }
      );
      playWinnerReaction(winnerReaction);

      // 10. Complete round
      const winnerCode = results.agents.find(a => a.agent_name === winnerName).code;
      await competitiveApi.completeRound(projectId, winnerName, winnerCode, subtask.id);
    }

    // Final status
    const finalStatus = await competitiveApi.getProjectStatus(projectId);
    setProjectStatus(finalStatus);

  } catch (error) {
    console.error('Battle error:', error);
  } finally {
    setIsWorkflowRunning(false);
  }
};
```

---

## 🎯 Key Missing Connections

### 1. **AgentCard** needs props:
```javascript
// Add to AgentCard.jsx:
const AgentCard = ({
  agentId,
  agentName,
  code,           // ← From /api/get-results
  reaction,       // ← From /api/livekit/agent-reaction
  isWorking,      // ← From state
  winCount,       // ← From /api/agent-stats
  onExpand,
  onLike
}) => {
  // Display real code instead of hardcoded content
  return (
    <div className="agent-card">
      {isWorking && <div className="working-indicator">⚡ Working...</div>}
      <pre className="agent-code">{code}</pre>
      <div className="agent-reaction">{reaction}</div>
      <div className="agent-stats">Wins: {winCount}</div>
    </div>
  );
};
```

### 2. **Commentator** needs real commentary:
```javascript
// Add to Commentator.jsx:
const Commentator = ({ projectId, subtaskId }) => {
  const [commentary, setCommentary] = useState('');

  useEffect(() => {
    if (projectId && subtaskId) {
      competitiveApi.getCommentary(projectId, subtaskId)
        .then(result => setCommentary(result.commentary));
    }
  }, [projectId, subtaskId]);

  return (
    <div className="commentator-card">
      <CommentatorOrb />
      <div className="commentary-text">{commentary}</div>
    </div>
  );
};
```

### 3. **ChatInput** needs API calls:
```javascript
// Add to ChatInput.jsx:
const ChatInput = ({ roomName, currentMode, selectedAgent }) => {
  const handleSubmit = async (message) => {
    if (currentMode === 'commentary') {
      const response = await livekitApi.askCommentator(roomName, message);
      playAudio(response.response_text);
    } else {
      const response = await livekitApi.askAgent(roomName, selectedAgent, message);
      playAudio(response.response_text);
    }
  };
};
```

---

## 🚀 Action Items

1. **Pass real data to AgentCards**
   - Code from `/api/get-results`
   - Reactions from `/api/livekit/agent-reaction`
   - Stats from `/api/agent-stats`

2. **Connect Commentator to API**
   - Get commentary from `/api/get-commentary`
   - Enable voice questions via `/api/livekit/ask-commentator`

3. **Connect ChatInput to voice system**
   - Send messages to commentator or agents
   - Play audio responses

4. **Update TranscriptPanel**
   - Poll `/api/livekit/get-transcript`
   - Display real-time conversation

5. **Add visual feedback**
   - Show "working" state during API calls
   - Display progress for each subtask
   - Highlight winner after each round

---

## 📝 Summary

**Problem:** Your UI components exist but aren't receiving real data from the backend APIs.

**Solution:** Pass API responses as props to components and update them in real-time during the battle.

**Result:** Beautiful UI + Real AI agent data = Complete system! 🎉
