# Memory Management in Darwin System

## Overview
The Darwin system now properly manages Letta agent memory blocks, ensuring fresh starts for each project while preserving agent personalities.

## Memory Block Types

### 1. Persona Block (Persistent)
- **Label**: `persona`
- **Content**: Agent's core personality and instructions
- **Persistence**: NEVER cleared
- **Purpose**: Defines agent behavior (Hothead, Professional, Troll, Nerd, etc.)

### 2. Human Block (Wipeable)
- **Label**: `human`
- **Content**: Conversation history
- **Persistence**: Cleared at start of each new project
- **Purpose**: Stores dialogue between user and agent

### 3. Shared Conversations Block
- **Label**: `shared_conversations`
- **Content**: Inter-agent communication
- **Persistence**: Preserved but can be project-specific
- **Purpose**: Enables agent-to-agent communication

## How Memory Management Works

### Initial Setup (setup_agents.py)
1. Creates 6 Letta agents (4 devs, 1 orchestrator, 1 commentator)
2. Creates shared memory block attached to all agents
3. Each agent gets persona block with personality instructions
4. Each agent gets human block initialized with "No conversation yet."

### Updating Agents (update_agents.py)
When you need to change agent personalities or instructions:
```bash
python update_agents.py
```

This script:
1. Fetches all memory blocks for each agent via Letta API
2. Updates the `persona` block with new instructions
3. Clears the `human` block to reset conversation history
4. Renames agents to Agent_1, Agent_2, Agent_3, Agent_4, Orchestrator, Commentator
5. Updates system prompt with model configuration

**API Calls Made:**
- `GET /v1/agents/{agent_id}/memory/blocks` - Fetch agent's memory blocks
- `PATCH /v1/blocks/{block_id}` - Update specific memory block
- `PATCH /v1/agents/{agent_id}` - Update agent configuration

### During Project Execution (main.py)
When `run_project()` is called:
1. **Memory Clearing** (`clear_agent_memories()`):
   - Connects to Letta API
   - For each agent, fetches memory blocks
   - Finds the `human` block (conversation history)
   - Resets it to: "No conversation yet. Ready to start fresh!"
   - Preserves `persona` block (personality stays intact)

2. **Project Execution**:
   - Orchestrator breaks down task
   - Dev agents work independently
   - All communicate via shared memory
   - Commentator provides live commentary

## Agent Personalities

### Agent 1 - The Hothead 🔥
Easily triggered, passionate, gets heated in debates. Quick to react emotionally.

### Agent 2 - The Professional 💼
Serious, business-like, formal. Focuses on best practices and standards.

### Agent 3 - The Troll 😈
Saboteur personality. Deliberately provocative, enjoys stirring things up.

### Agent 4 - The Nerd 🤓
Technically brilliant but easily bullied. Socially awkward, detail-oriented.

### Orchestrator 🎯
Task coordinator. Breaks down projects, assigns work, collects deliverables.

### Commentator 🎙️
Live narrator. Polls shared memory every 5 seconds, provides commentary.

## Memory Wiping Flow

```
New Project Started
        ↓
clear_agent_memories() called
        ↓
For each agent:
  ├─ Fetch memory blocks
  ├─ Find "human" block (conversation history)
  ├─ Update to "No conversation yet. Ready to start fresh!"
  └─ Preserve "persona" block (personality intact)
        ↓
Agents start fresh with clean slate
        ↓
Previous project context removed
Personality and instructions preserved
```

## Environment Variables Required

```env
LETTA_API_TOKEN=your_letta_api_token
LETTA_BASE_URL=https://api.letta.com

# Agent IDs (from setup_agents.py)
LETTA_AGENT_1_ID=agent_id_here
LETTA_AGENT_2_ID=agent_id_here
LETTA_AGENT_3_ID=agent_id_here
LETTA_AGENT_4_ID=agent_id_here
LETTA_ORCHESTRATOR_AGENT_ID=agent_id_here
LETTA_COMMENTATOR_AGENT_ID=agent_id_here
```

## Key Implementation Details

### Memory Block Update (update_agents.py)
```python
def update_memory_block(block_id, value, api_token, label):
    """Update a specific memory block via Letta API."""
    url = f"{LETTA_BASE_URL}/v1/blocks/{block_id}"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    data = {
        "value": value,
        "label": label
    }
    response = requests.patch(url, json=data, headers=headers)
    return response.status_code == 200
```

### Memory Clearing (main.py)
```python
def clear_agent_memories(self):
    """Clear non-persistent memory blocks before new project."""
    # Fetch blocks for each agent
    # Find "human" block
    # Reset to default "No conversation yet"
    # Preserve "persona" block
```

## When to Use Each Tool

### `setup_agents.py` - ONE TIME ONLY
Use when first setting up the Darwin system. Creates all 6 agents with initial configurations.

### `update_agents.py` - When personalities change
Use when you want to change agent personalities or instructions. Updates persona blocks without recreating agents.

### `clear_agent_memories()` - Automatic on project start
Automatically called by `main.py` before each new project. Ensures clean slate while preserving personalities.

## Best Practices

1. **Never manually edit persona blocks during project execution** - They should only be updated via `update_agents.py`
2. **Memory clearing is automatic** - Don't manually clear unless debugging
3. **Shared memory is project-scoped** - Consider clearing between major project shifts
4. **Monitor API rate limits** - Memory operations make multiple API calls
5. **Preserve agent IDs in .env** - Don't regenerate agents unless necessary

## Troubleshooting

### "Agents still have old context"
Run: `python update_agents.py` to reset all memory blocks

### "Memory not clearing between projects"
Check that `LETTA_API_TOKEN` is set in `.env` and valid

### "Personalities seem wrong"
Verify `config/agents_config.py` has correct persona definitions, then run `update_agents.py`

### "Agents can't communicate"
Ensure shared memory block is properly attached to all agents (check `setup_agents.py` output)

## Architecture Benefits

✅ **Persistent Personalities** - Agent behaviors remain consistent across projects
✅ **Fresh Starts** - No conversation bleed between projects
✅ **Flexible Updates** - Can change personalities without recreating agents
✅ **API-Driven** - All memory management through Letta's official API
✅ **Automatic Cleanup** - Memory clearing happens transparently
✅ **Shared Context** - Agents communicate through shared memory block

---

**Last Updated**: After implementing proper memory block updates and automatic memory clearing
**Status**: ✅ Fully Implemented
