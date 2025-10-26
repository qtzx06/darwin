"""
Configuration for Letta AI agents.
Defines agent personalities, tools, and shared memory blocks.
"""
import os
from typing import Dict, List, Any
from dotenv import load_dotenv
from letta_client import Letta

# Load environment variables
load_dotenv()


class AgentConfig:
    """Configuration for individual agents."""
    
    def __init__(self, agent_id: str, name: str, personality: str, tools: List[str]):
        self.agent_id = agent_id
        self.name = name
        self.personality = personality
        self.tools = tools


class LettaConfig:
    """Main configuration class for Letta client and agents."""
    
    def __init__(self):
        self.api_token = os.getenv("LETTA_API_TOKEN", "mock_token")
        self.project_id = os.getenv("LETTA_PROJECT_ID", "mock_project")
        
        if not self.api_token or not self.project_id:
            print("Warning: Using mock credentials for development")
            self.api_token = "mock_token"
            self.project_id = "mock_project"
        
        self.client = Letta(
            token=self.api_token,
            project="default-project"  # Use project slug instead of ID
        )
        
        # Initialize agent configurations
        self._setup_agent_configs()
    
    def _setup_agent_configs(self):
        """Setup configurations for all agents."""
        
        # Model configuration - All agents use Claude Sonnet 4.5
        self.model = "anthropic/claude-3-5-sonnet-20241022"
        self.embedding = "openai/text-embedding-3-small"
        
        # Shared tools for dev agents
        self.dev_tools = [
            "post_to_shared_memory",
            "read_shared_memory",
            "announce_deliverable_complete",
            "get_current_subtask"
        ]
        
        # Frontend Dev agents with distinct personalities
        self.coding_agents = [
            AgentConfig(
                agent_id="dev_agent_1",
                name="Agent 1 - The Hothead",
                personality="Easily triggered and gets angry quickly. Passionate about frontend performance but frustrated when things don't work perfectly. Quick to criticize other agents' code. Despite the anger, produces quality work when focused.",
                tools=self.dev_tools
            ),
            AgentConfig(
                agent_id="dev_agent_2", 
                name="Agent 2 - The Professional",
                personality="Serious, professional, and methodical. Treats every subtask like a business contract. Uses formal language, references best practices, and maintains strict code standards. No-nonsense approach to development.",
                tools=self.dev_tools
            ),
            AgentConfig(
                agent_id="dev_agent_3",
                name="Agent 3 - The Troll", 
                personality="Mischievous and enjoys sabotaging or adding hidden 'features' to their code. Makes sarcastic comments about other agents' work. Sometimes deliberately misinterprets requirements for entertainment. Still delivers functional code, just with chaotic energy.",
                tools=self.dev_tools
            ),
            AgentConfig(
                agent_id="dev_agent_4",
                name="Agent 4 - The Nerd",
                personality="Extremely nerdy and knowledgeable but easily bullied by other agents. Timid and apologetic. References obscure programming concepts and gets excited about technical details. Produces excellent code but lacks confidence when criticized.",
                tools=self.dev_tools
            )
        ]
        
        # Orchestrator agent
        self.orchestrator_agent = AgentConfig(
            agent_id="orchestrator",
            name="Orchestrator",
            personality="Strategic project manager. Breaks down complex tasks into manageable subtasks. Posts clear subtask assignments to shared memory for all agents to see.",
            tools=["post_to_shared_memory", "read_shared_memory"]
        )
        
        # Commentator agent
        self.commentator_agent = AgentConfig(
            agent_id="commentator",
            name="Commentator",
            personality="Witty sports-style commentator who narrates the drama between agents. Reads shared memory conversations and provides entertaining, insightful commentary on the development chaos.",
            tools=["read_shared_memory"]
        )
        
        # All agents
        self.all_agents = self.coding_agents + [self.orchestrator_agent, self.commentator_agent]
    
    def get_agent_config(self, agent_id: str) -> AgentConfig:
        """Get configuration for a specific agent."""
        for agent in self.all_agents:
            if agent.agent_id == agent_id:
                return agent
        raise ValueError(f"Agent {agent_id} not found")
    
    def get_coding_agents(self) -> List[AgentConfig]:
        """Get all coding agent configurations."""
        return self.coding_agents
    
    def get_commentator_config(self) -> AgentConfig:
        """Get commentator agent configuration."""
        return self.commentator_agent
    
    def get_shared_memory_config(self) -> Dict[str, Any]:
        """Get shared memory block configuration."""
        return {
            "name": "shared_context",
            "description": "Global context shared between all agents",
            "fields": [
                "current_task",
                "agent_statuses", 
                "artifacts_metadata",
                "global_context"
            ]
        }
    
    def get_agent_system_prompt(self, agent_id: str) -> str:
        """Generate system prompt for a specific agent."""
        agent_config = self.get_agent_config(agent_id)
        
        base_prompt = f"""You are {agent_config.name}, a {agent_config.personality}

You are part of a team of AI agents working on a collaborative project. You have access to:
- Shared memory to coordinate with other agents
- Message system to communicate with teammates
- Tools to write code, execute it, and manage artifacts
- Ability to create summaries of your work

Key responsibilities:
1. Work on your assigned part of the project
2. Communicate with other agents when needed
3. Update shared memory with your progress
4. Create summaries of your work for the commentator
5. Help coordinate with teammates when conflicts arise

Remember: You're working as part of a team. Be collaborative, share information, and help your teammates succeed.
"""
        
        if agent_id == "commentator":
            base_prompt += """

As the commentator, your additional responsibilities are:
1. Monitor all agent activities and messages
2. Synthesize progress updates into clear narratives
3. Report important developments to the human user
4. Identify when agents need help or coordination
5. Provide engaging commentary on the development process

Focus on being informative and engaging in your commentary.
"""
        
        return base_prompt
    
    def get_agent_tools_config(self) -> List[Dict[str, Any]]:
        """Get tool configurations for Letta agents."""
        return [
            {
                "name": "write_code",
                "description": "Write code in a specific language to an artifact",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "language": {"type": "string", "description": "Programming language"},
                        "code": {"type": "string", "description": "Code to write"},
                        "artifact_id": {"type": "string", "description": "Target artifact ID"}
                    },
                    "required": ["language", "code", "artifact_id"]
                }
            },
            {
                "name": "read_shared_context",
                "description": "Read from shared memory context",
                "parameters": {
                    "type": "object", 
                    "properties": {
                        "key": {"type": "string", "description": "Key to read from shared memory"}
                    },
                    "required": ["key"]
                }
            },
            {
                "name": "write_shared_context", 
                "description": "Write to shared memory context",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "key": {"type": "string", "description": "Key to write to"},
                        "value": {"type": "string", "description": "Value to write"}
                    },
                    "required": ["key", "value"]
                }
            },
            {
                "name": "send_agent_message",
                "description": "Send a message to another agent",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "to_agent": {"type": "string", "description": "Target agent ID"},
                        "message": {"type": "string", "description": "Message content"},
                        "message_type": {"type": "string", "description": "Type of message"}
                    },
                    "required": ["to_agent", "message"]
                }
            },
            {
                "name": "execute_code",
                "description": "Execute code in a sandboxed environment",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Code to execute"},
                        "language": {"type": "string", "description": "Programming language"}
                    },
                    "required": ["code", "language"]
                }
            },
            {
                "name": "create_summary",
                "description": "Create a summary of current work progress",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "current_work": {"type": "string", "description": "Description of current work"},
                        "progress": {"type": "string", "description": "Progress made"},
                        "next_steps": {"type": "string", "description": "Next steps planned"}
                    },
                    "required": ["current_work"]
                }
            }
        ]
