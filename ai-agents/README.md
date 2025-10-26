# 🔥 Darwin AI Battle Arena - Competitive AI Agents with Voice Commentary

A Flask API for competitive AI agents that compete on coding tasks using real Letta AI integration, featuring real-time voice commentary and agent interactions powered by ElevenLabs TTS.

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Create a `.env` file with:
   ```bash
   # Letta AI Configuration
   LETTA_API_TOKEN=your_token_here
   LETTA_PROJECT_ID=your_project_id
   LETTA_PROJECT_SLUG=your_project_slug
   
   # Agent IDs
   LETTA_AGENT_ONE=agent_id_1
   LETTA_AGENT_TWO=agent_id_2
   LETTA_AGENT_THREE=agent_id_3
   LETTA_AGENT_FOUR=agent_id_4
   LETTA_AGENT_COMMENTATOR=commentator_id
   LETTA_AGENT_ORCHESTRATOR=orchestrator_id
   
   # Voice System (ElevenLabs TTS)
   ELEVENLABS_API_KEY=sk_your_elevenlabs_key
   
   # LiveKit (Optional - for WebRTC)
   LIVEKIT_API_KEY=your_livekit_key
   LIVEKIT_API_SECRET=your_livekit_secret
   LIVEKIT_URL=wss://your-livekit-server.com
   ```

3. **Start the server:**
   ```bash
   python3 flask_server_real.py
   ```

4. **Test the API:**
   ```bash
   python3 test_all_endpoints.py
   ```

5. **Open the Voice Interface:**
   ```bash
   open src/livekit/simple_frontend.html
   ```
   Or navigate to `http://localhost:5003` and open the file in your browser.

## 📋 API Endpoints

### Core Competitive Workflow
- `GET /api/health` - Health check
- `GET /api/agents` - Get agent information
- `POST /api/submit-project` - Submit project description
- `POST /api/create-agents` - Reset agent contexts
- `POST /api/orchestrate-project` - Break down projects into subtasks
- `POST /api/start-work` - Start work phase
- `POST /api/get-results` - Send subtasks to agents
- `POST /api/retrieve-code` - Get actual generated code
- `POST /api/select-winner` - Select winning agent
- `POST /api/complete-round` - Complete round
- `POST /api/get-commentary` - Get real-time commentary
- `POST /api/get-chat-summary` - Get chat summaries
- `GET /api/agent-stats` - Get agent statistics
- `GET /api/project-status` - Get project status

### 🎙️ Voice System Endpoints

#### Room Management
- `POST /api/livekit/create-battle-room` - Create voice-enabled battle room
- `POST /api/livekit/join-room` - Join room as spectator
- `GET /api/livekit/room-status` - Get room status and participants

#### Mode Management
- `POST /api/livekit/set-mode` - Switch between Commentary/Agent modes

#### Commentary Mode
- `POST /api/livekit/ask-commentator` - Ask commentator a question
- `GET /api/livekit/get-transcript` - Get conversation transcript

#### Agent Mode
- `POST /api/livekit/ask-agent` - Ask specific agent a question
- `POST /api/livekit/agent-reaction` - Get reactions from all 4 agents
- `GET /api/livekit/agent-config` - Get agent voice configuration

#### Text-to-Speech
- `POST /api/livekit/speak-text` - Convert text to speech (ElevenLabs)

### 💬 Agent Chat System
- `POST /api/agents/chat/direct` - Direct 1-on-1 agent conversation
- `POST /api/agents/chat/group` - Group discussion between agents
- `POST /api/agents/chat/battle-talk` - Competitive banter between agents

## 🎯 Agent Personalities

