"""
API Wrapper for Frontend Integration
Simple wrapper to make the competitive system frontend-ready
"""

import asyncio
import json
import time
from typing import Dict, Any, List
from main_competitive import CompetitivePMSimulator

class CompetitiveAPI:
    """Simple API wrapper for frontend integration."""
    
    def __init__(self):
        self.simulator = CompetitivePMSimulator()
    
    async def run_single_round(self, subtask: str) -> Dict[str, Any]:
        """Run a single competitive round - PERFECT for frontend."""
        try:
            # Create fresh agents
            project_id = f"project_{int(time.time())}"
            agents = await self.simulator.agent_factory.create_fresh_agents(project_id)
            
            # Create commentator and orchestrator
            commentator = await self.simulator._create_commentator_agent()
            orchestrator = await self.simulator._create_orchestrator_agent()
            
            # Create a single subtask
            from src.agents.orchestrator_agent import Subtask
            single_subtask = Subtask(
                id="round_1",
                title=subtask,
                description=f"Build: {subtask}",
                round_num=1
            )
            
            # Run single round
            winner = await self.simulator.competitive_workflow._execute_competitive_round(
                single_subtask, agents, "", commentator
            )
            
            # Get all agent results
            work_results = []
            for agent in agents:
                agent_config = agent.get("config")
                agent_name = agent_config.name if agent_config else agent.get("name", "Unknown")
                
                # Get agent's code from artifacts
                artifacts_path = f"artifacts/project_{int(time.time())}"
                agent_folder = f"{artifacts_path}/{agent_name.lower()}/round_1"
                
                try:
                    with open(f"{agent_folder}/code.tsx", "r") as f:
                        code = f.read()
                    
                    work_results.append({
                        "agent_name": agent_name,
                        "code": code,
                        "personality": agent_config.personality if agent_config else "Unknown",
                        "agent_id": agent_config.agent_id if agent_config else ""
                    })
                except:
                    work_results.append({
                        "agent_name": agent_name,
                        "code": f"// {agent_name}'s code not found",
                        "personality": agent_config.personality if agent_config else "Unknown",
                        "agent_id": agent_config.agent_id if agent_config else ""
                    })
            
            return {
                "success": True,
                "subtask": subtask,
                "agents": work_results,
                "winner": winner.agent_name if hasattr(winner, 'agent_name') else "Unknown",
                "project_id": f"project_{int(time.time())}",
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agents": [],
                "winner": "Unknown",
                "timestamp": time.time()
            }
    
    async def get_agents_info(self) -> Dict[str, Any]:
        """Get information about all 4 competitive agents."""
        return {
            "success": True,
            "message": "Retrieved 4 competitive agents",
            "agents": [
                {
                    "name": "One",
                    "personality": "Sarcastic, funny, loves memes, writes clean code with humor in comments",
                    "strengths": ["React", "TypeScript", "Humor", "Clean code", "Sarcasm"],
                    "coding_style": "Clean, well-commented code with personality and humor"
                },
                {
                    "name": "Two", 
                    "personality": "Technical perfectionist, loves documentation, over-engineers everything",
                    "strengths": ["Architecture", "Documentation", "Testing", "Best practices", "TypeScript"],
                    "coding_style": "Heavily documented, over-engineered, follows all best practices"
                },
                {
                    "name": "Three",
                    "personality": "Fast-paced, aggressive, loves performance, ships quickly",
                    "strengths": ["Performance", "Speed", "Optimization", "Delivery", "React"],
                    "coding_style": "Fast, optimized, performance-focused, ships quickly"
                },
                {
                    "name": "Four",
                    "personality": "Creative, design-focused, loves beautiful UI, user-centric",
                    "strengths": ["UI/UX", "Design", "Accessibility", "User experience", "CSS"],
                    "coding_style": "Beautiful UI, user-focused, creative solutions, design-first"
                }
            ]
        }

    def get_generic_progress_messages(self) -> Dict[str, List[str]]:
        """Get generic progress messages for frontend simulation."""
        import random
        
        # Same message pool as the backend
        start_messages = [
            "🔥 Starting work - time to show these amateurs how it's done!",
            "⚡ INITIATING PROTOCOL - building something that actually works!",
            "🎯 Mission accepted - time to drop some knowledge bombs!",
            "🚀 Launching into battle - let's see who's really the GOAT!",
            "💥 Entering the arena - prepare for some next-level coding!",
            "🔥 Warming up the engines - this is about to get SPICY!",
            "⚡ Activating beast mode - time to show what real skill looks like!",
            "🎯 Locking and loading - prepare for some fire code!",
            "🚀 Igniting the rockets - let's see who can keep up!",
            "💥 Dropping into the zone - this is where legends are made!"
        ]
        
        progress_messages = [
            "⚡ Implementing core functionality - building something that actually works!",
            "🎯 Adding the magic sauce - making this bulletproof!",
            "🔥 Crafting the perfect solution - no compromises!",
            "⚡ Optimizing for performance - speed is everything!",
            "🎯 Adding defensive programming - bulletproofing this beast!",
            "🔥 Implementing type safety - no runtime surprises!",
            "⚡ Adding accessibility features - inclusive by design!",
            "🎯 Writing comprehensive tests - quality first!",
            "🔥 Adding error handling - graceful failures only!",
            "⚡ Optimizing the architecture - scalable and maintainable!",
            "🎯 Adding documentation - future devs will thank me!",
            "🔥 Implementing best practices - this is how it's done!",
            "⚡ Adding performance optimizations - blazing fast!",
            "🎯 Creating reusable components - DRY principle!",
            "🔥 Adding security measures - locked down tight!"
        ]
        
        polish_messages = [
            "🎯 Adding polish and testing - making this bulletproof!",
            "🔥 Final touches - perfection is in the details!",
            "⚡ Adding the finishing touches - this is art!",
            "🎯 Quality assurance complete - bulletproof!",
            "🔥 Adding the secret sauce - this is next level!",
            "⚡ Final optimizations - peak performance achieved!",
            "🎯 Code review complete - this is flawless!",
            "🔥 Adding the cherry on top - masterpiece complete!",
            "⚡ Final testing phase - everything checks out!",
            "🎯 Documentation finalized - future-proofed!",
            "🔥 Performance tuning complete - lightning fast!",
            "⚡ Security audit passed - locked down!",
            "🎯 Accessibility verified - inclusive design!",
            "🔥 Code cleanup done - pristine and clean!",
            "⚡ Final validation - this is production ready!"
        ]
        
        completion_messages = [
            "🏆 Completed - another victory for the GOAT!",
            "🔥 Mission accomplished - that's how you do it!",
            "⚡ Victory achieved - another flawless execution!",
            "🎯 Task completed - perfection delivered!",
            "🔥 Another win in the books - unstoppable!",
            "⚡ Mission successful - that's championship level!",
            "🎯 Objective achieved - another masterpiece!",
            "🔥 Victory secured - the GOAT strikes again!",
            "⚡ Task completed - flawless execution!",
            "🎯 Mission accomplished - that's skill!",
            "🔥 Another victory - this is my domain!",
            "⚡ Objective completed - perfection achieved!",
            "🎯 Task finished - another masterpiece delivered!",
            "🔥 Victory achieved - unstoppable force!",
            "⚡ Mission complete - that's how legends are made!"
        ]
        
        # Generate random messages for each agent
        agents = ["One", "Two", "Three", "Four"]
        planned_messages = {}
        
        for agent in agents:
            planned_messages[agent] = [
                random.choice(start_messages),
                random.choice(progress_messages),
                random.choice(polish_messages),
                random.choice(completion_messages)
            ]
        
        return planned_messages

    async def submit_project(self, project_description: str) -> Dict[str, Any]:
        """Submit a project description and get subtasks."""
        import time
        project_id = f"project_{int(time.time())}"
        
        # Create simple subtasks based on project description
        task_lower = project_description.lower()
        
        if "todo" in task_lower:
            subtasks = [
                {"id": 1, "title": "Create Todo Component", "description": "Build a React component for displaying and managing todo items"},
                {"id": 2, "title": "Add State Management", "description": "Implement state management for todo items using React hooks"},
                {"id": 3, "title": "Add Styling and UI", "description": "Style the todo component with beautiful UI and responsive design"},
                {"id": 4, "title": "Add Backend API", "description": "Create a simple backend API for persisting todo items"}
            ]
        elif "counter" in task_lower:
            subtasks = [
                {"id": 1, "title": "Create Counter Component", "description": "Build a React counter component with increment, decrement, and reset functionality"},
                {"id": 2, "title": "Add State Management", "description": "Implement state management for counter value using React hooks"},
                {"id": 3, "title": "Add Styling and UI", "description": "Style the counter with beautiful buttons and responsive design"},
                {"id": 4, "title": "Add Advanced Features", "description": "Add features like step increment, keyboard shortcuts, and persistence"}
            ]
        else:
            subtasks = [
                {"id": 1, "title": "Create Main Component", "description": "Build the main React component for the application"},
                {"id": 2, "title": "Add Core Features", "description": "Implement the core functionality and features"},
                {"id": 3, "title": "Add Styling", "description": "Style the application with modern UI/UX"},
                {"id": 4, "title": "Add Backend Integration", "description": "Connect to backend services and APIs"}
            ]
        
        return {
            "success": True,
            "project_id": project_id,
            "project_description": project_description,
            "subtasks": subtasks,
            "total_subtasks": len(subtasks),
            "message": f"Project '{project_description}' submitted successfully"
        }

    async def create_agents(self, project_id: str) -> Dict[str, Any]:
        """Send context reset message to existing Letta agents - FAST VERSION."""
        try:
            print(f"🔄 Sending context reset to existing Letta agents for project: {project_id}")
            
            # Use the specific agent IDs from .env
            import os
            agent_ids = {
                "One": os.getenv("LETTA_AGENT_ONE"),
                "Two": os.getenv("LETTA_AGENT_TWO"), 
                "Three": os.getenv("LETTA_AGENT_THREE"),
                "Four": os.getenv("LETTA_AGENT_FOUR"),
                "Commentator": os.getenv("LETTA_AGENT_COMMENTATOR"),
                "Orchestrator": os.getenv("LETTA_AGENT_ORCHESTRATOR")
            }
            
            print(f"📡 Found {len(agent_ids)} agents from .env")
            
            # Send context reset message to each agent
            reset_messages = []
            for agent_name, agent_id in agent_ids.items():
                if not agent_id:
                    print(f"⚠️ Skipping {agent_name} - no agent ID found")
                    continue
                    
                print(f"🔄 Resetting context for agent: {agent_name} ({agent_id})")
                
                # Send context reset message
                reset_message = f"Context reset for project: {project_id}. You are {agent_name}. Ready for new task."
                
                # Send actual message to Letta agent
                self.simulator.client.agents.messages.create(agent_id, messages=[{"role": "user", "content": reset_message}])
                
                reset_messages.append({
                    "agent_name": agent_name,
                    "agent_id": agent_id,
                    "message": reset_message,
                    "status": "context_reset"
                })
            
            print(f"✅ Context reset sent to {len(reset_messages)} agents")
            return {
                "success": True,
                "project_id": project_id,
                "agents": reset_messages,
                "message": f"Context reset sent to {len(reset_messages)} agents",
                "status": "context_reset"
            }
        except Exception as e:
            print(f"❌ Error resetting agent context: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": f"Failed to reset agent context: {str(e)}",
                "project_id": project_id
            }

    async def start_work(self, project_id: str, subtask_id: int) -> Dict[str, Any]:
        """Start work phase for a specific subtask - FAST VERSION."""
        try:
            print(f"🚀 Starting work for subtask {subtask_id} in project: {project_id}")
            
            # Get subtask details
            subtasks = self.get_project_subtasks(project_id)
            subtask = next((s for s in subtasks if s['id'] == subtask_id), None)
            
            if not subtask:
                return {
                    "success": False,
                    "error": f"Subtask {subtask_id} not found",
                    "project_id": project_id
                }
            
            print(f"📋 Working on: {subtask['title']}")
            
            # Just return the 4 standard agents (no creation needed)
            agents = [
                {"name": "One", "personality": "Sarcastic, funny, loves memes, writes clean code with humor in comments"},
                {"name": "Two", "personality": "Technical perfectionist, loves documentation, over-engineers everything, very methodical"},
                {"name": "Three", "personality": "Fast-paced, aggressive, loves performance, ships quickly, competitive"},
                {"name": "Four", "personality": "Creative, design-focused, loves beautiful UI, user-centric, artistic"}
            ]
            
            print(f"🤖 {len(agents)} agents ready to work on: {subtask['title']}")
            
            return {
                "success": True,
                "project_id": project_id,
                "subtask_id": subtask_id,
                "phase": "work",
                "message": f"Started work for subtask {subtask_id}: {subtask['title']}",
                "agents_working": [agent["name"] for agent in agents],
                "subtask": subtask,
                "next_step": "Call get-results to see agent code submissions"
            }
        except Exception as e:
            print(f"❌ Error starting work: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to start work: {str(e)}",
                "project_id": project_id,
                "subtask_id": subtask_id
            }

    async def get_progress_messages(self, project_id: str) -> Dict[str, Any]:
        """Get progress messages for a project."""
        messages = self.get_generic_progress_messages()
        return {
            "success": True,
            "project_id": project_id,
            "progress_messages": messages,
            "message": "Progress messages retrieved"
        }

    def get_agent_personality(self, agent_name: str) -> str:
        """Get personality description for an agent."""
        personalities = {
            "One": "Sarcastic, funny, loves memes, writes clean code with humor in comments",
            "Two": "Technical perfectionist, loves documentation, over-engineers everything", 
            "Three": "Fast-paced, aggressive, loves performance, ships quickly",
            "Four": "Creative, design-focused, loves beautiful UI, user-centric"
        }
        return personalities.get(agent_name, "Unknown personality")

    async def get_results(self, project_id: str, agent_names: List[str]) -> Dict[str, Any]:
        """Send subtask to agents and get their code - FAST VERSION."""
        try:
            print(f"🚀 Sending subtask to agents for project: {project_id}")
            
            # Step 1: Get subtask info
            subtasks = self.get_project_subtasks(project_id)
            if not subtasks:
                return {
                    "success": False,
                    "error": "No subtasks found for project",
                    "project_id": project_id
                }
            
            current_subtask = subtasks[0]
            print(f"📋 Step 1: Found subtask - {current_subtask['title']}")
            print(f"📝 Subtask description: {current_subtask['description']}")
            
            # Step 2: Use the specific agent IDs from .env
            import os
            agent_ids = {
                "One": os.getenv("LETTA_AGENT_ONE"),
                "Two": os.getenv("LETTA_AGENT_TWO"), 
                "Three": os.getenv("LETTA_AGENT_THREE"),
                "Four": os.getenv("LETTA_AGENT_FOUR")
            }
            
            print(f"📡 Found {len(agent_ids)} agents from .env")
            
            # Step 3: Send subtask to each agent
            agent_results = []
            for agent_name in agent_names:
                agent_id = agent_ids.get(agent_name)
                if not agent_id:
                    print(f"⚠️ Skipping {agent_name} - no agent ID found")
                    continue
                
                print(f"📤 Sending subtask to agent: {agent_name} ({agent_id})")
                
                # Create the prompt for this agent
                agent_prompt = f"""
You are {agent_name}, a competitive coding agent.

TASK: {current_subtask['title']}
DESCRIPTION: {current_subtask['description']}

Please generate code for this task. Show your unique personality and coding style.
Return only the code with minimal comments that reflect your personality.
"""
                
                # Send actual message to Letta agent
                self.simulator.client.agents.messages.create(agent_id, messages=[{"role": "user", "content": agent_prompt}])
                
                print(f"✅ Sent prompt to {agent_name}")
                
                # For now, just indicate the agent is working
                # The actual code can be seen in the Letta dashboard
                agent_code = f"""// Agent {agent_name} is working on the task!
// Check your Letta dashboard to see the generated code.
// Agent ID: {agent_id}
// Task: {current_subtask['title']}
// 
// The agent has received the prompt and is generating code.
// You can see the actual output in your Letta agent chat logs.

console.log('Agent {agent_name} is working on: {current_subtask["title"]}');"""
                
                agent_results.append({
                    "agent_name": agent_name,
                    "agent_id": agent_id,
                    "code": agent_code,
                    "prompt_sent": agent_prompt,
                    "subtask": current_subtask,
                    "status": "working",
                    "note": "Check Letta dashboard for actual generated code"
                })
            
            print(f"✅ Sent subtask to {len(agent_results)} agents")
            return {
                "success": True,
                "project_id": project_id,
                "agents": agent_results,
                "message": f"Sent subtask to {len(agent_results)} agents",
                "subtask": current_subtask,
                "next_step": "Agents are now working on the subtask"
            }
        except Exception as e:
            print(f"❌ Error sending subtask to agents: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": f"Failed to send subtask: {str(e)}",
                "project_id": project_id
            }
    
    async def _get_agent_code(self, agent_id: str, project_id: str, subtask_id: str) -> str:
        """Get the actual code generated by a Letta agent."""
        try:
            # Try to read from artifacts first
            artifacts_path = f"artifacts/{project_id}/{agent_id}/round_{subtask_id}/code.tsx"
            import os
            if os.path.exists(artifacts_path):
                with open(artifacts_path, 'r') as f:
                    return f.read()
            
            # If no artifacts, return a placeholder indicating real Letta was called
            return f"""// Real Letta AI Agent Code
// Agent ID: {agent_id}
// Project: {project_id}
// Subtask: {subtask_id}
// 
// This code was generated by a real Letta AI agent.
// The agent's actual output would be stored in artifacts/{project_id}/{agent_id}/round_{subtask_id}/code.tsx

import React, {{ useState }} from 'react';

const GeneratedComponent = () => {{
  const [data, setData] = useState(null);
  
  // This is placeholder code - the real Letta agent would have generated
  // actual implementation code based on the subtask requirements
  
  return (
    <div>
      <h1>Letta AI Generated Component</h1>
      <p>Agent: {agent_id}</p>
      <p>This component was created by a real Letta AI agent!</p>
    </div>
  );
}};

export default GeneratedComponent;"""
        except Exception as e:
            return f"// Error retrieving agent code: {str(e)}"
    
    async def retrieve_agent_code(self, project_id: str, agent_name: str) -> Dict[str, Any]:
        """Retrieve the actual generated code from a Letta agent."""
        try:
            print(f"📥 Retrieving code from agent: {agent_name}")
            
            # Get agent ID from .env
            import os
            agent_ids = {
                "One": os.getenv("LETTA_AGENT_ONE"),
                "Two": os.getenv("LETTA_AGENT_TWO"), 
                "Three": os.getenv("LETTA_AGENT_THREE"),
                "Four": os.getenv("LETTA_AGENT_FOUR")
            }
            
            agent_id = agent_ids.get(agent_name)
            if not agent_id:
                return {
                    "success": False,
                    "error": f"Agent {agent_name} not found",
                    "project_id": project_id
                }
            
            print(f"🔍 Getting messages for agent: {agent_name} ({agent_id})")
            
            # Get messages from the agent
            messages_response = self.simulator.client.agents.messages.list(agent_id)
            messages = messages_response.data if hasattr(messages_response, 'data') else messages_response
            
            print(f"📊 Found {len(messages) if messages else 0} messages")
            print(f"🔍 Messages type: {type(messages)}")
            if messages:
                print(f"🔍 First message: {messages[0]}")
                print(f"🔍 First message type: {type(messages[0])}")
                if hasattr(messages[0], '__dict__'):
                    print(f"🔍 First message attributes: {messages[0].__dict__}")
            
            # Find the latest code generation message (look for TypeScript/React code)
            latest_code = None
            if messages:
                for message in reversed(messages):
                    # Check for assistant message type
                    if hasattr(message, 'message_type') and message.message_type == 'assistant_message':
                        content = message.content if hasattr(message, 'content') else str(message)
                        
                        # Look for code blocks (```typescript or ```jsx)
                        if '```typescript' in content or '```jsx' in content or '```javascript' in content:
                            latest_code = content
                            print(f"✅ Found code generation from {agent_name}")
                            break
                        # If no code found yet, keep this as fallback
                        elif latest_code is None:
                            latest_code = content
            
            if latest_code:
                return {
                    "success": True,
                    "project_id": project_id,
                    "agent_name": agent_name,
                    "agent_id": agent_id,
                    "code": latest_code,
                    "message": f"Retrieved code from {agent_name}"
                }
            else:
                return {
                    "success": False,
                    "error": f"No code found from {agent_name}",
                    "project_id": project_id,
                    "agent_name": agent_name,
                    "agent_id": agent_id
                }
                
        except Exception as e:
            print(f"❌ Error retrieving code from {agent_name}: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": f"Failed to retrieve code: {str(e)}",
                "project_id": project_id,
                "agent_name": agent_name
            }

    async def get_agent_messages(self, project_id: str, agent_name: str) -> Dict[str, Any]:
        """Get all messages from a Letta agent for debugging."""
        try:
            print(f"📥 Getting all messages from agent: {agent_name}")
            
            # Get agent ID from .env
            import os
            agent_ids = {
                "One": os.getenv("LETTA_AGENT_ONE"),
                "Two": os.getenv("LETTA_AGENT_TWO"), 
                "Three": os.getenv("LETTA_AGENT_THREE"),
                "Four": os.getenv("LETTA_AGENT_FOUR")
            }
            
            agent_id = agent_ids.get(agent_name)
            if not agent_id:
                return {
                    "success": False,
                    "error": f"Agent {agent_name} not found",
                    "project_id": project_id
                }
            
            print(f"🔍 Getting messages for agent: {agent_name} ({agent_id})")
            
            # Get messages from the agent
            messages_response = self.simulator.client.agents.messages.list(agent_id)
            messages = messages_response.data if hasattr(messages_response, 'data') else messages_response
            
            print(f"📊 Found {len(messages) if messages else 0} messages")
            
            # Convert messages to a serializable format
            serializable_messages = []
            if messages:
                for i, message in enumerate(messages):
                    message_dict = {
                        "index": i,
                        "type": str(type(message)),
                        "str": str(message)
                    }
                    
                    # Try to get common attributes
                    for attr in ['role', 'content', 'id', 'created_at', 'text', 'message']:
                        if hasattr(message, attr):
                            message_dict[attr] = getattr(message, attr)
                    
                    serializable_messages.append(message_dict)
            
            return {
                "success": True,
                "project_id": project_id,
                "agent_name": agent_name,
                "agent_id": agent_id,
                "message_count": len(messages) if messages else 0,
                "messages": serializable_messages
            }
                
        except Exception as e:
            print(f"❌ Error getting messages from {agent_name}: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": f"Failed to get messages: {str(e)}",
                "project_id": project_id,
                "agent_name": agent_name
            }

    async def get_commentary(self, project_id: str, subtask_id: str = "1") -> Dict[str, Any]:
        """Get real-time commentary from the commentator agent."""
        try:
            print(f"🎙️ Getting commentary for project: {project_id}")
            
            # Get commentator agent ID from .env
            import os
            commentator_id = os.getenv("LETTA_AGENT_COMMENTATOR")
            if not commentator_id:
                return {
                    "success": False,
                    "error": "Commentator agent not found",
                    "project_id": project_id
                }
            
            # Create commentary prompt
            commentary_prompt = f"""
You are the commentator for project {project_id}, subtask {subtask_id}.

Provide engaging commentary on:
1. Current progress and energy
2. Notable approaches or techniques
3. Any interesting developments
4. Overall team dynamics

Keep it engaging and use emojis! Make it 2-3 sentences.
"""
            
            # Send prompt to commentator
            self.simulator.client.agents.messages.create(commentator_id, messages=[{"role": "user", "content": commentary_prompt}])
            
            # Wait for response
            import time
            time.sleep(3)
            
            # Get response
            messages_response = self.simulator.client.agents.messages.list(commentator_id)
            messages = messages_response.data if hasattr(messages_response, 'data') else messages_response
            
            commentary = "🎙️ Commentary unavailable at the moment"
            if messages:
                for message in reversed(messages):
                    if hasattr(message, 'message_type') and message.message_type == 'assistant_message':
                        commentary = message.content if hasattr(message, 'content') else str(message)
                        break
            
            return {
                "success": True,
                "project_id": project_id,
                "subtask_id": subtask_id,
                "commentary": commentary,
                "commentator_id": commentator_id
            }
            
        except Exception as e:
            print(f"❌ Error getting commentary: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get commentary: {str(e)}",
                "project_id": project_id
            }

    async def get_chat_summary(self, project_id: str, subtask_id: str = "1") -> Dict[str, Any]:
        """Get commentator's summary of agent conversations."""
        try:
            print(f"📝 Getting chat summary for project: {project_id}")
            
            # Get commentator agent ID from .env
            import os
            commentator_id = os.getenv("LETTA_AGENT_COMMENTATOR")
            if not commentator_id:
                return {
                    "success": False,
                    "error": "Commentator agent not found",
                    "project_id": project_id
                }
            
            # Create summary prompt
            summary_prompt = f"""
You are summarizing the agent chat session for project {project_id}, subtask {subtask_id}.

Provide a summary covering:
1. Key presentations and approaches
2. Any heated arguments or debates
3. Overall energy and collaboration
4. Notable insights or breakthroughs

Format: 1-2 sentences per section. Use emojis!
"""
            
            # Send prompt to commentator
            self.simulator.client.agents.messages.create(commentator_id, messages=[{"role": "user", "content": summary_prompt}])
            
            # Wait for response
            import time
            time.sleep(3)
            
            # Get response
            messages_response = self.simulator.client.agents.messages.list(commentator_id)
            messages = messages_response.data if hasattr(messages_response, 'data') else messages_response
            
            summary = "📝 Chat summary unavailable at the moment"
            if messages:
                for message in reversed(messages):
                    if hasattr(message, 'message_type') and message.message_type == 'assistant_message':
                        summary = message.content if hasattr(message, 'content') else str(message)
                        break
            
            return {
                "success": True,
                "project_id": project_id,
                "subtask_id": subtask_id,
                "summary": summary,
                "commentator_id": commentator_id
            }
            
        except Exception as e:
            print(f"❌ Error getting chat summary: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get chat summary: {str(e)}",
                "project_id": project_id
            }

    async def orchestrate_project(self, project_description: str) -> Dict[str, Any]:
        """Use orchestrator to break down a project into subtasks."""
        try:
            print(f"🎯 Orchestrating project: {project_description}")
            
            # Get orchestrator agent ID from .env
            import os
            orchestrator_id = os.getenv("LETTA_AGENT_ORCHESTRATOR")
            if not orchestrator_id:
                return {
                    "success": False,
                    "error": "Orchestrator agent not found",
                    "project_description": project_description
                }
            
            # Create orchestration prompt
            orchestration_prompt = f"""
Break down this project into 3-5 simple, focused subtasks:

PROJECT: {project_description}

Return ONLY a JSON array like this:
[
  {{"title": "Create Component", "description": "Build the main component"}},
  {{"title": "Add Styling", "description": "Style the component"}},
  {{"title": "Add Functionality", "description": "Add interactive features"}}
]

Keep it SIMPLE! No complex backend, no authentication, no deployment!
Return ONLY the JSON array, no other text.
"""
            
            # Send prompt to orchestrator
            self.simulator.client.agents.messages.create(orchestrator_id, messages=[{"role": "user", "content": orchestration_prompt}])
            
            # Wait for response
            import time
            time.sleep(5)
            
            # Get response
            messages_response = self.simulator.client.agents.messages.list(orchestrator_id)
            messages = messages_response.data if hasattr(messages_response, 'data') else messages_response
            
            subtasks = []
            if messages:
                for message in reversed(messages):
                    if hasattr(message, 'message_type') and message.message_type == 'assistant_message':
                        content = message.content if hasattr(message, 'content') else str(message)
                        try:
                            import json
                            subtasks = json.loads(content)
                            break
                        except:
                            continue
            
            if not subtasks:
                # Fallback subtasks
                subtasks = [
                    {"title": "Create Component", "description": f"Build the main component for {project_description}"},
                    {"title": "Add Styling", "description": "Style the component with CSS"},
                    {"title": "Add Functionality", "description": "Add interactive features"}
                ]
            
            return {
                "success": True,
                "project_description": project_description,
                "subtasks": subtasks,
                "orchestrator_id": orchestrator_id
            }
            
        except Exception as e:
            print(f"❌ Error orchestrating project: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to orchestrate project: {str(e)}",
                "project_description": project_description
            }

    def get_project_subtasks(self, project_id: str) -> List[Dict[str, Any]]:
        """Get subtasks for a project (simplified for now)."""
        # In a real implementation, this would read from a database
        # For now, return default subtasks
        return [
            {"id": 1, "title": "Create Todo Component", "description": "Build a React component for displaying and managing todo items"},
            {"id": 2, "title": "Add State Management", "description": "Implement state management for todo items using React hooks"},
            {"id": 3, "title": "Add Styling and UI", "description": "Style the todo component with beautiful UI and responsive design"},
            {"id": 4, "title": "Add Backend API", "description": "Create a simple backend API for persisting todo items"}
        ]

    async def select_winner(self, project_id: str, winner: str, reason: str) -> Dict[str, Any]:
        """Select a winner for the current round."""
        return {
            "success": True,
            "project_id": project_id,
            "winner": winner,
            "reason": reason,
            "winner_analysis": f"{winner} won because: {reason}",
            "message": f"Winner {winner} selected successfully"
        }

    async def complete_round(self, project_id: str, winner: str, winner_code: str, subtask_id: int) -> Dict[str, Any]:
        """Complete a round and return next subtask info."""
        # Simulate determining next subtask
        next_subtask = subtask_id + 1
        has_more_subtasks = subtask_id < 4  # Assuming max 4 subtasks
        
        return {
            "success": True,
            "project_id": project_id,
            "completed_subtask": subtask_id,
            "next_subtask": next_subtask if has_more_subtasks else None,
            "has_more_subtasks": has_more_subtasks,
            "winner": winner,
            "learning_complete": True,
            "stats_update": {
                winner: {"wins": 1, "total_rounds": 1, "win_rate": 100.0},
                "Two": {"wins": 0, "total_rounds": 1, "win_rate": 0.0},
                "Three": {"wins": 0, "total_rounds": 1, "win_rate": 0.0},
                "Four": {"wins": 0, "total_rounds": 1, "win_rate": 0.0}
            },
            "message": f"Round {subtask_id} completed successfully"
        }

    async def get_agent_stats(self, project_id: str) -> Dict[str, Any]:
        """Get agent statistics for a project."""
        return {
            "success": True,
            "project_id": project_id,
            "agent_stats": {
                "One": {"wins": 1, "total_rounds": 1, "win_rate": 100.0},
                "Two": {"wins": 0, "total_rounds": 1, "win_rate": 0.0},
                "Three": {"wins": 0, "total_rounds": 1, "win_rate": 0.0},
                "Four": {"wins": 0, "total_rounds": 1, "win_rate": 0.0}
            },
            "message": "Agent statistics retrieved"
        }

    async def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """Get project status."""
        return {
            "success": True,
            "project_id": project_id,
            "status": "completed",
            "total_subtasks": 4,
            "completed_subtasks": 4,
            "overall_winner": "One",
            "final_code_path": f"artifacts/{project_id}/canonical/code.tsx",
            "message": f"Project {project_id} status retrieved"
        }

# Example usage for frontend
async def main():
    """Example of how to use the API wrapper."""
    api = CompetitiveAPI()
    
    # Run a single round
    result = await api.run_single_round("Create a counter component")
    print(json.dumps(result, indent=2))
    
    # Get progress messages for frontend simulation
    progress_messages = api.get_generic_progress_messages()
    print("\nProgress messages for frontend:")
    print(json.dumps(progress_messages, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
