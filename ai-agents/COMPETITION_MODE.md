# Competition Mode Usage

## New Features

### 1. No Welcome/Goodbye Messages
- Chat starts immediately without greeting
- Exits silently without goodbye message

### 2. Competition State
The simulator now has two modes:

**IDLE MODE** (default):
- Light banter between agents
- Waiting for Boss to give them a task
- Casual roasting

**ACTIVE COMPETITION MODE**:
- Activated by calling `await simulator.start_competition()`
- Agents RAMP UP trash talk significantly
- Constant flexing about their progress
- Aggressive roasting of others' approaches
- Trying hard to impress Boss

### 3. Progress Updates
Feed agent progress to Claude without requiring response:

```python
await simulator.add_agent_progress("Speedrunner", "Completed setup in 30 seconds")
```

These updates:
- Add context to Claude's memory
- Agents can reference them in conversation
- Used as ammunition for trash talk during competition
- Don't trigger immediate responses (natural timing)

## Example Usage

```python
from chat_simulator import ChatSimulator

simulator = ChatSimulator()

# Start simulator (no welcome message)
await simulator.start()

# After Boss gives a task, start competition
await simulator.start_competition()

# Feed progress updates as agents work
await simulator.add_agent_progress("Bloom", "Designed beautiful UI")
await simulator.add_agent_progress("Solver", "Optimized algorithm")

# Agents will trash talk based on these updates
```

## Running the Demo

```bash
python test_competition_mode.py
```

This shows:
1. Idle chat
2. Competition starting
3. Progress updates being fed
4. Agents ramping up trash talk based on progress

## Integration with Real Agents

When integrating with actual Letta agents:
1. Start chat simulator in background
2. When task is assigned to Letta agents, call `start_competition()`
3. As Letta agents make progress, call `add_agent_progress()` with their updates
4. Chat agents will react naturally to the progress being made
