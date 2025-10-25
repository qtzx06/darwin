# Letta AI Agent PM Simulator

A project management simulator powered by Letta AI agents that work collaboratively on tasks with shared memory and real-time commentary.

## Architecture

- **4 Coding Agents**: Work on different aspects of a project with shared tooling
- **1 Commentator Agent**: Monitors and narrates the development process
- **Shared Memory**: Global context accessible by all agents
- **Message System**: Agent-to-agent communication with history
- **Artifact Management**: Track and render each agent's work

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure Letta Cloud credentials:
   ```bash
   cp .env.example .env
   # Edit .env with your Letta API token and project ID
   ```

3. Run the simulator:
   ```bash
   python main.py
   ```

## Usage

### Quick Demo (Recommended)
See real Letta agents working together:
```bash
python3 test_real_agents_demo.py
```

### Full PM Simulator
```bash
python3 main.py
```
Enter a high-level task description when prompted. The system will:
1. Distribute work across 4 coding agents
2. Allow agents to communicate and coordinate
3. Provide real-time commentary via the commentator agent
4. Display artifacts and progress updates

### Setup Real Letta Agents
If you haven't created agents yet:
```bash
python3 fix_letta_integration.py
```

For detailed testing instructions, see [TESTING.md](TESTING.md).

## Future Enhancements

- MCP integration for sandboxed code execution
- LiveKit integration for voice narration
- Web UI for artifact visualization
- Agent personality customization
