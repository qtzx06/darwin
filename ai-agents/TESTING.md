# Testing the Letta AI Agent PM Simulator

## Quick Start

### 1. **Real Agent Demo** (Recommended)
See your real Letta agents working together:

```bash
cd ai-agents
source venv/bin/activate
python3 test_real_agents_demo.py
```

This demonstrates:
- Frontend Specialist creating React components
- Backend Architect building Node.js APIs  
- Project Narrator providing intelligent commentary

### 2. **Full PM Simulator**
Run the complete simulator with real-time display:

```bash
cd ai-agents
source venv/bin/activate
python3 main.py
```

### 3. **View Logs**
View detailed logs of agent activities:

```bash
cd ai-agents
source venv/bin/activate
python3 view_logs.py
```

### 4. **Watch Logs in Real-Time**
Monitor logs as they're created:

```bash
tail -f logs/pm_simulator_*.log
```

Enter a project description when prompted, e.g.:
- "Build a React-based task management application"
- "Create a Python web scraper with API"
- "Design a mobile app for expense tracking"

## What You'll See

### Real Agent Demo
- **Frontend Specialist**: Complete React component with styling
- **Backend Architect**: Full Node.js API with error handling
- **Project Narrator**: Intelligent progress summary and next steps

### Full Simulator
- **Live Display**: Real-time agent status and progress
- **Agent Communication**: Messages between agents
- **Artifact Tracking**: Code and outputs from each agent
- **Commentary**: Live narration of what's happening
- **Comprehensive Logging**: Detailed logs of all agent activities

### Log Files
- **Text Log**: `logs/pm_simulator_YYYYMMDD_HHMMSS.log` - Detailed activity log
- **Session Data**: `logs/session_YYYYMMDD_HHMMSS.json` - Structured session data
- **Log Viewer**: `python3 view_logs.py` - Beautiful log visualization

## Requirements

- Python 3.10+
- Virtual environment activated
- Letta API credentials in `.env` file
- Real Letta agents created (run `python3 fix_letta_integration.py` first)

## Troubleshooting

**"No module named 'letta_client'"**
```bash
source venv/bin/activate
pip install letta-client
```

**"Missing agent IDs"**
```bash
python3 fix_letta_integration.py
```

**"Project not found"**
- Check your `.env` file has correct `LETTA_API_TOKEN`
- Ensure you have a Letta Cloud account

## Success Indicators

✅ Agents respond with detailed, specialized solutions  
✅ Frontend creates complete React components  
✅ Backend builds full APIs with error handling  
✅ Narrator provides intelligent progress updates  
✅ All agents maintain context across messages  

## Next Steps

Once testing is successful, you can:
- Add more specialized agents
- Integrate with MCP servers for code execution
- Add LiveKit for voice commentary
- Build a web UI for better visualization
