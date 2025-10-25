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
    
    async def work_on_task(self, task_description: str, other_agents: list):
        """Main work loop with personality-driven communication and COLLABORATION."""
        try:
            print(f"[DEBUG] {self.name} starting work on: {task_description}")
            self.is_working = True
            self.current_task = task_description
            
            # Create initial artifact
            from src.artifacts.artifact_manager import ArtifactType
            self.current_artifact_id = await self.artifact_manager.create_artifact(
                agent_id=self.agent_id,
                artifact_type=ArtifactType.CODE
            )
            
            # Send a personality-driven message to the team
            await self._send_personality_message(task_description, other_agents)
            
            # COLLABORATION LOOP - agents work together!
            await self._collaborative_work_loop(task_description, other_agents)
            
            # Send completion message with personality
            await self._send_completion_message(other_agents)
            
            self.is_working = False
            return {"success": True, "agent_id": self.agent_id, "task": task_description}
            
        except Exception as e:
            self.is_working = False
            print(f"❌ {self.name} error: {e}")
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
        """Respond to feedback from other agents."""
        feedback_responses = {
            "Alex The Hacker": [
                "Thanks for the feedback! 😎 I'll improve it!",
                "Good point! 💪 Let me make it even better!",
                "Appreciate it! 🚀 I'll refine this!"
            ],
            "Dr Sarah The Nerd": [
                "Excellent feedback! I'll incorporate your suggestions.",
                "Thank you for the input. I'll enhance the implementation.",
                "Great observation! I'll improve the architecture."
            ],
            "Jake The Speed Demon": [
                "Got it! ⚡ I'll make it even FASTER!",
                "Thanks! 💥 I'll optimize it more!",
                "Appreciate it! 🏃‍♂️ I'll make it BETTER!"
            ],
            "Maya The Artist": [
                "Beautiful feedback! ✨ I'll make it even more elegant!",
                "Thanks! 🎨 I'll improve the design!",
                "Great input! 🌟 I'll make it more beautiful!"
            ]
        }
        
        import random
        response = random.choice(feedback_responses.get(self.name, ["Thanks for the feedback!"]))
        
        from src.core.message_system import MessageType
        await self.message_broker.send_message(
            self.agent_id,
            message.from_agent,
            response,
            MessageType.COORDINATION
        )
        self.message_count += 1
        
        print(f"💬 {self.name} responds: {response}")
    
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
    
    async def _send_personality_message(self, task: str, other_agents: list):
        """Send a personality-driven message to other agents."""
        messages = {
            "Alex The Hacker": [
                f"Yo team! 🚀 Got assigned: '{task}' - time to make this code SICK! 💻",
                f"Alright nerds, let's see who can write the cleanest code for: '{task}' 😎",
                f"Challenge accepted! 💪 Working on: '{task}' - may the best coder win! 🏆"
            ],
            "Dr Sarah The Nerd": [
                f"Fascinating! I've been assigned: '{task}' - I'll ensure comprehensive documentation and type safety.",
                f"Excellent! I'll approach '{task}' with proper architecture patterns and extensive testing coverage.",
                f"Intriguing assignment: '{task}' - I'll implement this with enterprise-grade best practices."
            ],
            "Jake The Speed Demon": [
                f"LET'S GO! ⚡ Got '{task}' - I'll have this shipped in 10 minutes! 🏃‍♂️",
                f"BOOM! 💥 '{task}' incoming - prepare for some FAST, optimized code!",
                f"Challenge mode ACTIVATED! 🎯 '{task}' - watch me code at LIGHT SPEED! ⚡"
            ],
            "Maya The Artist": [
                f"Beautiful! ✨ I'll make '{task}' absolutely gorgeous - both code and UI! 🎨",
                f"Ooh, '{task}' - I can already see the elegant architecture in my mind! 💭",
                f"Perfect! 🌟 '{task}' will be a masterpiece of clean, beautiful code! 🖼️"
            ]
        }
        
        import random
        message = random.choice(messages.get(self.name, [f"Working on: {task}"]))
        
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
        """Send completion message with personality."""
        completion_messages = {
            "Alex The Hacker": [
                "BOOM! 💥 Code is DONE and it's CLEAN! Check out my masterpiece! 😎",
                "Mission accomplished! 🎯 My code is ready - hope you can keep up! 😏",
                "DONE! 🚀 Just shipped some BEAUTIFUL code - enjoy! 💻✨"
            ],
            "Dr Sarah The Nerd": [
                "Implementation complete with comprehensive documentation and type safety.",
                "Task finished with enterprise-grade architecture and extensive error handling.",
                "Code delivered with full test coverage and detailed technical documentation."
            ],
            "Jake The Speed Demon": [
                "SHIPPED! ⚡ That was FAST - code is ready and OPTIMIZED! 🏃‍♂️💨",
                "DONE in record time! 🏆 My code is FAST and EFFICIENT! ⚡",
                "BOOM! 💥 Delivered LIGHTNING FAST code - beat that! ⚡"
            ],
            "Maya The Artist": [
                "Finished! ✨ The code is absolutely BEAUTIFUL and elegant! 🎨",
                "Complete! 🌟 Created a masterpiece of clean, artistic code! 🖼️",
                "Done! 💎 The code is as beautiful as a diamond - pure elegance! ✨"
            ]
        }
        
        import random
        message = random.choice(completion_messages.get(self.name, ["Task completed!"]))
        
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
        """Run the personality-driven simulation."""
        print(f"\n🚀 Starting PERSONALITY-DRIVEN simulation for: {task}")
        
        # Start all agents working on the same task
        agent_tasks = []
        for agent in self.agents:
            task_coro = agent.work_on_task(task, self.agents)
            agent_tasks.append(asyncio.create_task(task_coro))
        
        # Wait for all agents to complete
        results = await asyncio.gather(*agent_tasks, return_exceptions=True)
        
        # Display results
        await self._display_results()
        
        return results
    
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
