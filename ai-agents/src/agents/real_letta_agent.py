"""
Real Letta agent wrapper for the PM simulator.
This class wraps actual Letta agents and provides the interface expected by the coordinator.
"""
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime

from ..core.shared_memory import SharedMemory
from ..core.message_system import MessageBroker, MessageType
from ..artifacts.artifact_manager import ArtifactManager


class RealLettaAgent:
    """
    Wrapper for real Letta agents that provides the interface expected by the coordinator.
    """
    
    def __init__(
        self, 
        agent_id: str,
        name: str,
        client,
        shared_memory: SharedMemory,
        message_broker: MessageBroker,
        artifact_manager: ArtifactManager,
        logger=None
    ):
        self.agent_id = agent_id
        self.name = name
        self.client = client
        self.shared_memory = shared_memory
        self.message_broker = message_broker
        self.artifact_manager = artifact_manager
        self.logger = logger
        
        # Add compatibility attributes
        self.agent_config = type('AgentConfig', (), {
            'agent_id': agent_id,
            'name': name,
            'personality': f"I am {name}, specialized in my field."
        })()
        
        # Agent state
        self.is_working = False
        self.current_task = None
        self.current_artifact_id = None
        self.work_summary = ""
    
    async def work_on_task(self, task_description: str) -> Dict[str, Any]:
        """
        Main work loop for the agent using real Letta.
        """
        try:
            print(f"[DEBUG] {self.name} starting work on: {task_description}")
            self.is_working = True
            self.current_task = task_description
            
            if self.logger:
                self.logger.log_agent_activity(self.agent_id, "Starting work on task", {
                    "task": task_description
                })
            
            # Update agent status in shared memory
            await self.shared_memory.update_agent_status(self.agent_id, {
                "status": "working",
                "current_task": task_description,
                "started_at": datetime.now().isoformat()
            })
            
            # Create initial artifact for this task
            from ..artifacts.artifact_manager import ArtifactType
            self.current_artifact_id = await self.artifact_manager.create_artifact(
                agent_id=self.agent_id,
                artifact_type=ArtifactType.CODE
            )
            
            if self.logger:
                self.logger.log_artifact_creation(
                    self.agent_id, 
                    self.current_artifact_id, 
                    "code", 
                    f"Initial artifact for: {task_description}"
                )
            
            # Send task to Letta agent
            print(f"[DEBUG] {self.name} calling Letta API...")
            try:
                # Run the synchronous Letta API call in a thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None, 
                    lambda: self.client.agents.messages.create(
                        agent_id=self.agent_id,
                        messages=[{"role": "user", "content": f"Task: {task_description}\n\nPlease work on this task and provide your solution. Focus on your specialization and create code/artifacts as needed."}]
                    )
                )
                print(f"[DEBUG] {self.name} got response from Letta API")
            except Exception as e:
                print(f"[DEBUG] {self.name} Letta API error: {e}")
                response = None
            
            # Process the response
            result = await self._process_letta_response(response)
            
            # Debug: Print the response content
            print(f"[DEBUG] {self.name} response content: {result.get('content', 'No content')[:200]}...")
            
            # Store the generated code in the artifact
            if result.get("content"):
                await self.artifact_manager.update_artifact(
                    agent_id=self.agent_id,
                    content={
                        "type": "code",
                        "language": "python",  # Could be detected from content
                        "code": result["content"],
                        "description": f"Generated code for: {task_description}",
                        "timestamp": datetime.now().isoformat()
                    },
                    artifact_id=self.current_artifact_id
                )
                
                if self.logger:
                    self.logger.log_artifact_update(
                        self.agent_id, 
                        self.current_artifact_id, 
                        "code_generated", 
                        result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"]
                    )
            else:
                print(f"[DEBUG] {self.name} - No content in response")
            
            # Generate work summary
            await self._generate_work_summary()
            
            # Update final status
            await self.shared_memory.update_agent_status(self.agent_id, {
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "result": result
            })
            
            if self.logger:
                self.logger.log_agent_activity(self.agent_id, "Completed task", {
                    "task": task_description,
                    "artifacts_created": result.get("messages_processed", 0),
                    "tools_used": result.get("tools_used", [])
                })
            
            self.is_working = False
            
            return {
                "success": True,
                "agent_id": self.agent_id,
                "task": task_description,
                "artifact_id": self.current_artifact_id,
                "result": result
            }
            
        except Exception as e:
            self.is_working = False
            await self.shared_memory.update_agent_status(self.agent_id, {
                "status": "error",
                "error": str(e),
                "error_at": datetime.now().isoformat()
            })
            
            return {
                "success": False,
                "agent_id": self.agent_id,
                "error": str(e)
            }
    
    async def _process_letta_response(self, response) -> Dict[str, Any]:
        """
        Process the response from Letta agent and extract useful information.
        """
        result = {
            "messages_processed": 0,
            "code_generated": False,
            "tools_used": [],
            "content": ""
        }
        
        for msg in response.messages:
            result["messages_processed"] += 1
            
            if msg.message_type == "assistant_message":
                result["content"] += msg.content + "\n"
                
                # Check if this looks like code
                if "```" in msg.content or "def " in msg.content or "function " in msg.content:
                    result["code_generated"] = True
                    
                    # Update artifact with the code
                    await self.artifact_manager.update_artifact(
                        agent_id=self.agent_id,
                        content={
                            "type": "code",
                            "language": "python",  # Default, could be detected
                            "code": msg.content,
                            "description": f"Generated code for: {self.current_task}",
                            "timestamp": datetime.now().isoformat()
                        },
                        artifact_id=self.current_artifact_id
                    )
            
            elif msg.message_type == "tool_call_message":
                if msg.tool_call.name:
                    result["tools_used"].append(msg.tool_call.name)
            
            elif msg.message_type == "tool_return_message":
                # Handle tool returns if needed
                pass
        
        return result
    
    async def generate_summary(self) -> str:
        """Generate a summary of current work progress."""
        try:
            # Get current artifact
            artifact = await self.artifact_manager.get_artifact(self.current_artifact_id)
            
            if artifact:
                summary = f"""
Agent: {self.name}
Task: {self.current_task}
Status: {'Working' if self.is_working else 'Completed'}
Artifact: {self.current_artifact_id}
Last Updated: {artifact.last_updated.isoformat()}
Content Type: {artifact.artifact_type}
"""
                
                if artifact.content.get("code"):
                    code_preview = artifact.content["code"][:200] + "..." if len(artifact.content["code"]) > 200 else artifact.content["code"]
                    summary += f"Code Preview:\n{code_preview}\n"
                
                self.work_summary = summary
                return summary
            else:
                return f"Agent {self.name}: No current work to summarize"
                
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    async def send_message_to_peer(self, agent_id: str, message: str, message_type: MessageType = MessageType.COORDINATION) -> str:
        """Send a message to another agent."""
        return await self.message_broker.send_message(
            from_agent=self.agent_id,
            to_agent=agent_id,
            content=message,
            message_type=message_type
        )
    
    async def update_artifact(self, content: Dict[str, Any]) -> str:
        """Update the current artifact with new content."""
        return await self.artifact_manager.update_artifact(
            agent_id=self.agent_id,
            content=content,
            artifact_id=self.current_artifact_id
        )
    
    async def access_shared_memory(self, key: str) -> Any:
        """Read from shared memory."""
        return await self.shared_memory.read(key)
    
    async def write_shared_memory(self, key: str, value: Any) -> None:
        """Write to shared memory."""
        await self.shared_memory.write(key, value)
    
    async def get_recent_messages(self, limit: int = 5) -> list:
        """Get recent messages for this agent."""
        messages = await self.message_broker.get_recent_messages(self.agent_id, limit)
        return [msg.to_dict() for msg in messages]
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "is_working": self.is_working,
            "current_task": self.current_task,
            "current_artifact_id": self.current_artifact_id,
            "work_summary": self.work_summary,
            "status": "working" if self.is_working else "idle"
        }
    
    async def stop_working(self):
        """Stop the agent's work."""
        self.is_working = False
        await self.shared_memory.update_agent_status(self.agent_id, {
            "status": "stopped",
            "stopped_at": datetime.now().isoformat()
        })


