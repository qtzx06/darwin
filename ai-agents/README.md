# Competitive AI Agents API

A Flask API for competitive AI agents that compete on coding tasks using real Letta AI integration.

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Create a `.env` file with:
   ```
   LETTA_API_TOKEN=your_token_here
   LETTA_PROJECT_ID=your_project_id
   LETTA_PROJECT_SLUG=your_project_slug
   LETTA_AGENT_ONE=agent_id_1
   LETTA_AGENT_TWO=agent_id_2
   LETTA_AGENT_THREE=agent_id_3
   LETTA_AGENT_FOUR=agent_id_4
   LETTA_AGENT_COMMENTATOR=commentator_id
   LETTA_AGENT_ORCHESTRATOR=orchestrator_id
   ```

3. **Start the server:**
   ```bash
   python3 flask_server_real.py
   ```

4. **Test the API:**
   ```bash
   python3 test_all_endpoints.py
   ```

## 📋 API Endpoints

### Core Workflow
- `POST /api/submit-project` - Submit project description
- `POST /api/create-agents` - Reset agent contexts
- `POST /api/start-work` - Start work phase
- `POST /api/get-results` - Send subtasks to agents
- `POST /api/retrieve-code` - Get actual generated code
- `POST /api/select-winner` - Select winning agent
- `POST /api/complete-round` - Complete round

### Additional Features
- `POST /api/get-commentary` - Get real-time commentary
- `POST /api/get-chat-summary` - Get chat summaries
- `POST /api/orchestrate-project` - Break down projects into subtasks
- `GET /api/health` - Health check
- `GET /api/agents` - Get agent information

## 🎯 Agent Personalities

- **One**: Sarcastic, clean code with humor
- **Two**: Technical perfectionist, over-engineered
- **Three**: Fast-paced, performance-focused
- **Four**: Creative, design-focused

## 🧪 Testing

Run the comprehensive test suite:
```bash
python3 test_all_endpoints.py
```

Run a quick demo:
```bash
python3 demo_code_outputs.py
```

## 📁 Project Structure

```
ai-agents/
├── flask_server_real.py    # Main Flask API server
├── api_wrapper.py          # API wrapper with all methods
├── main_competitive.py     # Core simulator
├── src/                    # Core modules
├── config/                 # Agent configurations
├── test_all_endpoints.py   # Comprehensive test suite
├── demo_code_outputs.py    # Working demo
└── requirements.txt       # Dependencies
```

## 🌐 Server

Runs on `http://localhost:5003` by default.