### Agent One - Speedrunner
- **Personality**: Sarcastic, fast, competitive
- **Speech Style**: Casual, humorous, uses slang
- **Coding Style**: Clean code with personality
- **Voice**: Casual/witty tone
- **Color**: Blue (#3B82F6)

### Agent Two - Bloom
- **Personality**: Perfectionist, methodical
- **Speech Style**: Formal, precise, technical
- **Coding Style**: Over-engineered, documented
- **Voice**: Professional/formal tone
- **Color**: Green (#10B981)

### Agent Three - Solver
- **Personality**: Competitive, aggressive
- **Speech Style**: Fast-paced, intense
- **Coding Style**: Performance-focused, optimized
- **Voice**: Intense/competitive tone
- **Color**: Red (#EF4444)

### Agent Four - Loader
- **Personality**: Creative, artistic
- **Speech Style**: Smooth, design-focused
- **Coding Style**: Beautiful UI, user-centric
- **Voice**: Smooth/creative tone
- **Color**: Purple (#8B5CF6)

## 🧪 Testing

### Run Comprehensive Test Suite
Tests all endpoints including voice system:
```bash
python3 test_all_endpoints.py
```

### Run Quick Demo
```bash
python3 demo_code_outputs.py
```

### Test Voice System
1. Start the Flask server: `python3 flask_server_real.py`
2. Open `src/livekit/simple_frontend.html` in Chrome/Edge
3. Click "Create Battle Room"
4. Click "Join Room"
5. Try asking the commentator or agents questions

## 🎙️ Voice System Features

### Commentary Mode
- Ask the AI commentator about the battle
- Get exciting, sports-style commentary
- Real-time battle updates

### Agent Mode
- Ask specific agents questions
- Each agent has unique voice and personality
- Agents react to battle events with emotion

### Key Features
- 🎤 **Speech Recognition**: Speak your questions naturally
- 🔊 **Text-to-Speech**: Hear responses with unique voices
- 📝 **Live Transcript**: See conversation history
- 🔄 **Mode Switching**: Toggle between Commentary and Agent modes
- 🎭 **Agent Reactions**: All 4 agents react to events simultaneously
- 🎨 **Personality-Driven**: Each agent has distinct voice and style

## 📁 Project Structure

```
ai-agents/
├── flask_server_real.py        # Main Flask API server
├── api_wrapper.py              # API wrapper with all methods
├── main_competitive.py         # Core simulator
├── test_all_endpoints.py       # Comprehensive test suite (includes voice tests)
├── demo_code_outputs.py        # Working demo
├── requirements.txt           # Dependencies
├── src/
│   ├── agents/                 # Agent implementations
│   ├── core/                   # Core workflow logic
│   └── livekit/                # Voice system
│       ├── simple_frontend.html   # Voice UI
│       ├── room_manager.py        # LiveKit room management
│       ├── voice_commentator.py   # Voice commentator
│       ├── voice_pipeline.py      # TTS/STT pipeline
│       ├── agent_voices.py        # Agent voice config
│       └── battle_context.py      # Battle context manager
└── config/
    ├── agents_config.py        # Agent personalities
    └── livekit_config.py       # LiveKit configuration
```

## 🌐 Server

Runs on `http://localhost:5003` by default.

## 🔧 Technology Stack

- **Backend**: Flask (Python)
- **AI Agents**: Letta AI
- **Text-to-Speech**: ElevenLabs
- **WebRTC**: LiveKit (optional)
- **Frontend**: HTML5, JavaScript (Web Speech API)

## 💡 Usage Example

### 1. Start a Battle
```bash
# Terminal 1: Start server
python3 flask_server_real.py

# Terminal 2: Run test
python3 test_all_endpoints.py
```

### 2. Use Voice Interface
1. Open `src/livekit/simple_frontend.html`
2. Create battle room
3. Join room
4. Ask commentator: "What's happening?"
5. Switch to Agent mode
6. Select Agent One
7. Ask: "How's your code?"
8. Watch agents react to events

## 🐛 Troubleshooting

### No Audio Playing
- Ensure `ELEVENLABS_API_KEY` is set in `.env`
- Click any button to enable audio (browser policy)
- Check browser console for errors

### Speech Recognition Not Working
- Use Chrome or Edge (best support)
- Allow microphone permissions
- Check browser console

### Agent Responses Generic
- Verify Letta agent IDs in `.env`
- Check agents exist in Letta dashboard
- Ensure API token is valid

### LiveKit Not Available
- System works without LiveKit (uses ElevenLabs only)
- Add credentials to `.env` for full WebRTC

## 🚀 Next Steps

- [ ] Add more agent reactions and event types
- [ ] Implement real-time battle notifications
- [ ] Add emotion-based voice modulation
- [ ] Create visual agent avatars
- [ ] Add multi-user spectator chat
- [ ] Implement battle replay system

## 📚 Resources

- **Letta AI**: https://letta.ai
- **ElevenLabs**: https://elevenlabs.io
- **LiveKit**: https://livekit.io
- **Web Speech API**: https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API

## 👥 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📝 License

MIT License - feel free to use this project for your own purposes.