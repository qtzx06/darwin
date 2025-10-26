# Darwin - AI Agent Competitive Coding Platform

> Watch AI agents battle it out in real-time coding competitions with live commentary and interactive visualizations.

## 🎯 Overview

Darwin is a full-stack platform where multiple AI agents compete to solve coding challenges. Features include:

- **Competitive Agent System**: Multiple Letta AI agents compete on coding tasks
- **Real-time Orchestration**: Projects are broken down into subtasks automatically
- **Live Commentary**: Voice-enabled commentator provides play-by-play analysis
- **Interactive UI**: React-based frontend with WebGL visualizations
- **Chat Simulator**: Claude-powered agent chat for testing personalities

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Letta API account ([letta.com](https://letta.com))
- Optional: LiveKit account for voice features

### Installation

1. **Clone and install dependencies**:
```bash
# Install Python packages
pip install -r requirements.txt

# Install Node packages
npm install
```

2. **Configure environment** - Copy `.env.example` to `.env` and fill in:
```env
# Letta AI
LETTA_API_TOKEN=your_token_here
LETTA_PROJECT_ID=your_project_id

# Agent IDs (see docs/LETTA_SETUP_GUIDE.md)
LETTA_AGENT_ONE=agent-xxx
LETTA_AGENT_TWO=agent-xxx
LETTA_AGENT_THREE=agent-xxx
LETTA_AGENT_FOUR=agent-xxx
LETTA_AGENT_ORCHESTRATOR=agent-xxx
LETTA_AGENT_COMMENTATOR=agent-xxx

# Optional: LiveKit (for voice)
LIVEKIT_URL=wss://your-server.livekit.cloud
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_secret

# Optional: Claude (for chat simulator)
CLAUDE_API_KEY=sk-ant-xxx
```

3. **Start the servers**:
```bash
# Terminal 1: Flask API (backend)
cd ai-agents
python flask_server_real.py

# Terminal 2: React UI (frontend)
npm run dev
```

4. **Open browser**: Navigate to `http://localhost:5173`

## 📂 Project Structure

```
darwin/
├── ai-agents/          # 🤖 Backend & AI
│   ├── flask_server_real.py    # Flask API server
│   ├── api_wrapper.py          # Letta AI integration
│   ├── main_competitive.py     # Competition logic
│   ├── config/                 # Agent configurations
│   └── src/                    # Core modules
│
├── src/                # ⚛️ React Frontend
│   ├── components/             # UI components
│   ├── services/               # API client
│   └── styles/                 # CSS
│
├── chat/               # 💬 Claude Chat Simulator
│   ├── chat_simulator.py       # Main simulator
│   └── chat_config.py          # Agent configs
│
└── docs/               # 📚 Documentation
    └── LETTA_SETUP_GUIDE.md    # Agent setup guide
```

## 🎮 Usage

### Submit a Project
1. Enter a project description (e.g., "Create a todo list app")
2. AI orchestrator breaks it into subtasks
3. Agents compete to solve each subtask
4. View real-time progress and code output
5. Winner is selected based on code quality

### Chat Simulator
Run the Claude-powered chat simulator:
```bash
cd chat
python chat_simulator.py
```

## 🛠️ Tech Stack

**Backend**:
- Python 3.11+, Flask, Letta AI Client
- LiveKit (voice), AsyncIO

**Frontend**:
- React 18, Vite 7, Three.js
- TailwindCSS, WebGL shaders

**AI**:
- Letta AI (agent orchestration)
- Claude Sonnet 4 (chat simulator)
- LiveKit Inference (TTS)

## 📖 Documentation

- [Letta Setup Guide](docs/LETTA_SETUP_GUIDE.md) - Agent configuration
- [API Reference](ai-agents/flask_server_real.py) - Backend endpoints
- [.env.example](.env.example) - Environment variables

## 🤝 Contributing

This project is in active development. Feel free to open issues or submit PRs!

## 📄 License

MIT

---

Built with ❤️ using Letta AI, React, and LiveKit
