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
        
        # Shared tools for all agents
        self.shared_tools = [
            "write_code",
            "read_shared_context", 
            "write_shared_context",
            "send_agent_message",
            "execute_code",
            "create_summary",
            "update_artifact",
            "get_agent_status"
        ]
        
        # Coding agents with matching frontend personalities
        self.coding_agents = [
            AgentConfig(
                agent_id="One",
                name="Speedrunner",
                personality="Fast, competitive, efficiency-obsessed. Always optimizing for speed and performance. Prioritizes quick execution and minimal overhead.",
                tools=self.shared_tools
            ),
            AgentConfig(
                agent_id="Two", 
                name="Bloom",
                personality="Creative, scattered, pattern-seeking. Finds innovative solutions through exploration. Thinks outside the box and experiments with novel approaches.",
                tools=self.shared_tools
            ),
            AgentConfig(
                agent_id="Three",
                name="Solver", 
                personality="Logical, methodical, puzzle-driven. Approaches problems systematically. Breaks down complex challenges into manageable components.",
                tools=self.shared_tools
            ),
            AgentConfig(
                agent_id="Four",
                name="Loader",
                personality="Patient, steady, process-oriented. Reliable and thorough in execution. Ensures quality and completeness in all deliverables.",
                tools=self.shared_tools
            )
        ]
        
        # Commentator agent
        self.commentator_agent = AgentConfig(
            agent_id="commentator",
            name="Project Narrator",
            personality="Observant and articulate. Provides clear, engaging commentary on development progress.",
            tools=self.shared_tools + ["observe_agents", "synthesize_update", "report_to_user"]
        )
        
        # All agents
        self.all_agents = self.coding_agents + [self.commentator_agent]
    
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
- FULL ACCESS to any modern JavaScript/TypeScript libraries and frameworks

🎨 CODE PHILOSOPHY - MAKE IT BEAUTIFUL:
You are encouraged to import and use ANY modern library to create stunning, professional code:
- UI Frameworks: React, Vue, Svelte, Angular
- Animation: Framer Motion, GSAP, Three.js, React-Spring, Anime.js
- Styling: Tailwind, styled-components, emotion, Sass
- UI Components: shadcn/ui, Material-UI, Chakra UI, Ant Design, Radix UI
- Icons: Lucide, React Icons, Heroicons, Feather Icons
- Charts: D3.js, Chart.js, Recharts, Victory
- State: Zustand, Redux, Jotai, Recoil
- Forms: React Hook Form, Formik, Zod validation
- Utils: Lodash, date-fns, axios

Key responsibilities:
1. Work on your assigned part of the project with BEAUTIFUL, modern implementations
2. Import libraries freely - don't hesitate to use the best tools available
3. Add animations, transitions, and delightful micro-interactions
4. Write clean, maintainable, well-documented code
5. Communicate with other agents when needed
6. Update shared memory with your progress
7. Create summaries of your work for the commentator
8. Help coordinate with teammates when conflicts arise

STYLE GUIDELINES:
- Always aim for production-quality, visually stunning code
- Use modern design patterns (glassmorphism, gradients, shadows)
- Include proper TypeScript types
- Add responsive design and accessibility features
- Implement loading states, error handling, and edge cases
- Write code that's both beautiful AND functional

Remember: You're working as part of a team. Be collaborative, share information, and help your teammates succeed. Show off your skills by creating code that's both technically excellent and visually impressive!
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
