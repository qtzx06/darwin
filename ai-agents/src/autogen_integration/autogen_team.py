"""
AutoGen Team Wrapper for Darwin Project
Manages a team of AutoGen agents that collaborate on subtasks
"""
import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

try:
    from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
except ImportError:
    # Silently handle missing pyautogen - system will use mock AutoGen
    AssistantAgent = None
    UserProxyAgent = None
    GroupChat = None
    GroupChatManager = None


class AutoGenTeamWrapper:
    """
    Wraps an AutoGen team (multiple agents in group chat) for use by Letta dev agents.
    Manages conversation, code generation, and result extraction.
    """
    
    def __init__(
        self, 
        team_id: str,
        team_name: str,
        specialization: str,
        team_number: int = 1,  # NEW: Which team (1-4) for API key selection
        work_dir: str = "workspace",
        silent: bool = True,  # Silence all non-essential output
        personality: str = ""  # PM personality to match
    ):
        self.team_id = team_id
        self.team_name = team_name
        self.specialization = specialization
        self.team_number = team_number
        self.work_dir = Path(work_dir) / team_id
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.silent = silent
        self.personality = personality
        
        # LLM configuration
        self.llm_config = self._get_llm_config()
        
        # Initialize AutoGen agents
        self._init_autogen_agents()
        
        # Conversation history
        self.conversation_history = []
        
        # Live conversation file
        self.live_dir = Path("live/conversations")
        self.live_dir.mkdir(parents=True, exist_ok=True)
        self.live_conversation_file = self.live_dir / f"{team_id}_live.txt"
        
    def _get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration for AutoGen agents."""
        config_list = []
        
        # Option 1: Google Gemini (FREE! 🎉) - Team-specific keys
        gemini_key = os.getenv(f"GOOGLE_API_KEY_TEAM{self.team_number}")
        if gemini_key:
            model = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")  # or gemini-1.5-flash
            config_list.append({
                "model": model,
                "api_key": gemini_key,
                "api_type": "google",
            })
            if not self.silent:
                print(f"✅ {self.team_name}: Using {model} with Team {self.team_number} key (FREE!)")
        
        # Option 2: Anthropic Claude (Sonnet, Haiku, Opus)
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
            config_list.append({
                "model": model,
                "api_key": anthropic_key,
                "api_type": "anthropic",
            })
            if not gemini_key and not self.silent:  # Only print if not using Gemini
                print(f"✅ {self.team_name}: Using {model}")
        
        # Option 3: OpenAI (GPT-4, GPT-3.5, GPT-4o)
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            model = os.getenv("OPENAI_MODEL", "gpt-4")
            config_list.append({
                "model": model,
                "api_key": openai_key,
                "api_type": "openai",
            })
            if not gemini_key and not anthropic_key and not self.silent:
                print(f"✅ {self.team_name}: Using {model}")
        
        # Option 4: Azure OpenAI
        azure_key = os.getenv("AZURE_OPENAI_API_KEY")
        if azure_key:
            config_list.append({
                "model": os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4"),
                "api_key": azure_key,
                "api_type": "azure",
                "base_url": os.getenv("AZURE_OPENAI_ENDPOINT"),
                "api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
            })
        
        if not config_list:
            if not self.silent:
                print(f"⚠️ {self.team_name}: No API keys found")
                print(f"   Set one of: GOOGLE_API_KEY, ANTHROPIC_API_KEY, OPENAI_API_KEY")
            return {"config_list": []}
        
        return {
            "config_list": config_list,
            "temperature": 0.7,
            "timeout": 120,
        }
    
    def _init_autogen_agents(self):
        """Initialize the AutoGen agents for this team."""
        if not AssistantAgent:
            if not self.silent:
                print("Warning: AutoGen not available")
            self.planner = None
            self.coder = None
            self.critic = None
            self.user_proxy = None
            self.groupchat = None
            self.manager = None
            return
        
        # Get personality style for agent messages
        personality_note = f"\n\nTEAM PERSONALITY:\n{self.personality}" if self.personality else ""
        
        # Create specialized agents based on team focus
        self.planner = AssistantAgent(
            name=f"{self.team_name}_Planner",
            system_message=f"""You are a planning specialist for {self.team_name}.
