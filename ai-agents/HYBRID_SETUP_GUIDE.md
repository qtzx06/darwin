# Darwin Hybrid System - Quick Start

## 🧬 Architecture

**Letta + AutoGen Hybrid**: 4 Letta dev agents (with memory/learning) each manage an AutoGen team (3 agents: Planner, Coder, Critic)

### How It Works

```
User gives project goal
        ↓
Orchestrator breaks into subtasks
        ↓
4 Letta Dev Agents (each managing AutoGen team)
        ↓
Each team competes on subtask
        ↓
Commentator presents results
        ↓
User gives feedback
        ↓
Feedback → Shared Memory (all agents learn)
        ↓
Next subtask (teams improve based on feedback)
        ↓
Repeat until project complete
```

## 📋 Required API Keys

### 1. Letta API Token
👉 https://cloud.letta.com → Create project → Get API token (`sk-let-xxx`)

### 2. LLM for AutoGen - 4 Team Keys (Gemini is FREE!)

**Option A: Google Gemini (FREE - Recommended)**
- 👉 https://aistudio.google.com/app/apikey
- **Get 4 API keys** (one for each competing team)
- Completely free, 1500 requests/day **per key** = 6,000 total!
- Add to `.env`:
  ```
  GOOGLE_API_KEY_TEAM1=your-key-1
  GOOGLE_API_KEY_TEAM2=your-key-2
  GOOGLE_API_KEY_TEAM3=your-key-3
  GOOGLE_API_KEY_TEAM4=your-key-4
  ```

**Why 4 keys?**
- Each team gets isolated 1,500 req/day limit
- Better parallel execution (no single key bottleneck)
- Track which team uses what
- Still 100% FREE!

**Alternative Options (if not using Gemini):**
- Anthropic Claude: $5 free credits → `ANTHROPIC_API_KEY=sk-ant-xxx`
- OpenAI: No free tier → `OPENAI_API_KEY=sk-xxx`

## � Quick Setup (5 minutes)

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Create `.env` File
```powershell
# Add your API tokens
LETTA_API_TOKEN=sk-let-xxx
GOOGLE_API_KEY=xxx  # Or ANTHROPIC_API_KEY or OPENAI_API_KEY
```

### 3. Create Letta Agents (ONE-TIME SETUP)
```powershell
python setup_hybrid_agents.py
```

**⚠️ Run this ONLY ONCE!**

This creates:
- 4 dev agents with **persistent memory blocks** (learn across projects)
- 1 orchestrator agent
- 1 commentator agent

Copy the 6 agent IDs to your `.env` file.

**Important:** The main system (`main_hybrid.py`) will **ONLY use existing agents** from `.env`. It will **NEVER create new agents** automatically. You have full control!

### 4. Run Darwin
```powershell
python main_hybrid.py
```

Enter your project goal:
- "Create an interactive 3D solar system website"
- "Build a React todo app"
- "Design a data dashboard"

### What Happens
1. Orchestrator breaks goal into subtasks
2. 4 teams compete on each subtask (AutoGen teams discuss internally)
3. Commentator narrates results
4. You give feedback
5. All agents learn from feedback
6. Repeat for next subtask

## 📁 Output Files

```
artifacts/
  subtask_1/
    raw/
      team_1_conversation.json  # Full AutoGen chat
      team_2_conversation.json
      ...
    summaries/
      team_1_summary.md         # Letta agent summary
      team_2_summary.md
      ...
    commentator_narrative.md    # User-facing story
  codebases/
    team_1_codebase.txt         # Growing code file
    team_2_codebase.txt
    ...
```

## ⚙️ Configuration

Edit `src/autogen_integration/autogen_team.py` to customize:
- Team composition (add more AutoGen agents)
- Specializations
- Max conversation rounds

## � Reset for New Projects

The system automatically resets agent memories between projects when you run `main_hybrid.py` in loop mode.

**Manual Reset (optional):**
```powershell
python reset_agents.py
```

This clears:
- ✓ All Letta agent memories
- ✓ Codebase files
- ✓ Shared memory state

Artifacts from old projects are preserved for review!

## �🐛 Troubleshooting

**"No API keys found"** → Set `GOOGLE_API_KEY` or `ANTHROPIC_API_KEY` in `.env`  
**"Missing agent IDs"** → Run `python setup_hybrid_agents.py`  
**Import errors** → Run `pip install -r requirements.txt`

## � More Info

- Old Letta-only setup: `LETTA_SETUP_GUIDE.md`
- Testing instructions: `TESTING.md`
- Main README: `README.md`

---

**Built with Letta + AutoGen** 🧬🤖
