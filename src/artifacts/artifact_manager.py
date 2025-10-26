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
    Manages artifacts created by agents.
    Tracks code, outputs, and generates previews.
    """
    
    def __init__(self):
        self._artifacts: Dict[str, Artifact] = {}
        self._agent_artifacts: Dict[str, List[str]] = {}  # agent_id -> artifact_ids
        self._lock = asyncio.Lock()
        self._artifact_counter = 0
    
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
