"""
Coordinator class for orchestrating all AI agents.
Manages task distribution, agent coordination, and overall simulation flow.
"""
from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime
import json

from .shared_memory import SharedMemory
from .message_system import MessageBroker
from .logger import PMSimulatorLogger
from ..artifacts.artifact_manager import ArtifactManager
from ..agents.real_letta_agent import RealLettaAgent, RealLettaCommentatorAgent
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from config.agents_config import LettaConfig


class Coordinator:
    """
    Main coordinator for the AI agent simulation.
    Manages all agents and orchestrates their collaboration.
    """
    
    def __init__(self):
        # Initialize core systems
        self.shared_memory = SharedMemory()
        self.message_broker = MessageBroker()
        self.artifact_manager = ArtifactManager()
        self.logger = PMSimulatorLogger()
        
        # Initialize Letta configuration
        try:
            self.letta_config = LettaConfig()
        except Exception as e:
            print(f"Error initializing Letta config: {e}")
            self.letta_config = None
        
        # Agent instances
        self.coding_agents: List[CodingAgent] = []
        self.commentator_agent: Optional[CommentatorAgent] = None
        
        # Simulation state
        self.is_running = False
        self.current_task = None
        self.simulation_start_time = None
        
    async def initialize_agents(self) -> bool:
        """Initialize all agents (4 coding + 1 commentator) with real Letta."""
        try:
            if not self.letta_config:
                self.logger.log_error("Letta configuration not available")
                return False
            
            # Get agent IDs from environment
            import os
            coding_agent_ids = [
                os.getenv("LETTA_CODING_AGENT_ID_1"),  # Frontend Specialist
                os.getenv("LETTA_CODING_AGENT_ID_2"),  # Backend Architect  
                os.getenv("LETTA_CODING_AGENT_ID_3"),  # DevOps Engineer
                os.getenv("LETTA_CODING_AGENT_ID_4"),  # Full-Stack Developer
            ]
            
            commentator_agent_id = os.getenv("LETTA_COMMENTATOR_AGENT_ID")
            
            if not all(coding_agent_ids) or not commentator_agent_id:
                print("Error: Missing agent IDs in environment variables")
                print("Available coding agent IDs:", [aid for aid in coding_agent_ids if aid])
                print("Commentator agent ID:", commentator_agent_id)
                return False
            
            # Create real Letta agents
            agent_names = ["Frontend Specialist", "Backend Architect", "DevOps Engineer", "Full-Stack Developer"]
            for i, agent_id in enumerate(coding_agent_ids):
                agent = RealLettaAgent(
                    agent_id=agent_id,
                    name=agent_names[i],
                    client=self.letta_config.client,
                    shared_memory=self.shared_memory,
                    message_broker=self.message_broker,
                    artifact_manager=self.artifact_manager,
                    logger=self.logger
                )
                self.coding_agents.append(agent)
                self.logger.log_agent_initialization(agent_id, agent_names[i], "coding")
            
            # Create commentator agent
            self.commentator_agent = RealLettaCommentatorAgent(
                agent_id=commentator_agent_id,
                name="Project Narrator",
                client=self.letta_config.client,
                shared_memory=self.shared_memory,
                message_broker=self.message_broker,
                artifact_manager=self.artifact_manager,
                coding_agents=self.coding_agents,
                logger=self.logger
            )
            self.logger.log_agent_initialization(commentator_agent_id, "Project Narrator", "commentator")
            
            print(f"✅ Initialized {len(self.coding_agents)} coding agents and 1 commentator agent with real Letta")
            return True
            
        except Exception as e:
            print(f"Error initializing agents: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def distribute_task(self, user_prompt: str) -> Dict[str, Any]:
        """
        Break down the user task and distribute it among agents.
        """
        try:
            self.current_task = user_prompt
            self.logger.log_session_start(user_prompt)
            
            # Set the task in shared memory
            await self.shared_memory.set_current_task(user_prompt)
            
            # Break down the task into subtasks for each agent
            subtasks = await self._break_down_task(user_prompt)
            
            # Distribute subtasks to agents
            task_distribution = {}
            for i, agent in enumerate(self.coding_agents):
                if i < len(subtasks):
                    task_distribution[agent.agent_config.agent_id] = subtasks[i]
                else:
                    task_distribution[agent.agent_config.agent_id] = "Work on general aspects of the project"
            
            # Store task distribution in shared memory
            await self.shared_memory.write("task_distribution", task_distribution)
            
            # Log task distribution
            self.logger.log_task_distribution(task_distribution)
            
            return {
                "success": True,
                "original_task": user_prompt,
                "subtasks": subtasks,
                "distribution": task_distribution
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _break_down_task(self, task: str) -> List[str]:
        """
        Break down a high-level task into subtasks for individual agents.
        This is a simple implementation - could be enhanced with AI.
        """
        # Simple task breakdown based on common patterns
        task_lower = task.lower()
        
        subtasks = []
        
        if "web" in task_lower or "website" in task_lower or "frontend" in task_lower:
            subtasks.extend([
                "Design and implement the user interface and user experience",
                "Set up the backend API and data management systems",
                "Configure deployment and infrastructure setup",
                "Implement testing and quality assurance features"
            ])
        elif "app" in task_lower or "application" in task_lower:
            subtasks.extend([
                "Design the application architecture and user interface",
                "Implement core business logic and data processing",
                "Set up development and deployment pipelines",
                "Create comprehensive testing and documentation"
            ])
        elif "api" in task_lower or "service" in task_lower:
            subtasks.extend([
                "Design the API structure and endpoints",
                "Implement the core service logic and data handling",
                "Set up monitoring, logging, and deployment infrastructure",
                "Create API documentation and testing suite"
            ])
        else:
            # Generic breakdown
            subtasks.extend([
                "Analyze requirements and design the solution architecture",
                "Implement the core functionality and business logic",
                "Set up infrastructure, deployment, and monitoring",
                "Create documentation, tests, and quality assurance"
            ])
        
        return subtasks[:4]  # Ensure we don't exceed 4 agents
    
    async def start_simulation(self) -> Dict[str, Any]:
        """
        Start the agent simulation.
        All agents begin working on their assigned tasks.
        """
        try:
            if not self.coding_agents or not self.commentator_agent:
                return {
                    "success": False,
                    "error": "Agents not initialized. Call initialize_agents() first."
                }
            
            self.is_running = True
            self.simulation_start_time = datetime.now()
            
            # Start commentator first
            await self.commentator_agent.start_observing()
            
            # Start all coding agents
            agent_tasks = []
            for agent in self.coding_agents:
                task_distribution = await self.shared_memory.read("task_distribution")
                agent_task = task_distribution.get(agent.agent_config.agent_id, "Work on assigned project tasks")
                
                # Start agent work asynchronously
                task = asyncio.create_task(agent.work_on_task(agent_task))
                agent_tasks.append(task)
            
            # Wait for all agents to complete
            results = await asyncio.gather(*agent_tasks, return_exceptions=True)
            
            # Stop commentator
            await self.commentator_agent.stop_observing()
            
            self.is_running = False
            
            return {
                "success": True,
                "simulation_duration": (datetime.now() - self.simulation_start_time).total_seconds(),
                "agent_results": results
            }
            
        except Exception as e:
            self.is_running = False
            return {
                "success": False,
                "error": str(e)
            }
    
    async def monitor_progress(self) -> Dict[str, Any]:
        """Monitor the current progress of all agents."""
        try:
            progress = {
                "timestamp": datetime.now().isoformat(),
                "is_running": self.is_running,
                "agents": {},
                "overall_status": "unknown"
            }
            
            # Get status from all coding agents
            for agent in self.coding_agents:
                status = await agent.get_status()
                progress["agents"][agent.agent_config.agent_id] = status
            
            # Get commentator status
            if self.commentator_agent:
                progress["commentator"] = await self.commentator_agent.get_status()
            
            # Determine overall status
            agent_statuses = [agent.get("is_working", False) for agent in progress["agents"].values()]
            if all(not status for status in agent_statuses):
                progress["overall_status"] = "completed"
            elif any(agent_statuses):
                progress["overall_status"] = "in_progress"
            else:
                progress["overall_status"] = "not_started"
            
            return progress
            
        except Exception as e:
            return {
                "error": str(e)
            }
    
    async def handle_agent_messages(self) -> Dict[str, Any]:
        """Handle and process messages between agents."""
        try:
            # Get all recent messages
            all_messages = await self.message_broker.get_all_messages()
            recent_messages = all_messages[-20:] if len(all_messages) > 20 else all_messages
            
            # Process messages (could add logic here for message handling)
            message_summary = {
                "total_messages": len(all_messages),
                "recent_messages": len(recent_messages),
                "message_types": {}
            }
            
            # Count message types
            for message in recent_messages:
                msg_type = message.message_type.value
                message_summary["message_types"][msg_type] = message_summary["message_types"].get(msg_type, 0) + 1
            
            return message_summary
            
        except Exception as e:
            return {
                "error": str(e)
            }
    
    async def get_artifacts_summary(self) -> Dict[str, Any]:
        """Get a summary of all artifacts created by agents."""
        try:
            summary = {
                "timestamp": datetime.now().isoformat(),
                "agents": {}
            }
            
            for agent in self.coding_agents:
                agent_artifacts = await self.artifact_manager.get_agent_artifacts(agent.agent_config.agent_id)
                summary["agents"][agent.agent_config.agent_id] = {
                    "name": agent.agent_config.name,
                    "artifact_count": len(agent_artifacts),
                    "artifacts": [artifact.to_dict() for artifact in agent_artifacts]
                }
            
            return summary
            
        except Exception as e:
            return {
                "error": str(e)
            }
    
    async def get_project_overview(self) -> Dict[str, Any]:
        """Get a comprehensive overview of the entire project."""
        try:
            if not self.commentator_agent:
                return {"error": "Commentator agent not available"}
            
            overview = await self.commentator_agent.get_project_overview()
            return overview
            
        except Exception as e:
            return {
                "error": str(e)
            }
    
    async def stop_simulation(self) -> Dict[str, Any]:
        """Stop the current simulation."""
        try:
            self.is_running = False
            
            # Stop all agents
            for agent in self.coding_agents:
                await agent.stop_working()
            
            if self.commentator_agent:
                await self.commentator_agent.stop_observing()
            
            return {
                "success": True,
                "message": "Simulation stopped",
                "stopped_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_simulation_status(self) -> Dict[str, Any]:
        """Get the current status of the simulation."""
        return {
            "is_running": self.is_running,
            "current_task": self.current_task,
            "simulation_start_time": self.simulation_start_time.isoformat() if self.simulation_start_time else None,
            "agents_initialized": len(self.coding_agents) > 0 and self.commentator_agent is not None,
            "coding_agents_count": len(self.coding_agents),
            "commentator_available": self.commentator_agent is not None
        }