class RealLettaCommentatorAgent:
    """
    Real Letta commentator agent that observes and narrates development progress.
    """
    
    def __init__(
        self, 
        agent_id: str,
        name: str,
        client,
        shared_memory: SharedMemory,
        message_broker: MessageBroker,
        artifact_manager: ArtifactManager,
        coding_agents: list,
        logger=None
    ):
        self.agent_id = agent_id
        self.name = name
        self.client = client
        self.shared_memory = shared_memory
        self.message_broker = message_broker
        self.artifact_manager = artifact_manager
        self.coding_agents = coding_agents
        self.logger = logger
        
        # Commentator state
        self.is_observing = False
        self.commentary_history = []
        self.last_observation_time = None
    
    async def start_observing(self) -> None:
        """Start observing agent activities and providing commentary."""
        self.is_observing = True
        self.last_observation_time = datetime.now()
        
        await self.shared_memory.update_agent_status(self.agent_id, {
            "status": "observing",
            "started_observing": datetime.now().isoformat()
        })
        
        # Start observation loop
        asyncio.create_task(self._observation_loop())
    
    async def stop_observing(self) -> None:
        """Stop observing agent activities."""
        self.is_observing = False
        
        await self.shared_memory.update_agent_status(self.agent_id, {
            "status": "stopped",
            "stopped_observing": datetime.now().isoformat()
        })
    
    async def _observation_loop(self) -> None:
        """Main observation loop that monitors agent activities."""
        while self.is_observing:
            try:
                # Observe agent activities
                await self.observe_agents()
                
                # Generate commentary if there are updates
                commentary = await self.synthesize_update()
                if commentary:
                    await self.report_to_user(commentary)
                
                # Wait before next observation
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                print(f"Error in commentator observation loop: {e}")
                await asyncio.sleep(10)  # Wait longer on error
    
    async def observe_agents(self) -> Dict[str, Any]:
        """Observe all agent activities and collect information."""
        try:
            observation = {
                "timestamp": datetime.now().isoformat(),
                "agent_statuses": {},
                "recent_messages": [],
                "artifact_updates": {},
                "overall_progress": {}
            }
            
            # Check status of all coding agents
            for agent in self.coding_agents:
                agent_status = await agent.get_status()
                observation["agent_statuses"][agent.agent_id] = agent_status
                
                # Check for recent messages
                recent_messages = await agent.get_recent_messages(limit=3)
                observation["recent_messages"].extend(recent_messages)
                
                # Check artifact updates
                artifacts = await self.artifact_manager.get_agent_artifacts(agent.agent_id)
                if artifacts:
                    latest_artifact = max(artifacts, key=lambda a: a.last_updated)
                    observation["artifact_updates"][agent.agent_id] = {
                        "artifact_id": latest_artifact.id,
                        "type": latest_artifact.artifact_type,
                        "last_updated": latest_artifact.last_updated.isoformat()
                    }
            
            # Get overall progress from shared memory
            current_task = await self.shared_memory.get_current_task()
            if current_task:
                observation["overall_progress"] = {
                    "task": current_task.get("description", "Unknown task"),
                    "status": current_task.get("status", "unknown"),
                    "created_at": current_task.get("created_at", "")
                }
            
            # Store observation
            self.commentary_history.append(observation)
            
            # Keep only last 50 observations
            if len(self.commentary_history) > 50:
                self.commentary_history = self.commentary_history[-50:]
            
            return observation
            
        except Exception as e:
            print(f"Error observing agents: {e}")
            return {"error": str(e)}
    
    async def synthesize_update(self) -> Optional[str]:
        """Synthesize observations into engaging commentary."""
        try:
            if not self.commentary_history:
                return None
            
            latest_observation = self.commentary_history[-1]
            
            # Check if there are significant updates since last commentary
            if self.last_observation_time:
                recent_updates = [
                    obs for obs in self.commentary_history
                    if datetime.fromisoformat(obs["timestamp"]) > self.last_observation_time
                ]
                if not recent_updates:
                    return None
            
            # Generate commentary based on observations
            commentary = await self._generate_commentary(latest_observation)
            
            if commentary:
                self.last_observation_time = datetime.now()
                self.commentary_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "type": "commentary",
                    "content": commentary
                })
            
            return commentary
            
        except Exception as e:
            print(f"Error synthesizing update: {e}")
            return None
    
    async def _generate_commentary(self, observation: Dict[str, Any]) -> Optional[str]:
        """Generate commentary based on observation data."""
        try:
            # Analyze agent activities
            active_agents = []
            completed_agents = []
            error_agents = []
            
            for agent_id, status in observation.get("agent_statuses", {}).items():
                if status.get("is_working"):
                    active_agents.append(agent_id)
                elif status.get("status") == "completed":
                    completed_agents.append(agent_id)
                elif status.get("status") == "error":
                    error_agents.append(agent_id)
            
            # Generate commentary based on activity
            commentary_parts = []
            
            if active_agents:
                agent_names = [self._get_agent_name(aid) for aid in active_agents]
                commentary_parts.append(f"🎯 {', '.join(agent_names)} are actively working on their tasks")
            
            if completed_agents:
                agent_names = [self._get_agent_name(aid) for aid in completed_agents]
                commentary_parts.append(f"✅ {', '.join(agent_names)} have completed their work")
            
            if error_agents:
                agent_names = [self._get_agent_name(aid) for aid in error_agents]
                commentary_parts.append(f"⚠️ {', '.join(agent_names)} encountered some issues")
            
            # Check for inter-agent communication
            recent_messages = observation.get("recent_messages", [])
            if recent_messages:
                message_count = len(recent_messages)
                commentary_parts.append(f"💬 The team has been actively communicating ({message_count} recent messages)")
            
            # Check for artifact updates
            artifact_updates = observation.get("artifact_updates", {})
            if artifact_updates:
                update_count = len(artifact_updates)
                commentary_parts.append(f"📝 {update_count} agents have updated their artifacts")
            
            # Check overall progress
            overall_progress = observation.get("overall_progress", {})
            if overall_progress:
                task = overall_progress.get("task", "the project")
                status = overall_progress.get("status", "in progress")
                commentary_parts.append(f"📊 Overall project status: {status}")
            
            if commentary_parts:
                return " | ".join(commentary_parts)
            
            return None
            
        except Exception as e:
            print(f"Error generating commentary: {e}")
            return None
    
    def _get_agent_name(self, agent_id: str) -> str:
        """Get display name for agent ID."""
        agent_name_map = {
            "agent-f8748261-ed3b-46a5-922b-833b16ae0878": "Frontend Specialist",
            "agent-080437d1-83d3-4c74-83d6-71741ce36cd3": "Backend Architect", 
            "agent-aa65ae8b-be7a-49c4-a36e-728efcaf09bb": "DevOps Engineer",
            "agent-11e3c16e-b130-4338-b9b4-efbcf57d581c": "Full-Stack Developer"
        }
        return agent_name_map.get(agent_id, agent_id)
    
    async def report_to_user(self, text: str) -> None:
        """Report commentary to the user."""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] 🎙️  Commentator: {text}")
            
            # Store in shared memory for potential web UI consumption
            await self.shared_memory.write(
                f"commentator_latest",
                {
                    "text": text,
                    "timestamp": datetime.now().isoformat(),
                    "type": "commentary"
                }
            )
            
        except Exception as e:
            print(f"Error reporting to user: {e}")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current commentator status."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "is_observing": self.is_observing,
            "commentary_count": len(self.commentary_history),
            "last_observation": self.last_observation_time.isoformat() if self.last_observation_time else None
        }
    
    async def get_project_overview(self) -> Dict[str, Any]:
        """Get a comprehensive overview of the entire project."""
        try:
            overview = {
                "timestamp": datetime.now().isoformat(),
                "agents": {},
                "artifacts": {},
                "messages": {},
                "overall_status": "unknown"
            }
            
            # Get agent statuses and summaries
            for agent in self.coding_agents:
                status = await agent.get_status()
                summary = await agent.generate_summary()
                
                overview["agents"][agent.agent_id] = {
                    "name": agent.name,
                    "status": status,
                    "summary": summary
                }
            
            # Get artifact summaries
            for agent in self.coding_agents:
                artifacts = await self.artifact_manager.get_agent_artifacts(agent.agent_id)
                overview["artifacts"][agent.agent_id] = {
                    "count": len(artifacts),
                    "latest": artifacts[-1].to_dict() if artifacts else None
                }
            
            # Get message statistics
            message_stats = await self.message_broker.get_message_stats()
            overview["messages"] = message_stats
            
            # Determine overall status
            agent_statuses = [agent.get("status", {}).get("status", "unknown") for agent in overview["agents"].values()]
            if all(status == "completed" for status in agent_statuses):
                overview["overall_status"] = "completed"
            elif any(status == "working" for status in agent_statuses):
                overview["overall_status"] = "in_progress"
            elif any(status == "error" for status in agent_statuses):
                overview["overall_status"] = "error"
            
            return overview
            
        except Exception as e:
            return {"error": str(e)}
