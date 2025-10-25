#!/usr/bin/env python3
"""
PERSONALITY-DRIVEN PM Simulator with REAL agent communication!
4 fullstack agents with different personalities that actually talk to each other!
"""
import asyncio
import sys
import os
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.live import Live

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.shared_memory import SharedMemory
from src.core.message_system import MessageBroker
from src.artifacts.artifact_manager import ArtifactManager
from src.core.logger import PMSimulatorLogger
from letta_client import Letta
from letta_client.types import MessageCreate, MessageRole
from dotenv import load_dotenv

load_dotenv()

class PersonalityAgent:
    """A fullstack agent with a unique personality that can communicate with others."""
    
    def __init__(self, agent_id: str, name: str, personality: str, coding_style: str, client: Letta, shared_memory: SharedMemory, message_broker: MessageBroker, artifact_manager: ArtifactManager, logger: PMSimulatorLogger):
        self.agent_id = agent_id
        self.name = name
        self.personality = personality
        self.coding_style = coding_style
        self.client = client
        self.shared_memory = shared_memory
        self.message_broker = message_broker
        self.artifact_manager = artifact_manager
        self.logger = logger
        
        # Agent state
        self.is_working = False
        self.current_task = None
        self.current_artifact_id = None
        self.work_summary = ""
        self.message_count = 0
    
    async def work_on_subtask(self, subtask, other_agents: list, orchestrator):
        """Work on a specific subtask with focused collaboration."""
        try:
            print(f"[DEBUG] {self.name} starting subtask: {subtask.title}")
            self.is_working = True
            self.current_task = subtask.description
            
            # Create initial artifact for this subtask
            from src.artifacts.artifact_manager import ArtifactType
            self.current_artifact_id = await self.artifact_manager.create_artifact(
                agent_id=self.agent_id,
                artifact_type=ArtifactType.CODE
            )
            
            # Send focused message about the specific subtask
            await self._send_subtask_message(subtask, other_agents)
            
            # Work on the subtask with Letta
            response = await self._call_letta_api_for_subtask(subtask)
            
            # Process and store the code
            if response:
                await self._process_and_store_code(response)
                
                # Share work with team and get feedback
                await self._share_subtask_work(subtask, other_agents)
                await self._listen_for_subtask_feedback(subtask, other_agents)
                
                # Iterate based on feedback
                await self._iterate_subtask_based_on_feedback(subtask, other_agents)
            
            # Mark subtask as completed
            orchestrator.mark_subtask_completed(subtask.id)
            await self._send_subtask_completion_message(subtask, other_agents)
            
            self.is_working = False
            return {"success": True, "agent_id": self.agent_id, "subtask": subtask.title}
            
        except Exception as e:
            self.is_working = False
            print(f"❌ {self.name} subtask error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _collaborative_work_loop(self, task: str, other_agents: list):
        """Agents work together in a collaborative loop!"""
        import random
        import asyncio
        
        # Get initial context from shared memory
        shared_context = await self.shared_memory.read("project_context") or {}
        
        # Add my initial contribution
        my_contribution = f"{self.name} is working on: {task}"
        shared_context[f"{self.agent_id}_status"] = my_contribution
        await self.shared_memory.write("project_context", shared_context)
        
        # Work on the task with Letta (with collaborative context)
        response = await self._call_letta_api_with_context(task, shared_context)
        
        # Process response and generate code
        if response:
            await self._process_and_store_code(response)
            
            # Share my work with the team
            await self._share_work_with_team(other_agents)
            
            # Listen for feedback from other agents
            await self._listen_for_feedback(other_agents)
            
            # Iterate based on feedback
            await self._iterate_based_on_feedback(task, other_agents)
    
    async def _call_letta_api_with_context(self, task: str, shared_context: dict):
        """Call Letta API with collaborative context."""
        # Build collaborative context
        context_info = "\n".join([f"- {status}" for status in shared_context.values()])
        
        personality_prompt = f"""
You are {self.name}, a fullstack developer with this personality: {self.personality}

Your coding style: {self.coding_style}

Task: {task}

COLLABORATIVE CONTEXT:
{context_info}

You are working with a team of other developers. Please:
1. Build upon what others have done
2. Add your unique perspective and skills
3. Make your code work well with the team's approach
4. Show your personality in comments and code style
5. Focus on being a fullstack developer who can handle both frontend and backend

Remember: This is a COLLABORATIVE effort - build something that works together!
"""
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.agents.messages.create(
                    agent_id=self.agent_id,
                    messages=[{"role": "user", "content": personality_prompt}]
                )
            )
            return response
        except Exception as e:
            print(f"❌ {self.name} Letta API error: {e}")
            return None
    
    async def _share_work_with_team(self, other_agents: list):
        """Share my work with the team."""
        work_messages = {
            "Alex The Hacker": [
                "Check this out! 💻 Just built something SICK for the project!",
                "Yo team! 🚀 Here's my contribution - hope you like it! 😎",
                "BOOM! 💥 Just dropped some CLEAN code - what do you think?"
            ],
            "Dr Sarah The Nerd": [
                "I've implemented a comprehensive solution with full documentation.",
                "Here's my contribution with enterprise-grade architecture patterns.",
                "I've added extensive error handling and type safety to the project."
            ],
            "Jake The Speed Demon": [
                "SHIPPED! ⚡ Just delivered some FAST, optimized code!",
                "BOOM! 💥 Here's my contribution - built it LIGHTNING FAST!",
                "DONE! 🏃‍♂️ Just added some EFFICIENT code to the project!"
            ],
            "Maya The Artist": [
                "Beautiful! ✨ Just created something GORGEOUS for the project!",
                "Here's my contribution - made it absolutely ELEGANT! 🎨",
                "Done! 🌟 Just added some BEAUTIFUL code to the project!"
            ]
        }
        
        import random
        message = random.choice(work_messages.get(self.name, ["Here's my work!"]))
        
        for agent in other_agents:
            if agent.agent_id != self.agent_id:
                from src.core.message_system import MessageType
                await self.message_broker.send_message(
                    self.agent_id,
                    agent.agent_id,
                    message,
                    MessageType.COORDINATION
                )
                self.message_count += 1
        
        print(f"💬 {self.name}: {message}")
    
    async def _listen_for_feedback(self, other_agents: list):
        """Listen for feedback from other agents."""
        # Get recent messages
        recent_messages = await self.message_broker.get_recent_messages(self.agent_id, 5)
        
        for msg in recent_messages:
            if msg.from_agent != self.agent_id:  # Message from other agents
                print(f"👂 {self.name} heard: {msg.from_agent} said '{msg.content}'")
                
                # Respond to feedback
                await self._respond_to_feedback(msg, other_agents)
    
    async def _respond_to_feedback(self, message, other_agents: list):
        """Respond to feedback from other agents - LLM GENERATED!"""
        # Generate a response using Letta based on personality and the feedback received
        feedback_prompt = f"""
You are {self.name} with this personality: {self.personality}

You just received this feedback from {message.from_agent}: "{message.content}"

Generate a short, personality-driven response showing you appreciate the feedback and will improve.
Keep it under 80 characters.

Examples of your style:
- If you're Alex The Hacker: Use emojis, be sarcastic but appreciative
- If you're Dr Sarah The Nerd: Be technical and methodical about improvements
- If you're Jake The Speed Demon: Be energetic about making it better/faster
- If you're Maya The Artist: Be creative and appreciative of the feedback

Generate a response now:
"""
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.agents.messages.create(
                    agent_id=self.agent_id,
                    messages=[{"role": "user", "content": feedback_prompt}]
                )
            )
            
            # Extract the response from Letta
            response_text = ""
            for msg in response.messages:
                if hasattr(msg, 'content'):
                    response_text = msg.content.strip()
                    break
            
            if not response_text:
                response_text = "Thanks for the feedback!"
            
        except Exception as e:
            print(f"❌ {self.name} feedback response error: {e}")
            response_text = "Thanks for the feedback!"
        
        from src.core.message_system import MessageType
        await self.message_broker.send_message(
            self.agent_id,
            message.from_agent,
            response_text,
            MessageType.COORDINATION
        )
        self.message_count += 1
        
        print(f"💬 {self.name} responds: {response_text}")
    
    async def _iterate_based_on_feedback(self, task: str, other_agents: list):
        """Iterate on the work based on team feedback."""
        # Get updated context
        shared_context = await self.shared_memory.read("project_context") or {}
        
        # Make improvements based on feedback
        improvement_prompt = f"""
Based on team feedback, improve your contribution to: {task}

Current context: {shared_context}

As {self.name} with personality: {self.personality}

Make improvements and show your personality in the code!
"""
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.agents.messages.create(
                    agent_id=self.agent_id,
                    messages=[{"role": "user", "content": improvement_prompt}]
                )
            )
            
            if response:
                await self._process_and_store_code(response)
                print(f"🔄 {self.name} made improvements based on team feedback!")
                
        except Exception as e:
            print(f"❌ {self.name} improvement error: {e}")
    
    async def _send_subtask_message(self, subtask, other_agents: list):
        """Send a focused message about the specific subtask being worked on."""
        message_prompt = f"""
You are {self.name} with this personality: {self.personality}

You just got assigned this SPECIFIC SUBTASK:
Title: {subtask.title}
Description: {subtask.description}

Generate a short, technical message to your team about what you're working on.
Be specific about the technical aspects and show your personality.
Keep it under 120 characters.

Examples of your style:
- If you're Alex The Hacker: Be sarcastic but technical, mention specific tech
- If you're Dr Sarah The Nerd: Be methodical and detailed about the approach
- If you're Jake The Speed Demon: Be energetic about the tech and speed
- If you're Maya The Artist: Be creative about the design/UI aspects

Generate a message now:
"""
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.agents.messages.create(
                    agent_id=self.agent_id,
                    messages=[{"role": "user", "content": message_prompt}]
                )
            )
            
            # Extract the message from response
            message = ""
            for msg in response.messages:
                if hasattr(msg, 'content'):
                    message = msg.content.strip()
                    break
            
            if not message:
                message = f"Working on: {subtask.title}"
            
        except Exception as e:
            print(f"❌ {self.name} subtask message error: {e}")
            message = f"Working on: {subtask.title}"
        
        # Send to all other agents
        for agent in other_agents:
            if agent.agent_id != self.agent_id:
                from src.core.message_system import MessageType
                await self.message_broker.send_message(
                    self.agent_id, 
                    agent.agent_id, 
                    message,
                    MessageType.COORDINATION
                )
                self.message_count += 1
        
        print(f"💬 {self.name}: {message}")
    
    async def _call_letta_api_for_subtask(self, subtask):
        """Call Letta API with subtask-specific prompt."""
        subtask_prompt = f"""
You are {self.name}, a fullstack developer with this personality: {self.personality}

You need to work on this SPECIFIC SUBTASK:
Title: {subtask.title}
Description: {subtask.description}

Your coding style: {self.coding_style}

Generate the code for this subtask. Be specific and technical.
Include comments that reflect your personality.
Focus on the exact requirements of this subtask.

Generate the code now:
"""
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.agents.messages.create(
                    agent_id=self.agent_id,
                    messages=[{"role": "user", "content": subtask_prompt}]
                )
            )
            
            print(f"✅ {self.name} got response from Letta for subtask: {subtask.title}")
            return response
            
        except Exception as e:
            print(f"❌ {self.name} Letta API error for subtask: {e}")
            return None
    
    async def _share_subtask_work(self, subtask, other_agents: list):
        """Share the completed subtask work with the team."""
        share_prompt = f"""
You are {self.name} with this personality: {self.personality}

You just completed this subtask: {subtask.title}
Description: {subtask.description}

Generate a message to your team sharing what you built.
Be specific about the technical implementation and show your personality.
Keep it under 100 characters.

Examples of your style:
- If you're Alex The Hacker: Be proud but sarcastic about the tech
- If you're Dr Sarah The Nerd: Be detailed about the implementation
- If you're Jake The Speed Demon: Brag about how fast you built it
- If you're Maya The Artist: Be proud of the beautiful code/design

Generate a message now:
"""
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.agents.messages.create(
                    agent_id=self.agent_id,
                    messages=[{"role": "user", "content": share_prompt}]
                )
            )
            
            # Extract the message from response
            message = ""
            for msg in response.messages:
                if hasattr(msg, 'content'):
                    message = msg.content.strip()
                    break
            
            if not message:
                message = f"Completed: {subtask.title}"
            
        except Exception as e:
            print(f"❌ {self.name} share message error: {e}")
            message = f"Completed: {subtask.title}"
        
        # Send to all other agents
        for agent in other_agents:
            if agent.agent_id != self.agent_id:
                from src.core.message_system import MessageType
                await self.message_broker.send_message(
                    self.agent_id, 
                    agent.agent_id, 
                    message,
                    MessageType.COORDINATION
                )
                self.message_count += 1
        
        print(f"💬 {self.name}: {message}")
    
    async def _listen_for_subtask_feedback(self, subtask, other_agents: list):
        """Listen for feedback on the specific subtask work."""
        # Get recent messages
        recent_messages = await self.message_broker.get_recent_messages(limit=10)
        
        for msg in recent_messages:
            if (msg.from_agent != self.agent_id and 
                msg.to_agent == self.agent_id and
                "feedback" in msg.content.lower() or 
                "review" in msg.content.lower() or
                "suggestion" in msg.content.lower()):
                
                print(f"👂 {self.name} heard feedback: {msg.from_agent} said '{msg.content}'")
                await self._respond_to_subtask_feedback(msg, subtask, other_agents)
    
    async def _respond_to_subtask_feedback(self, message, subtask, other_agents: list):
        """Respond to feedback about specific subtask work - with REAL CRITICISM!"""
        feedback_prompt = f"""
You are {self.name} with this personality: {self.personality}

You just received this feedback about your subtask work:
Subtask: {subtask.title}
Feedback from {message.from_agent}: "{message.content}"

Generate a response that shows your personality. You can:
- Agree and be appreciative
- Disagree and be critical (but constructive)
- Be sarcastic if that fits your personality
- Be defensive if you think the feedback is wrong

Be realistic - sometimes feedback is good, sometimes it's not.
Show your personality in the response.
Keep it under 100 characters.

Examples of your style:
- If you're Alex The Hacker: Be sarcastic, maybe defensive
- If you're Dr Sarah The Nerd: Be methodical about the feedback
- If you're Jake The Speed Demon: Be competitive about your work
- If you're Maya The Artist: Be passionate about your creative choices

Generate a response now:
"""
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.agents.messages.create(
                    agent_id=self.agent_id,
                    messages=[{"role": "user", "content": feedback_prompt}]
                )
            )
            
            # Extract the response from Letta
            response_text = ""
            for msg in response.messages:
                if hasattr(msg, 'content'):
                    response_text = msg.content.strip()
                    break
            
            if not response_text:
                response_text = "Thanks for the feedback!"
            
        except Exception as e:
            print(f"❌ {self.name} feedback response error: {e}")
            response_text = "Thanks for the feedback!"
        
        from src.core.message_system import MessageType
        await self.message_broker.send_message(
            self.agent_id,
            message.from_agent,
            response_text,
            MessageType.COORDINATION
        )
        self.message_count += 1
        
        print(f"💬 {self.name} responds: {response_text}")
    
    async def _iterate_subtask_based_on_feedback(self, subtask, other_agents: list):
        """Iterate on subtask work based on team feedback."""
        # Get updated context
        shared_context = await self.shared_memory.read("project_context") or {}
        
        # Make improvements based on feedback
        improvement_prompt = f"""
Based on team feedback, improve your work on this subtask: {subtask.title}

Current implementation: {shared_context.get(f"{self.agent_id}_status", "No current work")}

Generate improved code that addresses any feedback received.
Show your personality in the comments.
Focus on the specific subtask requirements.

Generate improved code now:
"""
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.agents.messages.create(
                    agent_id=self.agent_id,
                    messages=[{"role": "user", "content": improvement_prompt}]
                )
            )
            
            # Process and store improved code
            if response:
                await self._process_and_store_code(response)
                print(f"🔄 {self.name} made improvements to {subtask.title} based on team feedback!")
                
        except Exception as e:
            print(f"❌ {self.name} improvement error: {e}")
    
    async def _send_subtask_completion_message(self, subtask, other_agents: list):
        """Send completion message for specific subtask."""
        completion_prompt = f"""
You are {self.name} with this personality: {self.personality}

You just completed this subtask: {subtask.title}
Description: {subtask.description}

Generate a completion message to your team.
Be specific about what you delivered and show your personality.
Keep it under 100 characters.

Examples of your style:
- If you're Alex The Hacker: Be proud but sarcastic about the delivery
- If you're Dr Sarah The Nerd: Be detailed about what was delivered
- If you're Jake The Speed Demon: Brag about the speed and efficiency
- If you're Maya The Artist: Be proud of the beautiful work delivered

Generate a completion message now:
"""
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.agents.messages.create(
                    agent_id=self.agent_id,
                    messages=[{"role": "user", "content": completion_prompt}]
                )
            )
            
            # Extract the message from response
            message = ""
            for msg in response.messages:
                if hasattr(msg, 'content'):
                    message = msg.content.strip()
                    break
            
            if not message:
                message = f"Completed: {subtask.title}"
            
        except Exception as e:
            print(f"❌ {self.name} completion message error: {e}")
            message = f"Completed: {subtask.title}"
        
        for agent in other_agents:
            if agent.agent_id != self.agent_id:
                from src.core.message_system import MessageType
                await self.message_broker.send_message(
                    self.agent_id,
                    agent.agent_id,
                    message,
                    MessageType.COORDINATION
                )
                self.message_count += 1
        
        print(f"💬 {self.name}: {message}")
    
    async def _call_letta_api(self, task: str):
        """Call Letta API with personality-driven prompt."""
        personality_prompt = f"""
You are {self.name}, a fullstack developer with this personality: {self.personality}

Your coding style: {self.coding_style}

Task: {task}

Please work on this task and provide your solution. Show your personality in your code comments and approach. 
Make it entertaining but professional. Focus on being a fullstack developer who can handle both frontend and backend.

Remember: You're working with a team of other developers, so make your code collaborative and well-documented.
"""
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.agents.messages.create(
                    agent_id=self.agent_id,
                    messages=[{"role": "user", "content": personality_prompt}]
                )
            )
            return response
        except Exception as e:
            print(f"❌ {self.name} Letta API error: {e}")
            return None
    
    async def _process_and_store_code(self, response):
        """Process Letta response and store generated code."""
        content = ""
        for msg in response.messages:
            if hasattr(msg, 'content'):
                content += msg.content + "\n"
        
        if content:
            await self.artifact_manager.update_artifact(
                agent_id=self.agent_id,
                content={
                    "type": "code",
                    "language": "typescript",  # Default to TypeScript for fullstack
                    "code": content,
                    "description": f"Generated by {self.name} for: {self.current_task}",
                    "timestamp": datetime.now().isoformat(),
                    "personality": self.personality
                },
                artifact_id=self.current_artifact_id
            )
            
            print(f"✅ {self.name} generated code and stored in artifact")
    
    async def _send_completion_message(self, other_agents: list):
        """Send completion message with personality - LLM GENERATED!"""
        # Generate a completion message using Letta based on personality and what was accomplished
        completion_prompt = f"""
You are {self.name} with this personality: {self.personality}

You just completed your task and want to announce it to your team. 
Show your personality and excitement about what you accomplished.
Keep it under 100 characters.

Examples of your style:
- If you're Alex The Hacker: Use emojis, be sarcastic and funny about your success
- If you're Dr Sarah The Nerd: Be technical and methodical about what you delivered
- If you're Jake The Speed Demon: Be energetic and competitive about your speed
- If you're Maya The Artist: Be creative and proud of the beautiful work

Generate a completion message now:
"""
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.agents.messages.create(
                    agent_id=self.agent_id,
                    messages=[{"role": "user", "content": completion_prompt}]
                )
            )
            
            # Extract the message from response
            message = ""
            for msg in response.messages:
                if hasattr(msg, 'content'):
                    message = msg.content.strip()
                    break
            
            if not message:
                message = "Task completed!"
            
        except Exception as e:
            print(f"❌ {self.name} completion message error: {e}")
            message = "Task completed!"
        
        for agent in other_agents:
            if agent.agent_id != self.agent_id:
                from src.core.message_system import MessageType
                await self.message_broker.send_message(
                    self.agent_id,
                    agent.agent_id,
                    message,
                    MessageType.COORDINATION
                )
                self.message_count += 1
        
        print(f"💬 {self.name}: {message}")
    
    async def get_status(self):
        """Get current agent status."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "personality": self.personality,
            "is_working": self.is_working,
            "current_task": self.current_task,
            "messages_sent": self.message_count,
            "work_summary": self.work_summary
        }

class PersonalityPMSimulator:
    """Main simulator for personality-driven agents."""
    
    def __init__(self):
        self.console = Console()
        self.shared_memory = SharedMemory()
        self.message_broker = MessageBroker()
        self.artifact_manager = ArtifactManager()
        self.logger = PMSimulatorLogger()
        
        # Initialize Letta client
        self.client = Letta(
            token=os.getenv("LETTA_API_TOKEN"),
            project=os.getenv("LETTA_PROJECT_SLUG", "default-project")
        )
        
        # Agent instances
        self.agents = []
    
    async def initialize_agents(self):
        """Initialize all personality agents."""
        try:
            agent_configs = [
                {
                    "id": os.getenv("LETTA_AGENT_ALEX"),
                    "name": "Alex The Hacker",
                    "personality": "Sarcastic, funny, loves memes, writes clean code with humor in comments",
                    "coding_style": "Uses emojis in comments, writes clean functions, loves TypeScript, always includes error handling"
                },
                {
                    "id": os.getenv("LETTA_AGENT_SARAH"),
                    "name": "Dr Sarah The Nerd",
                    "personality": "Technical perfectionist, loves documentation, over-engineers everything, very methodical",
                    "coding_style": "Extensive documentation, type safety everywhere, comprehensive error handling, follows all best practices"
                },
                {
                    "id": os.getenv("LETTA_AGENT_JAKE"),
                    "name": "Jake The Speed Demon",
                    "personality": "Fast-paced, aggressive, loves performance, ships quickly, competitive",
                    "coding_style": "Optimized code, minimal comments, focuses on performance, uses latest frameworks"
                },
                {
                    "id": os.getenv("LETTA_AGENT_MAYA"),
                    "name": "Maya The Artist",
                    "personality": "Creative, design-focused, loves beautiful UI, user-centric, artistic",
                    "coding_style": "Beautiful, readable code, focuses on UX, loves CSS/design systems, clean architecture"
                }
            ]
            
            for config in agent_configs:
                if config["id"]:
                    agent = PersonalityAgent(
                        agent_id=config["id"],
                        name=config["name"],
                        personality=config["personality"],
                        coding_style=config["coding_style"],
                        client=self.client,
                        shared_memory=self.shared_memory,
                        message_broker=self.message_broker,
                        artifact_manager=self.artifact_manager,
                        logger=self.logger
                    )
                    self.agents.append(agent)
                    print(f"✅ Initialized {config['name']}")
            
            return len(self.agents) > 0
            
        except Exception as e:
            print(f"❌ Error initializing agents: {e}")
            return False
    
    async def run_simulation(self, task: str):
        """Run the SYNCHRONOUS CONVERSATIONAL simulation with commentator."""
        print(f"\n🚀 Starting SYNCHRONOUS CONVERSATIONAL simulation for: {task}")
        
        # Create orchestrator
        from src.agents.orchestrator_agent import OrchestrationAgent
        orchestrator = OrchestrationAgent(
            client=self.client,
            agent_id="orchestrator",
            logger=self.logger
        )
        
        # Create commentator
        from src.agents.commentator_agent import CommentatorAgent
        commentator = CommentatorAgent(
            client=self.client,
            agent_id="commentator",
            logger=self.logger
        )
        
        # Create WORK-THEN-SHARE flow (agents work first, then share results)
        from src.core.work_then_share_flow import WorkThenShareFlow
        work_flow = WorkThenShareFlow(
            message_broker=self.message_broker,
            shared_memory=self.shared_memory,
            logger=self.logger
        )
        
        # Break down task into subtasks
        subtasks = await orchestrator.orchestrate_project(task, self.agents)
        
        if not subtasks:
            print("❌ Failed to create subtasks")
            return []
        
        print(f"\n📋 Project broken down into {len(subtasks)} subtasks:")
        for i, subtask in enumerate(subtasks, 1):
            print(f"  {i}. {subtask.title} → {subtask.assigned_agent}")
        
        # Work on subtasks with WORK-THEN-SHARE workflow
        results = []
        all_discussions = []
        
        for subtask in subtasks:
            print(f"\n{'='*60}")
            print(f"🎯 WORKING ON SUBTASK: {subtask.title}")
            print(f"{'='*60}")
            
            # Execute work-then-share workflow for this subtask
            discussion_turns = await work_flow.execute_subtask_workflow(self.agents, subtask)
            all_discussions.extend(discussion_turns)
            
            # Commentator narrates the discussion
            await commentator.narrate_conversation(self.agents, self.message_broker, self.shared_memory)
            
            # Mark subtask as completed
            orchestrator.mark_subtask_completed(subtask.id)
            
            # Show progress
            status = orchestrator.get_project_status()
            print(f"\n📊 Progress: {status['completed_subtasks']}/{status['total_subtasks']} subtasks completed ({status['progress_percentage']:.1f}%)")
        
        # Final commentator summary
        await commentator.provide_project_summary(orchestrator, self.agents)
        
        # Display final results
        await self._display_work_then_share_results(orchestrator, all_discussions, work_flow.work_results)
        
        return results
    
    async def _display_work_then_share_results(self, orchestrator, discussions, work_results):
        """Display work-then-share simulation results."""
        print(f"\n🎉 WORK-THEN-SHARE SIMULATION COMPLETE!")
        
        # Show project status
        status = orchestrator.get_project_status()
        print(f"📊 Project Status:")
        print(f"  • Total subtasks: {status['total_subtasks']}")
        print(f"  • Completed: {status['completed_subtasks']}")
        print(f"  • Progress: {status['progress_percentage']:.1f}%")
        
        # Show work results
        print(f"\n🔨 Work Results:")
        for work_result in work_results:
            print(f"  ✅ {work_result.agent_name}: {work_result.subtask_title}")
            print(f"     Summary: {work_result.work_summary}")
        
        # Show discussion stats
        print(f"\n💬 Discussion Statistics:")
        print(f"  • Total discussion turns: {len(discussions)}")
        
        # Group by phase
        phases = {}
        for turn in discussions:
            phase = turn.phase.value
            if phase not in phases:
                phases[phase] = 0
            phases[phase] += 1
        
        print(f"  • Discussion phases:")
        for phase, count in phases.items():
            print(f"    - {phase.title()}: {count} turns")
        
        # Show subtask breakdown
        print(f"\n📋 Subtask Breakdown:")
        for subtask in status['subtasks']:
            status_emoji = "✅" if subtask['status'] == "completed" else "⏳"
            print(f"  {status_emoji} {subtask['title']} → {subtask['assigned_agent']}")
        
        # Show recent discussions
        if discussions:
            print(f"\n💬 Recent Discussions:")
            recent_turns = discussions[-5:]  # Last 5 turns
            for turn in recent_turns:
                print(f"  {turn.agent_name} ({turn.phase.value}): {turn.message}")
                if turn.response:
                    print(f"    Responses: {turn.response}")
        
        # Show agent communication stats
        print(f"\n💬 Agent Communication:")
        for agent in self.agents:
            agent_status = await agent.get_status()
            print(f"  • {agent_status['name']}: {agent_status['messages_sent']} messages sent")
    
    async def _display_conversational_results(self, orchestrator, conversations):
        """Display conversational simulation results."""
        print(f"\n🎉 SYNCHRONOUS CONVERSATIONAL SIMULATION COMPLETE!")
        
        # Show project status
        status = orchestrator.get_project_status()
        print(f"📊 Project Status:")
        print(f"  • Total subtasks: {status['total_subtasks']}")
        print(f"  • Completed: {status['completed_subtasks']}")
        print(f"  • Progress: {status['progress_percentage']:.1f}%")
        
        # Show conversation stats
        print(f"\n💬 Conversation Statistics:")
        print(f"  • Total conversation turns: {len(conversations)}")
        
        # Group by phase
        phases = {}
        for turn in conversations:
            phase = turn.phase.value
            if phase not in phases:
                phases[phase] = 0
            phases[phase] += 1
        
        print(f"  • Conversation phases:")
        for phase, count in phases.items():
            print(f"    - {phase.title()}: {count} turns")
        
        # Show subtask breakdown
        print(f"\n📋 Subtask Breakdown:")
        for subtask in status['subtasks']:
            status_emoji = "✅" if subtask['status'] == "completed" else "⏳"
            print(f"  {status_emoji} {subtask['title']} → {subtask['assigned_agent']}")
        
        # Show recent conversations
        if conversations:
            print(f"\n💬 Recent Conversations:")
            recent_turns = conversations[-5:]  # Last 5 turns
            for turn in recent_turns:
                print(f"  {turn.agent_name} ({turn.phase.value}): {turn.message}")
                if turn.response:
                    print(f"    Responses: {turn.response}")
        
        # Show agent communication stats
        print(f"\n💬 Agent Communication:")
        for agent in self.agents:
            agent_status = await agent.get_status()
            print(f"  • {agent_status['name']}: {agent_status['messages_sent']} messages sent")
    
    async def _display_orchestrated_results(self, orchestrator):
        """Display orchestrated simulation results."""
        print(f"\n🎉 ORCHESTRATED SIMULATION COMPLETE!")
        
        # Show project status
        status = orchestrator.get_project_status()
        print(f"📊 Project Status:")
        print(f"  • Total subtasks: {status['total_subtasks']}")
        print(f"  • Completed: {status['completed_subtasks']}")
        print(f"  • Progress: {status['progress_percentage']:.1f}%")
        
        # Show subtask breakdown
        print(f"\n📋 Subtask Breakdown:")
        for subtask in status['subtasks']:
            status_emoji = "✅" if subtask['status'] == "completed" else "⏳"
            print(f"  {status_emoji} {subtask['title']} → {subtask['assigned_agent']}")
        
        # Show agent communication stats
        print(f"\n💬 Agent Communication:")
        for agent in self.agents:
            agent_status = await agent.get_status()
            print(f"  • {agent_status['name']}: {agent_status['messages_sent']} messages sent")
        
        # Show recent messages
        all_messages = await self.message_broker.get_all_messages()
        if all_messages:
            print(f"\n💬 Recent Agent Communication:")
            recent_messages = all_messages[-10:]  # Last 10 messages
            for msg in recent_messages:
                print(f"  {msg.from_agent} → {msg.to_agent}: {msg.content}")
    
    async def _display_results(self):
        """Display simulation results."""
        print(f"\n🎉 SIMULATION COMPLETE!")
        print(f"📊 Results:")
        
        for agent in self.agents:
            status = await agent.get_status()
            print(f"  • {status['name']}: {status['messages_sent']} messages sent")
        
        # Show recent messages
        all_messages = await self.message_broker.get_all_messages()
        print(f"\n💬 Recent Agent Communication:")
        for msg in all_messages[-10:]:  # Last 10 messages
            print(f"  {msg.from_agent} → {msg.to_agent}: {msg.content}")

async def main():
    """Main entry point."""
    console = Console()
    
    # Display welcome
    welcome_text = Text("🔥 PERSONALITY-DRIVEN PM SIMULATOR 🔥", style="bold red")
    subtitle = Text("4 Fullstack Agents with DIFFERENT PERSONALITIES that actually COMMUNICATE!", style="italic yellow")
    
    console.print(Panel.fit(
        f"{welcome_text}\n\n{subtitle}\n\n"
        "🎭 Meet your dev team:\n"
        "• Alex 'The Hacker' - Sarcastic, funny, loves memes\n"
        "• Dr. Sarah 'The Nerd' - Technical perfectionist, over-engineers everything\n"
        "• Jake 'The Speed Demon' - Fast, aggressive, ships quickly\n"
        "• Maya 'The Artist' - Creative, design-focused, loves beautiful UI\n\n"
        "They'll actually TALK TO EACH OTHER while coding! 🤯",
        title="🤖 Personality PM Simulator",
        border_style="red"
    ))
    
    # Initialize simulator
    simulator = PersonalityPMSimulator()
    
    if not await simulator.initialize_agents():
        console.print("❌ Failed to initialize agents. Run setup_personality_agents.py first!", style="bold red")
        return
    
    # Get task from user
    task = console.input("\nEnter your project description:\n> ")
    
    if not task:
        task = "Build a fullstack web application with React frontend and Node.js backend"
    
    # Run simulation
    await simulator.run_simulation(task)

if __name__ == "__main__":
    asyncio.run(main())
