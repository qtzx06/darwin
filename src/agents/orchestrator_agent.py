"""
Orchestration Agent - Splits main tasks into specific subtasks and coordinates the team.
"""

import asyncio
import json
from typing import List, Dict, Any
from dataclasses import dataclass
from letta_client import Letta

@dataclass
class Subtask:
    """Represents a specific subtask for an agent."""
    id: str
    title: str
    description: str
    assigned_agent: str
    dependencies: List[str] = None
    status: str = "pending"  # pending, in_progress, completed, blocked
    priority: int = 1  # 1 = high, 2 = medium, 3 = low

class OrchestrationAgent:
    """Orchestrates the team by breaking down tasks and coordinating work."""
    
    def __init__(self, client: Letta, agent_id: str, logger):
        self.client = client
        self.agent_id = agent_id
        self.logger = logger
        self.subtasks: List[Subtask] = []
        self.current_phase = "planning"
        
    async def orchestrate_project(self, main_task: str, agents: List[Any]) -> List[Subtask]:
        """Break down the main task into specific subtasks and assign them to agents."""
        print(f"🎯 Orchestrator: Breaking down task: {main_task}")
        
        # Generate subtasks using Letta
        subtasks_prompt = f"""
You are a technical project manager. Break down this task into specific, actionable subtasks:

MAIN TASK: {main_task}

Available agents:
- Alex The Hacker: Frontend/Backend, React/Node.js, loves clean code
- Dr Sarah The Nerd: Backend/Architecture, TypeScript, loves documentation  
- Jake The Speed Demon: Frontend/Performance, React/Next.js, loves optimization
- Maya The Artist: Frontend/UI, React/CSS, loves beautiful design

Create 4-6 specific subtasks that can be worked on in parallel or sequence.
Each subtask should be:
1. Specific and actionable
2. Assigned to the most suitable agent
3. Have clear deliverables
4. Include technical requirements

Format as JSON:
{{
  "subtasks": [
    {{
      "title": "Subtask title",
      "description": "Detailed description with technical requirements",
      "assigned_agent": "Agent name",
      "priority": 1,
      "dependencies": []
    }}
  ]
}}
"""
        
        try:
            # Add timeout to prevent hanging
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self.client.agents.messages.create(
                        agent_id=self.agent_id,
                        messages=[{"role": "user", "content": subtasks_prompt}]
                    )
                ),
                timeout=30.0  # 30 second timeout
            )
            
            # Extract subtasks from response
            subtasks_data = self._extract_subtasks_from_response(response)
            self.subtasks = self._create_subtask_objects(subtasks_data, agents)
            
            print(f"✅ Orchestrator: Created {len(self.subtasks)} subtasks")
            for i, subtask in enumerate(self.subtasks, 1):
                print(f"  {i}. {subtask.title} → {subtask.assigned_agent}")
            
            return self.subtasks
            
        except asyncio.TimeoutError:
            print(f"⏰ Orchestrator: Letta API timeout, using fallback subtasks")
            return self._create_fallback_subtasks(main_task, agents)
        except Exception as e:
            print(f"❌ Orchestrator error: {e}")
            # Fallback: create basic subtasks
            return self._create_fallback_subtasks(main_task, agents)
    
    def _extract_subtasks_from_response(self, response) -> List[Dict]:
        """Extract subtasks from Letta response."""
        try:
            for msg in response.messages:
                if hasattr(msg, 'content'):
                    content = msg.content.strip()
                    # Try to find JSON in the response
                    if '{' in content and '}' in content:
                        # Find the JSON part
                        start = content.find('{')
                        end = content.rfind('}') + 1
                        json_str = content[start:end]
                        data = json.loads(json_str)
                        return data.get('subtasks', [])
        except Exception as e:
            print(f"❌ Error parsing subtasks: {e}")
        
        return []
    
    def _create_subtask_objects(self, subtasks_data: List[Dict], agents: List[Any]) -> List[Subtask]:
        """Create Subtask objects from parsed data."""
        subtasks = []
        agent_names = {agent.name: agent for agent in agents}
        
        for i, data in enumerate(subtasks_data):
            # Find the assigned agent
            assigned_agent = None
            for agent in agents:
                if agent.name in data.get('assigned_agent', ''):
                    assigned_agent = agent
                    break
            
            if not assigned_agent:
                # Default to first agent if not found
                assigned_agent = agents[0]
            
            subtask = Subtask(
                id=f"subtask_{i+1}",
                title=data.get('title', f'Subtask {i+1}'),
                description=data.get('description', ''),
                assigned_agent=assigned_agent.agent_id,
                priority=data.get('priority', 1),
                dependencies=data.get('dependencies', [])
            )
            subtasks.append(subtask)
        
        return subtasks
    
    def _create_fallback_subtasks(self, main_task: str, agents: List[Any]) -> List[Subtask]:
        """Create basic fallback subtasks if Letta fails."""
        subtasks = []
        
        # Basic subtasks for a fullstack app
        basic_tasks = [
            ("Frontend Setup", "Set up React frontend with routing and basic components", agents[0]),
            ("Backend API", "Create Node.js backend with REST API endpoints", agents[1]),
            ("Database Design", "Design and implement database schema", agents[2]),
            ("UI/UX Implementation", "Create beautiful, responsive user interface", agents[3])
        ]
        
        for i, (title, desc, agent) in enumerate(basic_tasks):
            subtask = Subtask(
                id=f"subtask_{i+1}",
                title=title,
                description=desc,
                assigned_agent=agent.agent_id,
                priority=1
            )
            subtasks.append(subtask)
        
        return subtasks
    
    async def get_next_subtask(self, agent_id: str) -> Subtask:
        """Get the next available subtask for an agent."""
        for subtask in self.subtasks:
            if (subtask.assigned_agent == agent_id and 
                subtask.status == "pending" and
                not self._has_blocking_dependencies(subtask)):
                return subtask
        return None
    
    def _has_blocking_dependencies(self, subtask: Subtask) -> bool:
        """Check if subtask has uncompleted dependencies."""
        if not subtask.dependencies:
            return False
        
        for dep_id in subtask.dependencies:
            dep_subtask = next((s for s in self.subtasks if s.id == dep_id), None)
            if dep_subtask and dep_subtask.status != "completed":
                return True
        return False
    
    def mark_subtask_completed(self, subtask_id: str):
        """Mark a subtask as completed."""
        for subtask in self.subtasks:
            if subtask.id == subtask_id:
                subtask.status = "completed"
                print(f"✅ Orchestrator: {subtask.title} completed!")
                break
    
    def get_project_status(self) -> Dict[str, Any]:
        """Get current project status."""
        completed = sum(1 for s in self.subtasks if s.status == "completed")
        total = len(self.subtasks)
        
        return {
            "total_subtasks": total,
            "completed_subtasks": completed,
            "progress_percentage": (completed / total * 100) if total > 0 else 0,
            "current_phase": self.current_phase,
            "subtasks": [
                {
                    "id": s.id,
                    "title": s.title,
                    "assigned_agent": s.assigned_agent,
                    "status": s.status,
                    "priority": s.priority
                }
                for s in self.subtasks
            ]
        }
