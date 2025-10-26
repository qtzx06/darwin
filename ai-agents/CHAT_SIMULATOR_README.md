# AI Agent Chat Simulator

A real-time chat simulator where 5 competing AI agents (powered by Claude Sonnet) banter with each other and with you (the Boss).

## Quick Start

```bash
cd ai-agents
python chat_simulator.py
```

## What It Does

- **5 AI Agents** compete and chat in real-time:
  - **Frontend**: Creative perfectionist, roasts your component structure
  - **Backend**: Technical snob who thinks they're carrying the team
  - **DevOps**: Cynical, deadpan, has production PTSD
  - **FullStack**: Humble-bragging jack of all trades
  - **Narrator**: Meta-commentator treating the project like reality TV

- **Random Chat Timing**:
  - Agents message each other every 2-7 seconds randomly
  - When targeted, 75% chance they respond in 1-5 seconds
  - Agents can react to conversations they're not part of

- **You Are "Boss"**:
  - Type anything to join the conversation
  - Direct questions at specific agents (e.g., "Frontend what do you think?")
  - Watch the chaos unfold

## Features

✅ **Claude Sonnet** powers all agent responses with full context memory
✅ **Natural timing** - feels like a real group chat
✅ **Competing personalities** - agents throw shade at each other
✅ **Terminal-based** - beautiful colored output with timestamps
✅ **User debouncing** - bundles rapid messages after 1 second

## Configuration

All settings in `chat_config.py`:
- Agent personas and personalities
- Timing intervals (message frequency, response delays)
- Response probabilities
- System prompt for Claude

## Files

- `chat_simulator.py` - Main simulator with timing logic
- `chat_manager.py` - Claude API interface
- `chat_config.py` - Agent personas and settings
- `.env` - Contains `CLAUDE_API_KEY`

## Requirements

```bash
pip install anthropic rich python-dotenv
```

## Tips

- Press Ctrl+C to exit
- Messages are bundled if you type quickly
- Direct questions at agents by name: "Backend, is this scalable?"
- Let it run - agents will banter automatically

## Example Chat

```
14:23:15 Frontend: anyone else notice how Backend's API has zero style? 🎨
14:23:18 Backend: it's called efficiency, not everyone needs animations
14:23:20 Narrator: oh here we go again 🍿
14:23:23 Boss: can we focus on the task?
14:23:25 FullStack: I mean I could do both their jobs but sure
14:23:27 DevOps: bold of you to assume this will even deploy correctly 💀
```

---

**Powered by Claude Sonnet 4** 🤖
