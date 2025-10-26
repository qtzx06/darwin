# Darwin AI Frontend Development System

A competitive AI development system where 4 Letta agents with distinct personalities collaborate (and clash) on frontend development tasks with live commentary.

## Architecture

- **4 Frontend Dev Agents**: Independent Letta agents with unique personalities
  - Agent 1: The Hothead (easily triggered/angry)
  - Agent 2: The Professional (serious/formal)
  - Agent 3: The Troll (mischievous/saboteur)
  - Agent 4: The Nerd (smart but easily bullied)
- **1 Orchestrator Agent**: Breaks down tasks into subtasks, coordinates workflow
- **1 Commentator Agent**: Provides live commentary every 5 seconds
- **Shared Memory**: Chronological conversation log for agent communication
- **All agents use Claude Sonnet 4.5**

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure Letta Cloud credentials:
   ```bash
   cp .env.example .env
   # Edit .env with your Letta API token
   ```

3. Create agents (ONE-TIME SETUP):
   ```bash
   python setup_agents.py
   ```
   Copy the agent IDs to your .env file.

4. Run the system:
   ```bash
   python main.py
   ```

## Usage

When you run `python main.py`, you'll be prompted to enter a frontend development project goal.

Examples:
- "Create an interactive 3D solar system visualization"
- "Build a todo list app with drag-and-drop"
- "Design a data dashboard with charts"

The system will:
1. Break down your goal into 3-5 frontend subtasks
2. All 4 dev agents work independently on each subtask
3. Agents communicate through shared memory (with their personalities showing!)
4. Commentator provides live commentary every 5 seconds
5. You give feedback after each subtask
6. Deliverables are saved to `artifacts/` directory

## Deliverables

Agents produce:
- React components (preferred for open-artifacts)
- HTML/CSS/JS files (fallback)

View deliverables at: https://github.com/13point5/open-artifacts

## Future Enhancements

- Real-time artifact viewer
- Voice narration for commentator
- Agent personality customization
- Multi-agent voting system