Your role: Break down tasks, suggest approaches, coordinate the team.
Be concise and practical.{personality_note}""",
            llm_config=self.llm_config
        )
        
        self.coder = AssistantAgent(
            name=f"{self.team_name}_Coder",
            system_message=f"""You are a coding specialist for {self.team_name}.
Your role: Write clean, efficient code following best practices.
Focus on practical, working solutions.{personality_note}""",
            llm_config=self.llm_config
        )
        
        self.critic = AssistantAgent(
            name=f"{self.team_name}_Critic",
            system_message=f"""You are a code reviewer for {self.team_name}.
Your role: Review code, suggest improvements, ensure quality.
Be constructive and specific.{personality_note}""",
            llm_config=self.llm_config
        )
        
        # User proxy for code execution
        self.user_proxy = UserProxyAgent(
            name=f"{self.team_name}_Executor",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config={
                "work_dir": str(self.work_dir),
                "use_docker": False,  # Set to True for safer execution
            }
        )
        
        # Create group chat
        self.groupchat = GroupChat(
            agents=[self.planner, self.coder, self.critic, self.user_proxy],
            messages=[],
            max_round=15,
            speaker_selection_method="auto"
        )
        
        self.manager = GroupChatManager(
            groupchat=self.groupchat,
            llm_config=self.llm_config
        )
    
    async def solve_subtask(
        self, 
        subtask_description: str,
        existing_codebase: str = "",
        user_feedback: str = "",
        context: Dict[str, Any] = None,
        live_feed = None,  # NEW: Live feed for real-time updates
        agent_name: str = "",  # NEW: For live feed identification
        agent_id: str = "",  # NEW: For live feed identification
        subtask_id: int = 0  # NEW: For file naming
    ) -> Dict[str, Any]:
        """
        Have the AutoGen team solve a subtask.
        Returns solution, conversation, and metadata.
        Publishes live updates if live_feed provided.
        """
        # Initialize live conversation file
        self._init_live_conversation_file(subtask_id, agent_name)
        
        if not self.manager:
            # Fallback if AutoGen not available
            return self._mock_solution(subtask_description)
        
        # Build comprehensive prompt
        prompt = self._build_prompt(
            subtask_description, 
            existing_codebase, 
            user_feedback,
            context or {}
        )
        
        # Run the conversation in executor to avoid blocking
        loop = asyncio.get_event_loop()
        chat_result = await loop.run_in_executor(
            None,
            lambda: self.user_proxy.initiate_chat(
                self.manager,
                message=prompt
            )
        )
        
        # Extract results
        conversation = self._extract_conversation()
        solution = self._extract_solution()
        code = self._extract_code(conversation)
        
        # Write final conversation to live file
        for msg in conversation:
            self._append_to_live_conversation(msg.get("speaker", "Unknown"), msg.get("content", ""))
        
        return {
            "team_id": self.team_id,
            "team_name": self.team_name,
            "subtask": subtask_description,
            "conversation": conversation,
            "solution": solution,
            "code": code,
            "message_count": len(conversation),
            "timestamp": datetime.now().isoformat()
        }
    
    def _build_prompt(
        self,
        subtask: str,
        existing_code: str,
        feedback: str,
        context: Dict[str, Any]
    ) -> str:
        """Build the prompt for the AutoGen team."""
        prompt_parts = [
            f"Team: {self.team_name}",
            f"Specialization: {self.specialization}",
            f"\n🎯 CURRENT SUBTASK:\n{subtask}",
            f"\n⚠️ CRITICAL REQUIREMENT:",
            f"You MUST produce a VISUAL artifact - something the user can SEE.",
            f"Output must be:",
            f"  - Complete HTML file with styling",
            f"  - Interactive React component",
            f"  - SVG visualization",
            f"  - Canvas animation",
            f"  - Or similar visual output",
            f"\nNO plain code explanations. NO console logs. VISUAL OUTPUT ONLY.",
            f"The user needs to see your work rendered in a browser!",
        ]
        
        if existing_code:
            prompt_parts.append(f"\nEXISTING CODEBASE:\n```\n{existing_code}\n```")
            prompt_parts.append("\nIMPORTANT: Build upon this existing code. Do not start from scratch.")
        
        if feedback:
            prompt_parts.append(f"\nUSER FEEDBACK FROM PREVIOUS SUBTASK:\n{feedback}")
            prompt_parts.append("\nApply this feedback to improve your approach.")
        
        if context.get("global_learnings"):
            learnings = context["global_learnings"]
            prompt_parts.append(f"\nLEARNINGS FROM PREVIOUS WORK:\n{json.dumps(learnings, indent=2)}")
        
        prompt_parts.append("\n✅ DELIVERABLE: Complete, working HTML/React/SVG that can be rendered visually.")
        prompt_parts.append("Work together to create the best solution. When complete, end with TERMINATE.")
        
        return "\n".join(prompt_parts)
    
    def _extract_conversation(self) -> List[Dict[str, str]]:
        """Extract formatted conversation from group chat."""
        if not self.groupchat:
            return []
        
        conversation = []
        for msg in self.groupchat.messages:
            conversation.append({
                "speaker": msg.get("name", "Unknown"),
                "role": msg.get("role", ""),
                "content": msg.get("content", ""),
                "timestamp": datetime.now().isoformat()
            })
        
        return conversation
    
    def _extract_solution(self) -> str:
        """Extract the final solution summary from conversation."""
        if not self.groupchat or not self.groupchat.messages:
            return "No solution generated"
        
        # Get last few messages as solution
        last_messages = self.groupchat.messages[-3:]
        solution_parts = []
        
        for msg in last_messages:
            content = msg.get("content", "")
            if content and "TERMINATE" not in content:
                solution_parts.append(f"{msg.get('name', 'Agent')}: {content}")
        
        return "\n\n".join(solution_parts) if solution_parts else "Solution completed"
    
    def _extract_code(self, conversation: List[Dict[str, str]]) -> str:
        """Extract all code blocks from the conversation."""
        import re
        
        code_blocks = []
        for msg in conversation:
            content = msg.get("content", "")
            # Find code blocks between ```
            blocks = re.findall(r'```(?:\w+)?\n(.*?)```', content, re.DOTALL)
            code_blocks.extend(blocks)
        
        # Return the most recent/complete code block
        return code_blocks[-1] if code_blocks else ""
    
    def _init_live_conversation_file(self, subtask_id: int, agent_name: str):
        """Initialize the live conversation file for streaming updates."""
        try:
            self.live_conversation_file = self.live_dir / f"{self.team_id}_subtask{subtask_id}.txt"
            with open(self.live_conversation_file, 'w', encoding='utf-8') as f:
                f.write(f"{'='*70}\n")
                f.write(f"{agent_name} - LIVE CONVERSATION\n")
                f.write(f"Subtask {subtask_id} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*70}\n\n")
        except Exception as e:
            pass  # Silently handle errors
    
    def _append_to_live_conversation(self, speaker: str, content: str):
        """Append a message to the live conversation file in real-time."""
        try:
            if hasattr(self, 'live_conversation_file'):
                timestamp = datetime.now().strftime("%H:%M:%S")
                with open(self.live_conversation_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{timestamp}] {speaker}:\n")
                    f.write(f"{content}\n\n")
        except Exception as e:
            pass  # Silently handle errors
    
    def _mock_solution(self, subtask: str) -> Dict[str, Any]:
        """Fallback mock solution when AutoGen is not available."""
        return {
            "team_id": self.team_id,
            "team_name": self.team_name,
            "subtask": subtask,
            "conversation": [
                {
                    "speaker": "Mock_Planner",
                    "content": f"Planning approach for: {subtask}",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "speaker": "Mock_Coder",
                    "content": f"Implementing solution with focus on {self.specialization}",
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "solution": f"Mock solution for {subtask}",
            "code": "// Mock code generated",
            "message_count": 2,
            "timestamp": datetime.now().isoformat()
        }
    
    def save_conversation(self, filepath: str):
        """Save conversation to JSON file."""
        if not self.groupchat:
            return
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump({
                "team_id": self.team_id,
                "team_name": self.team_name,
                "messages": self.groupchat.messages,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)
