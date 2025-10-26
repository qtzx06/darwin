# Darwin System - Quick Start Guide

## 🎯 What Darwin Does

Darwin is a competitive AI development system where 4 Letta agents with distinct personalities work on frontend development tasks while a commentator narrates the chaos in real-time.

## 🤖 The Agents

### Development Agents (Frontend Developers)
1. **Agent 1 - The Hothead**: Easily triggered, passionate about performance, quick to anger
2. **Agent 2 - The Professional**: Serious, methodical, references best practices
3. **Agent 3 - The Troll**: Mischievous, adds Easter eggs, sabotages for fun
4. **Agent 4 - The Nerd**: Extremely knowledgeable but easily bullied

### Coordination Agents
5. **Orchestrator**: Breaks down your project into subtasks
6. **Commentator**: Provides live sports-style commentary every 5 seconds

All agents use **Claude Sonnet 4.5** (`anthropic/claude-3-5-sonnet-20241022`)

## 🚀 Setup (5 minutes)

### 1. Get Letta API Token
Visit https://cloud.letta.com
- Create an account
- Get your API token (starts with `sk-let-xxx`)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your LETTA_API_TOKEN
```

### 4. Create Agents (ONE-TIME ONLY)
```bash
python setup_agents.py
```

This creates 6 Letta agents and a shared memory block. **Copy the IDs to your .env file**.

⚠️ **Important**: Only run this ONCE! The agent IDs are permanent.

### 5. Run Darwin
```bash
python main.py
```

## 💬 How It Works

1. **You provide a frontend project goal**
   - Example: "Create an interactive 3D solar system"

2. **Orchestrator breaks it into 3-5 subtasks**
   - Posts each subtask to shared memory

3. **All 4 dev agents work independently**
   - They communicate through shared memory
   - Personalities clash and interact
   - Each builds their own deliverable

4. **Commentator narrates live (every 5 seconds)**
   - Reads shared memory conversations
   - Provides entertaining commentary

5. **You give feedback after each subtask**
   - Agents learn from your feedback via shared memory

6. **Repeat until project complete**

## 📦 Deliverables

Agents produce:
- **React components** (preferred)
- **HTML/CSS/JS files** (fallback)

Deliverables are saved to `artifacts/agent_<id>/` directories.

View them at: https://github.com/13point5/open-artifacts

## 🎙️ Live Commentary

Watch live commentary in real-time in your terminal as the system runs!
The commentator polls shared memory every 5 seconds and prints updates directly to the console.

## 📋 Example Project Goals

- "Create an interactive 3D solar system visualization"
- "Build a todo list app with drag-and-drop"
- "Design a data dashboard with real-time charts"
- "Make a portfolio website with scroll animations"
- "Create a weather app with animated backgrounds"

## 🔧 Troubleshooting

### "Missing dev agent IDs in .env"
- Run `python setup_agents.py` first
- Copy all 6 agent IDs to .env

### "LETTA_API_TOKEN not set"
- Get token from https://cloud.letta.com
- Add to .env file

### Agents not responding
- Check your Letta API token is valid
- Verify agent IDs exist in Letta Cloud
- Try re-running setup_agents.py if needed

## 🎨 Architecture

```
User Input
    ↓
Orchestrator (breaks into subtasks)
    ↓
Shared Memory (posts subtask)
    ↓
4 Dev Agents (work independently)
    ↓
Shared Memory (agents chat/argue)
    ↓
Commentator (reads & narrates)
    ↓
User Feedback
    ↓
Shared Memory (feedback posted)
    ↓
Next Subtask...
```

## 🔮 What Makes Darwin Unique

1. **Personality-Driven Development**: Agents have real personalities that clash
2. **Shared Memory Communication**: All conversations are chronological and visible
3. **Live Commentary**: Sports-style narration of the development process
4. **Competitive Approach**: 4 different solutions to each subtask
5. **Iterative Feedback**: User guides the direction after each step
6. **Pure Letta**: No AutoGen or other frameworks - just Letta agents

## 📁 Project Structure

```
ai-agents/
├── main.py                 # Main entry point
├── setup_agents.py         # One-time agent creation
├── src/
│   ├── agents/
│   │   ├── letta_dev_agent.py        # Dev agent implementation
│   │   ├── letta_orchestrator.py    # Orchestrator implementation
│   │   └── letta_commentator.py     # Commentator implementation
│   ├── core/
│   │   ├── shared_memory.py         # Shared memory system
│   │   └── message_system.py        # Message broker
│   └── tools/
│       └── shared_memory_tools.py   # Letta tools for agents
├── artifacts/              # Agent deliverables
├── live/                   # Live commentary feed
└── config/
    └── agents_config.py    # Agent configurations
```

## 🎯 Next Steps

After your first successful run:
- Experiment with different project goals
- Watch how agent personalities evolve
- Check the live commentary for entertaining interactions
- Review deliverables in `artifacts/` directory

Enjoy the chaos! 🎉
