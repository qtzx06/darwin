"""
Orchestrator Agent - Breaks down main tasks into subtasks for competitive workflow.
"""

import asyncio
import json
import time
from typing import List, Dict, Any
from dataclasses import dataclass
from letta_client import Letta

@dataclass
class Subtask:
    """Represents a subtask for competitive work."""
    id: str
    title: str
    description: str
    round_num: int
    status: str = "pending"  # pending, in_progress, completed

class OrchestrationAgent:
    """Orchestrator agent that breaks down tasks into subtasks."""
    
    def __init__(self, client: Letta, agent_id: str, logger):
        self.client = client
        self.agent_id = agent_id
        self.logger = logger
        self.name = "Orchestrator"
        self.subtasks = []
        self.project_status = {
            "total_subtasks": 0,
            "completed_subtasks": 0,
            "progress_percentage": 0.0
        }
    
    async def orchestrate_project(self, main_task: str, agents: List[Any]) -> List[Subtask]:
        """Breaks down a main task into subtasks using Letta AI."""
        print(f"\n🎯 ORCHESTRATOR: Analyzing project with Letta AI: {main_task}")
        
        try:
            # Use Letta API to intelligently break down the project
            subtasks_data = await self._letta_orchestrate_project(main_task)
            
            # Convert to Subtask objects
            self.subtasks = []
            for i, subtask_data in enumerate(subtasks_data, 1):
                subtask = Subtask(
                    id=f"subtask_{i}",
                    title=subtask_data["title"],
                    description=subtask_data["description"],
                    round_num=i
                )
                self.subtasks.append(subtask)
            
            # Update project status
            self.project_status["total_subtasks"] = len(self.subtasks)
            self.project_status["completed_subtasks"] = 0
            self.project_status["progress_percentage"] = 0.0
            
            print(f"✅ ORCHESTRATOR: Created {len(self.subtasks)} subtasks:")
            for subtask in self.subtasks:
                print(f"  • {subtask.title}: {subtask.description}")
            
            return self.subtasks
            
        except Exception as e:
            print(f"❌ ORCHESTRATOR: Letta orchestration failed: {e}")
            print("🔄 Falling back to default subtasks...")
            
            # Fallback to default subtasks
            subtasks_data = self._create_subtasks_for_project(main_task)
            
            # Convert to Subtask objects
            self.subtasks = []
            for i, subtask_data in enumerate(subtasks_data, 1):
                subtask = Subtask(
                    id=f"subtask_{i}",
                    title=subtask_data["title"],
                    description=subtask_data["description"],
                    round_num=i
                )
                self.subtasks.append(subtask)
            
            self.project_status["total_subtasks"] = len(self.subtasks)
            self.project_status["completed_subtasks"] = 0
            self.project_status["progress_percentage"] = 0.0
            
            print(f"✅ ORCHESTRATOR: Created {len(self.subtasks)} fallback subtasks")
            for i, subtask in enumerate(self.subtasks, 1):
                print(f"  {i}. {subtask.title}")
            
            return self.subtasks
    
    async def _letta_orchestrate_project(self, main_task: str) -> List[Dict[str, Any]]:
        """Use Letta AI to intelligently break down a project into subtasks."""
        orchestration_prompt = f"""
🎯 SIMPLE PROJECT BREAKDOWN REQUEST 🎯

You are an expert project manager. Break down this project into 3-4 SIMPLE, EASY subtasks.

PROJECT DESCRIPTION:
{main_task}

REQUIREMENTS:
1. Each subtask should be VERY SIMPLE and achievable in 5-10 minutes
2. Focus on basic functionality only
3. No complex architecture or deployment
4. Just basic React components and simple features
5. Make it EASY for coding agents to complete

EXAMPLES OF SIMPLE SUBTASKS:
- "Create a basic counter component"
- "Add increment and decrement buttons"
- "Add a reset button"
- "Style the counter with basic CSS"

OUTPUT FORMAT:
Return ONLY a JSON array with this exact structure:
[
  {{
    "title": "Simple Subtask Title",
    "description": "Very simple description of what to build"
  }}
]

IMPORTANT: Keep it SIMPLE! No complex backend, no authentication, no deployment!
Return ONLY the JSON array, no other text.
"""
        
        try:
            # Call Letta API with timeout
            response = self.client.agents.messages.create(
                agent_id=self.agent_id,
                messages=[{"role": "user", "content": orchestration_prompt}]
            )
            
            # Extract response content
            response_text = ""
            for msg in response.messages:
                if hasattr(msg, 'content'):
                    response_text = msg.content.strip()
                    break
            
            if not response_text:
                raise Exception("Empty response from Letta API")
            
            # Parse JSON response
            subtasks_data = json.loads(response_text)
            
            # Validate structure
            if not isinstance(subtasks_data, list):
                raise Exception("Response is not a JSON array")
            
            for subtask in subtasks_data:
                if not isinstance(subtask, dict) or "title" not in subtask or "description" not in subtask:
                    raise Exception("Invalid subtask structure")
            
            print(f"✅ ORCHESTRATOR: Letta AI created {len(subtasks_data)} intelligent subtasks")
            return subtasks_data
            
        except asyncio.TimeoutError:
            raise Exception("Letta API timeout - orchestration took too long")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response from Letta: {e}")
        except Exception as e:
            raise Exception(f"Letta orchestration failed: {e}")
    
    def _create_subtasks_for_project(self, main_task: str) -> List[Dict[str, Any]]:
        """Create subtasks based on the main task description."""
        task_lower = main_task.lower()
        
        if "todo" in task_lower:
            return [
                {
                    "title": "Create Todo Component",
                    "description": "Build a React component for displaying and managing todo items with add, edit, delete functionality"
                },
                {
                    "title": "Add State Management",
                    "description": "Implement state management for todo items using React hooks or context"
                },
                {
                    "title": "Add Styling and UI",
                    "description": "Style the todo component with beautiful UI and responsive design"
                },
                {
                    "title": "Add Backend API",
                    "description": "Create a simple backend API for persisting todo items"
                }
            ]
        elif "blog" in task_lower:
            return [
                {
                    "title": "Create Blog Post Component",
                    "description": "Build a React component for displaying blog posts with title, content, and metadata"
                },
                {
                    "title": "Add Post Management",
                    "description": "Implement functionality to create, edit, and delete blog posts"
                },
                {
                    "title": "Add Comment System",
                    "description": "Create a comment system for blog posts with nested replies"
                },
                {
                    "title": "Add Authentication",
                    "description": "Implement user authentication and authorization for blog management"
                }
            ]
        elif "landing" in task_lower or "page" in task_lower:
            return [
                {
                    "title": "Create Hero Section",
                    "description": "Build the main hero section with compelling headline, subtext, and call-to-action"
                },
                {
                    "title": "Add Feature Sections",
                    "description": "Create feature sections highlighting key benefits and functionality"
                },
                {
                    "title": "Add Navigation and Footer",
                    "description": "Implement responsive navigation header and footer with links"
                },
                {
                    "title": "Add Styling and Animations",
                    "description": "Style the landing page with modern design, animations, and responsive layout"
                }
            ]
        elif "counter" in task_lower:
            return [
                {
                    "title": "Create Counter Component",
                    "description": "Build a React counter component with increment, decrement, and reset functionality"
                },
                {
                    "title": "Add State Management",
                    "description": "Implement state management for counter value using React hooks"
                },
                {
                    "title": "Add Styling and UI",
                    "description": "Style the counter with beautiful buttons and responsive design"
                },
                {
                    "title": "Add Advanced Features",
                    "description": "Add features like step increment, keyboard shortcuts, and persistence"
                }
            ]
        else:
            # Generic subtasks for any project
            return [
                {
                    "title": "Create Main Component",
                    "description": "Build the main React component for the application"
                },
                {
                    "title": "Add Core Features",
                    "description": "Implement the core functionality and features"
                },
                {
                    "title": "Add Styling",
                    "description": "Style the application with modern UI/UX"
                },
                {
                    "title": "Add Backend Integration",
                    "description": "Connect to backend services and APIs"
                }
            ]
    
    def mark_subtask_completed(self, subtask_id: str):
        """Mark a subtask as completed."""
        for subtask in self.subtasks:
            if subtask.id == subtask_id:
                subtask.status = "completed"
                self.project_status["completed_subtasks"] += 1
                self.project_status["progress_percentage"] = (
                    self.project_status["completed_subtasks"] / 
                    self.project_status["total_subtasks"] * 100
                )
                print(f"✅ Orchestrator: Completed {subtask.title}")
                break
    
    def get_project_status(self) -> Dict[str, Any]:
        """Get current project status."""
        return self.project_status.copy()
    
    def get_current_subtask(self) -> Subtask:
        """Get the current subtask being worked on."""
        for subtask in self.subtasks:
            if subtask.status == "pending":
                return subtask
        return None
    
    def get_remaining_subtasks(self) -> List[Subtask]:
        """Get all remaining subtasks."""
        return [subtask for subtask in self.subtasks if subtask.status == "pending"]
    
    def get_completed_subtasks(self) -> List[Subtask]:
        """Get all completed subtasks."""
        return [subtask for subtask in self.subtasks if subtask.status == "completed"]
