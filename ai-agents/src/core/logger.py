"""
Logging system for the Letta AI Agent PM Simulator.
Captures agent activities, messages, artifacts, and system events.
"""
import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

class PMSimulatorLogger:
    """Centralized logging for the PM Simulator."""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create timestamped log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"pm_simulator_{timestamp}.log"
        self.session_file = self.log_dir / f"session_{timestamp}.json"
        
        # Setup logging
        self._setup_logging()
        
        # Session data
        self.session_data = {
            "session_id": f"session_{timestamp}",
            "start_time": datetime.now().isoformat(),
            "agents": {},
            "tasks": [],
            "artifacts": [],
            "messages": [],
            "events": []
        }
    
    def _setup_logging(self):
        """Setup the logging configuration."""
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Setup file handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Setup console handler - DISABLED (only commentator should print)
        # console_handler = logging.StreamHandler()
        # console_handler.setLevel(logging.INFO)
        # console_handler.setFormatter(formatter)
        
        # Setup root logger
        self.logger = logging.getLogger('pm_simulator')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        # self.logger.addHandler(console_handler)  # DISABLED - only file logging
        
        # Prevent duplicate logs
        self.logger.propagate = False
    
    def log_session_start(self, project_description: str):
        """Log the start of a new simulation session."""
        self.session_data["project_description"] = project_description
        self.logger.info(f"Starting PM Simulator Session")
        self.logger.info(f"Project: {project_description}")
        self._save_session_data()
    
    def log_agent_initialization(self, agent_id: str, agent_name: str, agent_type: str):
        """Log agent initialization."""
        self.session_data["agents"][agent_id] = {
            "name": agent_name,
            "type": agent_type,
            "initialized_at": datetime.now().isoformat(),
            "activities": [],
            "artifacts_created": 0,
            "messages_sent": 0,
            "messages_received": 0
        }
        
        self.logger.info(f"🤖 Initialized {agent_type}: {agent_name} ({agent_id})")
        self._save_session_data()
    
    def log_task_distribution(self, tasks: Dict[str, str]):
        """Log task distribution to agents."""
        self.session_data["tasks"] = [
            {
                "agent_id": agent_id,
                "task": task,
                "assigned_at": datetime.now().isoformat(),
                "status": "assigned"
            }
            for agent_id, task in tasks.items()
        ]
        
        self.logger.info("📝 Task Distribution:")
        for agent_id, task in tasks.items():
            agent_name = self.session_data["agents"].get(agent_id, {}).get("name", agent_id)
            self.logger.info(f"  • {agent_name}: {task}")
        
        self._save_session_data()
    
    def log_agent_activity(self, agent_id: str, activity: str, details: Dict[str, Any] = None):
        """Log agent activity."""
        timestamp = datetime.now().isoformat()
        
        activity_log = {
            "timestamp": timestamp,
            "activity": activity,
            "details": details or {}
        }
        
        if agent_id in self.session_data["agents"]:
            self.session_data["agents"][agent_id]["activities"].append(activity_log)
        
        agent_name = self.session_data["agents"].get(agent_id, {}).get("name", agent_id)
        self.logger.info(f"{agent_name}: {activity}")
        
        if details:
            for key, value in details.items():
                self.logger.debug(f"    {key}: {value}")
        
        self._save_session_data()
    
    def log_agent_message(self, from_agent: str, to_agent: str, content: str, message_type: str = "agent_to_agent"):
        """Log inter-agent communication."""
        timestamp = datetime.now().isoformat()
        
        message_log = {
            "timestamp": timestamp,
            "from_agent": from_agent,
            "to_agent": to_agent,
            "content": content,
            "type": message_type
        }
        
        self.session_data["messages"].append(message_log)
        
        # Update agent message counts
        if from_agent in self.session_data["agents"]:
            self.session_data["agents"][from_agent]["messages_sent"] += 1
        if to_agent in self.session_data["agents"]:
            self.session_data["agents"][to_agent]["messages_received"] += 1
        
        from_name = self.session_data["agents"].get(from_agent, {}).get("name", from_agent)
        to_name = self.session_data["agents"].get(to_agent, {}).get("name", to_agent)
        
        self.logger.info(f"💬 {from_name} → {to_name}: {content[:100]}{'...' if len(content) > 100 else ''}")
        self._save_session_data()
    
    def log_artifact_creation(self, agent_id: str, artifact_id: str, artifact_type: str, description: str = ""):
        """Log artifact creation."""
        timestamp = datetime.now().isoformat()
        
        artifact_log = {
            "timestamp": timestamp,
            "agent_id": agent_id,
            "artifact_id": artifact_id,
            "type": artifact_type,
            "description": description
        }
        
        self.session_data["artifacts"].append(artifact_log)
        
        # Update agent artifact count
        if agent_id in self.session_data["agents"]:
            self.session_data["agents"][agent_id]["artifacts_created"] += 1
        
        agent_name = self.session_data["agents"].get(agent_id, {}).get("name", agent_id)
        self.logger.info(f"{agent_name} created {artifact_type} artifact: {artifact_id}")
        
        if description:
            self.logger.debug(f"    Description: {description}")
        
        self._save_session_data()
    
    def log_artifact_update(self, agent_id: str, artifact_id: str, update_type: str, content_preview: str = ""):
        """Log artifact updates."""
        agent_name = self.session_data["agents"].get(agent_id, {}).get("name", agent_id)
        self.logger.info(f"{agent_name} updated artifact {artifact_id}: {update_type}")
        
        if content_preview:
            self.logger.debug(f"    Preview: {content_preview[:200]}{'...' if len(content_preview) > 200 else ''}")
    
    def log_commentator_narration(self, content: str):
        """Log commentator narration."""
        timestamp = datetime.now().isoformat()
        
        narration_log = {
            "timestamp": timestamp,
            "type": "commentator_narration",
            "content": content
        }
        
        self.session_data["events"].append(narration_log)
        self.logger.info(f"Commentator: {content}")
        self._save_session_data()
    
    def log_system_event(self, event: str, details: Dict[str, Any] = None):
        """Log system events."""
        timestamp = datetime.now().isoformat()
        
        event_log = {
            "timestamp": timestamp,
            "type": "system_event",
            "event": event,
            "details": details or {}
        }
        
        self.session_data["events"].append(event_log)
        self.logger.info(f"⚙️  System: {event}")
        
        if details:
            for key, value in details.items():
                self.logger.debug(f"    {key}: {value}")
        
        self._save_session_data()
    
    def log_error(self, error: str, details: Dict[str, Any] = None):
        """Log errors."""
        timestamp = datetime.now().isoformat()
        
        error_log = {
            "timestamp": timestamp,
            "type": "error",
            "error": error,
            "details": details or {}
        }
        
        self.session_data["events"].append(error_log)
        self.logger.error(f"❌ Error: {error}")
        
        if details:
            for key, value in details.items():
                self.logger.error(f"    {key}: {value}")
        
        self._save_session_data()
    
    def log_session_end(self, status: str = "completed"):
        """Log the end of a simulation session."""
        self.session_data["end_time"] = datetime.now().isoformat()
        self.session_data["final_status"] = status
        
        # Calculate session statistics
        total_artifacts = sum(agent.get("artifacts_created", 0) for agent in self.session_data["agents"].values())
        total_messages = len(self.session_data["messages"])
        total_events = len(self.session_data["events"])
        
        self.logger.info(f"🏁 Session {status}")
        self.logger.info(f"📊 Statistics:")
        self.logger.info(f"  • Agents: {len(self.session_data['agents'])}")
        self.logger.info(f"  • Artifacts: {total_artifacts}")
        self.logger.info(f"  • Messages: {total_messages}")
        self.logger.info(f"  • Events: {total_events}")
        
        self._save_session_data()
    
    def _save_session_data(self):
        """Save session data to JSON file."""
        try:
            with open(self.session_file, 'w') as f:
                json.dump(self.session_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save session data: {e}")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of the current session."""
        return {
            "session_id": self.session_data["session_id"],
            "project": self.session_data.get("project_description", "Unknown"),
            "agents": len(self.session_data["agents"]),
            "artifacts": len(self.session_data["artifacts"]),
            "messages": len(self.session_data["messages"]),
            "events": len(self.session_data["events"]),
            "log_file": str(self.log_file),
            "session_file": str(self.session_file)
        }
    
    def get_agent_summary(self, agent_id: str) -> Dict[str, Any]:
        """Get summary for a specific agent."""
        if agent_id not in self.session_data["agents"]:
            return {}
        
        agent_data = self.session_data["agents"][agent_id]
        return {
            "name": agent_data["name"],
            "type": agent_data["type"],
            "activities": len(agent_data["activities"]),
            "artifacts_created": agent_data["artifacts_created"],
            "messages_sent": agent_data["messages_sent"],
            "messages_received": agent_data["messages_received"],
            "last_activity": agent_data["activities"][-1]["timestamp"] if agent_data["activities"] else None
        }

