"""
Artifact management system for tracking and rendering agent work.
Manages code, outputs, and previews for each agent.
"""
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path


class ArtifactType(Enum):
    """Types of artifacts agents can create."""
    CODE = "code"
    DOCUMENTATION = "documentation"
    DESIGN = "design"
    CONFIG = "config"
    TEST = "test"
    OUTPUT = "output"


@dataclass
class Artifact:
    """Represents an artifact created by an agent."""
    id: str
    agent_id: str
    artifact_type: ArtifactType
    content: Dict[str, Any]
    created_at: datetime
    last_updated: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert artifact to dictionary."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "artifact_type": self.artifact_type.value,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "metadata": self.metadata or {}
        }


class ArtifactManager:
    """
    Manages artifacts created by agents with Claude Artifacts-style structure.
    Tracks code, outputs, and generates previews for frontend rendering.
    """
    
    def __init__(self):
        self._artifacts: Dict[str, Artifact] = {}
        self._agent_artifacts: Dict[str, List[str]] = {}  # agent_id -> artifact_ids
        self._lock = asyncio.Lock()
        self._artifact_counter = 0
        self._projects: Dict[str, Dict[str, Any]] = {}  # project_id -> project info
    
    def _generate_artifact_id(self, agent_id: str, artifact_type: ArtifactType) -> str:
        """Generate unique artifact ID."""
        self._artifact_counter += 1
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{agent_id}_{artifact_type.value}_{self._artifact_counter}_{timestamp}"
    
    async def _save_artifact_to_file(self, artifact: Artifact):
        """Save artifact content to a file."""
        try:
            # Create artifacts directory if it doesn't exist
            artifacts_dir = Path("artifacts")
            artifacts_dir.mkdir(exist_ok=True)
            
            # Determine file extension based on artifact type
            file_extension = artifact.artifact_type.value
            
            # Create file path
            file_path = artifacts_dir / f"{artifact.id}.{file_extension}"
            
            # Save content as JSON
            with open(file_path, 'w') as f:
                json.dump(artifact.content, f, indent=2, default=str)
                
        except Exception as e:
            print(f"Error saving artifact {artifact.id}: {e}")
    
    async def create_artifact(
        self, 
        agent_id: str, 
        artifact_type: ArtifactType,
        initial_content: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new artifact for an agent."""
        artifact_id = self._generate_artifact_id(agent_id, artifact_type)
        
        artifact = Artifact(
            id=artifact_id,
            agent_id=agent_id,
            artifact_type=artifact_type,
            content=initial_content or {},
            created_at=datetime.now(),
            last_updated=datetime.now(),
            metadata={}
        )
        
        async with self._lock:
            self._artifacts[artifact_id] = artifact
            
            if agent_id not in self._agent_artifacts:
                self._agent_artifacts[agent_id] = []
            self._agent_artifacts[agent_id].append(artifact_id)
            
            # Save artifact to file
            await self._save_artifact_to_file(artifact)
        
        return artifact_id
    
    async def update_artifact(
        self, 
        agent_id: str, 
        content: Dict[str, Any],
        artifact_id: Optional[str] = None
    ) -> str:
        """Update an artifact with new content."""
        async with self._lock:
            # If no artifact_id provided, find the most recent artifact for this agent
            if artifact_id is None:
                if agent_id not in self._agent_artifacts or not self._agent_artifacts[agent_id]:
                    # Create a new artifact
                    artifact_type = ArtifactType.CODE  # Default type
                    artifact_id = self._generate_artifact_id(agent_id, artifact_type)
                    artifact = Artifact(
                        id=artifact_id,
                        agent_id=agent_id,
                        artifact_type=artifact_type,
                        content=content,
                        created_at=datetime.now(),
                        last_updated=datetime.now(),
                        metadata={}
                    )
                    self._artifacts[artifact_id] = artifact
                    
                    if agent_id not in self._agent_artifacts:
                        self._agent_artifacts[agent_id] = []
                    self._agent_artifacts[agent_id].append(artifact_id)
                else:
                    # Use the most recent artifact
                    artifact_id = self._agent_artifacts[agent_id][-1]
            
            # Update the artifact
            if artifact_id in self._artifacts:
                artifact = self._artifacts[artifact_id]
                artifact.content.update(content)
                artifact.last_updated = datetime.now()
            else:
                # Create new artifact if not found
                artifact_type = ArtifactType.CODE  # Default type
                artifact = Artifact(
                    id=artifact_id,
                    agent_id=agent_id,
                    artifact_type=artifact_type,
                    content=content,
                    created_at=datetime.now(),
                    last_updated=datetime.now(),
                    metadata={}
                )
                self._artifacts[artifact_id] = artifact
                
                if agent_id not in self._agent_artifacts:
                    self._agent_artifacts[agent_id] = []
                if artifact_id not in self._agent_artifacts[agent_id]:
                    self._agent_artifacts[agent_id].append(artifact_id)
            
            # Save updated artifact to file
            if artifact_id in self._artifacts:
                await self._save_artifact_to_file(self._artifacts[artifact_id])
        
        return artifact_id
    
    async def get_artifact(self, artifact_id: str) -> Optional[Artifact]:
        """Get an artifact by ID."""
        async with self._lock:
            return self._artifacts.get(artifact_id)
    
    async def get_agent_artifacts(self, agent_id: str) -> List[Artifact]:
        """Get all artifacts for a specific agent."""
        async with self._lock:
            if agent_id not in self._agent_artifacts:
                return []
            
            artifacts = []
            for artifact_id in self._agent_artifacts[agent_id]:
                if artifact_id in self._artifacts:
                    artifacts.append(self._artifacts[artifact_id])
            
            return artifacts
    
    async def get_latest_artifact(self, agent_id: str) -> Optional[Artifact]:
        """Get the most recent artifact for an agent."""
        artifacts = await self.get_agent_artifacts(agent_id)
        if not artifacts:
            return None
        
        return max(artifacts, key=lambda a: a.last_updated)
    
    async def render_preview(self, artifact_id: str) -> Dict[str, Any]:
        """Generate a preview of an artifact."""
        artifact = await self.get_artifact(artifact_id)
        if not artifact:
            return {"error": "Artifact not found"}
        
        preview = {
            "artifact_id": artifact_id,
            "agent_id": artifact.agent_id,
            "type": artifact.artifact_type.value,
            "preview": {}
        }
        
        # Generate preview based on artifact type
        if artifact.artifact_type == ArtifactType.CODE:
            preview["preview"] = {
                "language": artifact.content.get("language", "unknown"),
                "code_snippet": artifact.content.get("code", "")[:500] + "..." if len(artifact.content.get("code", "")) > 500 else artifact.content.get("code", ""),
                "line_count": len(artifact.content.get("code", "").split('\n')) if artifact.content.get("code") else 0
            }
        elif artifact.artifact_type == ArtifactType.DOCUMENTATION:
            preview["preview"] = {
                "title": artifact.content.get("title", "Untitled"),
                "content_preview": artifact.content.get("content", "")[:200] + "..." if len(artifact.content.get("content", "")) > 200 else artifact.content.get("content", ""),
                "word_count": len(artifact.content.get("content", "").split()) if artifact.content.get("content") else 0
            }
        elif artifact.artifact_type == ArtifactType.DESIGN:
            preview["preview"] = {
                "design_type": artifact.content.get("type", "unknown"),
                "description": artifact.content.get("description", ""),
                "elements": artifact.content.get("elements", [])
            }
        else:
            preview["preview"] = {
                "content": artifact.content,
                "size": len(str(artifact.content))
            }
        
        return preview
    
    async def get_artifact_summary(self, agent_id: str) -> Dict[str, Any]:
        """Get a summary of all artifacts for an agent."""
        artifacts = await self.get_agent_artifacts(agent_id)
        
        summary = {
            "agent_id": agent_id,
            "total_artifacts": len(artifacts),
            "artifact_types": {},
            "latest_activity": None,
            "artifacts": []
        }
        
        if artifacts:
            # Count by type
            for artifact in artifacts:
                artifact_type = artifact.artifact_type.value
                summary["artifact_types"][artifact_type] = summary["artifact_types"].get(artifact_type, 0) + 1
            
            # Find latest activity
            latest_artifact = max(artifacts, key=lambda a: a.last_updated)
            summary["latest_activity"] = {
                "artifact_id": latest_artifact.id,
                "type": latest_artifact.artifact_type.value,
                "last_updated": latest_artifact.last_updated.isoformat()
            }
            
            # Add artifact summaries
            for artifact in artifacts:
                summary["artifacts"].append({
                    "id": artifact.id,
                    "type": artifact.artifact_type.value,
                    "created_at": artifact.created_at.isoformat(),
                    "last_updated": artifact.last_updated.isoformat()
                })
        
        return summary
    
    async def delete_artifact(self, artifact_id: str) -> bool:
        """Delete an artifact."""
        async with self._lock:
            if artifact_id not in self._artifacts:
                return False
            
            artifact = self._artifacts[artifact_id]
            agent_id = artifact.agent_id
            
            # Remove from agent's artifact list
            if agent_id in self._agent_artifacts:
                if artifact_id in self._agent_artifacts[agent_id]:
                    self._agent_artifacts[agent_id].remove(artifact_id)
            
            # Remove from artifacts
            del self._artifacts[artifact_id]
            
            return True
    
    async def get_all_artifacts(self) -> List[Artifact]:
        """Get all artifacts across all agents."""
        async with self._lock:
            return list(self._artifacts.values())
    
    async def search_artifacts(self, query: str, agent_id: Optional[str] = None) -> List[Artifact]:
        """Search artifacts by content."""
        artifacts = await self.get_all_artifacts()
        
        if agent_id:
            artifacts = [a for a in artifacts if a.agent_id == agent_id]
        
        # Simple text search in content
        matching_artifacts = []
        query_lower = query.lower()
        
        for artifact in artifacts:
            content_str = str(artifact.content).lower()
            if query_lower in content_str:
                matching_artifacts.append(artifact)
        
        return matching_artifacts
    
    async def create_project_workspace(self, project_id: str, project_name: str) -> str:
        """Create Claude-style project workspace structure."""
        project_path = Path("artifacts") / project_id
        
        # Create main project directory
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Create agent directories
        agents = ["One", "Two", "Three", "Four"]
        for agent in agents:
            agent_path = project_path / agent
            agent_path.mkdir(exist_ok=True)
            
            # Create final directory for each agent
            (agent_path / "final").mkdir(exist_ok=True)
        
        # Create canonical directory
        canonical_path = project_path / "canonical"
        canonical_path.mkdir(exist_ok=True)
        
        # Create project metadata
        project_metadata = {
            "project_id": project_id,
            "project_name": project_name,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "current_round": 0,
            "subtasks": [],
            "winners": []
        }
        
        with open(project_path / "metadata.json", 'w') as f:
            json.dump(project_metadata, f, indent=2)
        
        # Store project info
        self._projects[project_id] = {
            "path": str(project_path),
            "name": project_name,
            "created_at": datetime.now().isoformat()
        }
        
        print(f"📁 Created project workspace: {project_path}")
        return str(project_path)
    
    async def save_agent_round(self, project_id: str, agent_name: str, round_num: int, 
                              code: str, metadata: Dict[str, Any]) -> str:
        """Save agent's code for a specific round."""
        project_path = Path("artifacts") / project_id
        round_path = project_path / agent_name.lower().replace(" ", "_") / f"round_{round_num}"
        round_path.mkdir(parents=True, exist_ok=True)
        
        # Save code file
        code_file = round_path / "code.tsx"
        with open(code_file, 'w') as f:
            f.write(code)
        
        # Save metadata
        round_metadata = {
            "agent_name": agent_name,
            "agent_id": metadata.get("agent_id", ""),
            "personality": metadata.get("personality", ""),
            "subtask": metadata.get("subtask", ""),
            "round": round_num,
            "timestamp": datetime.now().isoformat(),
            "language": metadata.get("language", "typescript"),
            "is_winner": False,
            "code_summary": metadata.get("code_summary", ""),
            "file_type": metadata.get("file_type", "component"),
            "preview_available": True,
            "lines_of_code": len(code.split('\n'))
        }
        
        with open(round_path / "metadata.json", 'w') as f:
            json.dump(round_metadata, f, indent=2)
        
        # Save summary
        summary_file = round_path / "summary.md"
        with open(summary_file, 'w') as f:
            f.write(f"# {agent_name}'s Round {round_num} Submission\n\n")
            f.write(f"**Subtask:** {metadata.get('subtask', 'Unknown')}\n\n")
            f.write(f"**Approach:** {metadata.get('code_summary', 'No description provided')}\n\n")
            f.write(f"**Personality Notes:** {metadata.get('personality', '')}\n")
        
        print(f"💾 Saved {agent_name}'s round {round_num} to {round_path}")
        return str(round_path)
    
    async def save_canonical_code(self, project_id: str, winner_code: str, 
                                 winner_metadata: Dict[str, Any]) -> str:
        """Save winning code as canonical for next round."""
        project_path = Path("artifacts") / project_id
        canonical_path = project_path / "canonical"
        
        # Save canonical code
        code_file = canonical_path / "code.tsx"
        with open(code_file, 'w') as f:
            f.write(winner_code)
        
        # Save canonical metadata
        canonical_metadata = {
            "subtask": winner_metadata.get("subtask", ""),
            "winner": winner_metadata.get("agent_name", ""),
            "winner_agent_id": winner_metadata.get("agent_id", ""),
            "why_it_won": winner_metadata.get("why_it_won", ""),
            "timestamp": datetime.now().isoformat(),
            "round": winner_metadata.get("round", 0)
        }
        
        with open(canonical_path / "metadata.json", 'w') as f:
            json.dump(canonical_metadata, f, indent=2)
        
        # Update project metadata
        await self._update_project_metadata(project_id, winner_metadata)
        
        print(f"🏆 Saved canonical code from {winner_metadata.get('agent_name', 'Unknown')}")
        return str(canonical_path)
    
    async def update_agent_final(self, project_id: str, agent_name: str, 
                                complete_code: str, metadata: Dict[str, Any]) -> str:
        """Update agent's final artifact with complete code."""
        project_path = Path("artifacts") / project_id
        final_path = project_path / agent_name.lower().replace(" ", "_") / "final"
        final_path.mkdir(parents=True, exist_ok=True)
        
        # Save final code
        code_file = final_path / "code.tsx"
        with open(code_file, 'w') as f:
            f.write(complete_code)
        
        # Save final metadata
        final_metadata = {
            "agent_name": agent_name,
            "agent_id": metadata.get("agent_id", ""),
            "personality": metadata.get("personality", ""),
            "project_id": project_id,
            "completed_at": datetime.now().isoformat(),
            "total_rounds": metadata.get("total_rounds", 0),
            "wins": metadata.get("wins", 0),
            "code_summary": f"Complete {metadata.get('project_name', 'project')} implementation",
            "file_type": "complete_project",
            "lines_of_code": len(complete_code.split('\n'))
        }
        
        with open(final_path / "metadata.json", 'w') as f:
            json.dump(final_metadata, f, indent=2)
        
        # Save README
        readme_file = final_path / "README.md"
        with open(readme_file, 'w') as f:
            f.write(f"# {agent_name}'s Final Project\n\n")
            f.write(f"**Project:** {metadata.get('project_name', 'Unknown')}\n\n")
            f.write(f"**Personality:** {metadata.get('personality', '')}\n\n")
            f.write(f"**Wins:** {metadata.get('wins', 0)} rounds\n\n")
            f.write(f"**Total Rounds:** {metadata.get('total_rounds', 0)}\n\n")
            f.write("## Code\n\nThis is the complete implementation with my unique style and approach.\n")
        
        # Save summary
        summary_file = final_path / "summary.md"
        with open(summary_file, 'w') as f:
            f.write(f"# {agent_name}'s Project Summary\n\n")
            f.write(f"**Approach:** {metadata.get('personality', '')}\n\n")
            f.write(f"**Key Features:** Complete fullstack implementation\n\n")
            f.write(f"**Wins:** {metadata.get('wins', 0)} out of {metadata.get('total_rounds', 0)} rounds\n")
        
        print(f"🎯 Updated {agent_name}'s final artifact")
        return str(final_path)
    
    async def get_all_round_artifacts(self, project_id: str, round_num: int) -> List[Dict[str, Any]]:
        """Get all artifacts for a specific round (for frontend display)."""
        project_path = Path("artifacts") / project_id
        artifacts = []
        
        agents = ["a", "b", "c", "d"]
        for agent in agents:
            round_path = project_path / agent / f"round_{round_num}"
            if round_path.exists():
                # Load metadata
                metadata_file = round_path / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    # Load code
                    code_file = round_path / "code.tsx"
                    if code_file.exists():
                        with open(code_file, 'r') as f:
                            code = f.read()
                        metadata["code"] = code
                    
                    artifacts.append(metadata)
        
        return artifacts
    
    async def get_final_artifacts(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all final artifacts for project completion."""
        project_path = Path("artifacts") / project_id
        artifacts = []
        
        agents = ["a", "b", "c", "d"]
        for agent in agents:
            final_path = project_path / agent / "final"
            if final_path.exists():
                # Load metadata
                metadata_file = final_path / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    # Load code
                    code_file = final_path / "code.tsx"
                    if code_file.exists():
                        with open(code_file, 'r') as f:
                            code = f.read()
                        metadata["code"] = code
                    
                    artifacts.append(metadata)
        
        return artifacts
    
    async def _update_project_metadata(self, project_id: str, winner_metadata: Dict[str, Any]):
        """Update project metadata with winner information."""
        project_path = Path("artifacts") / project_id
        metadata_file = project_path / "metadata.json"
        
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                project_metadata = json.load(f)
            
            # Add winner to history
            winner_info = {
                "subtask": winner_metadata.get("subtask", ""),
                "round": winner_metadata.get("round", 0),
                "winner": winner_metadata.get("agent_name", ""),
                "why_it_won": winner_metadata.get("why_it_won", ""),
                "timestamp": datetime.now().isoformat()
            }
            
            project_metadata["winners"].append(winner_info)
            project_metadata["current_round"] = winner_metadata.get("round", 0)
            
            with open(metadata_file, 'w') as f:
                json.dump(project_metadata, f, indent=2)
