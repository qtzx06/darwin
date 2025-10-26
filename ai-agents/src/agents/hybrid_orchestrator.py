"""
Hybrid Orchestrator Agent
Manages subtask breakdown, feedback collection, and coordinates Letta+AutoGen teams
"""
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from ..core.shared_memory import SharedMemory
from ..core.message_system import MessageBroker, MessageType


class HybridOrchestrator:
    """
    Orchestrates the hybrid Letta+AutoGen workflow:
    1. Breaks down user task into subtasks
    2. Coordinates 4 dev agents through each subtask
    3. Collects user feedback after each subtask
    4. Updates shared memory with structured feedback
    """
    
    def __init__(
        self,
        letta_agent_id: str,
        letta_client,
        shared_memory: SharedMemory,
        message_broker: MessageBroker,
        dev_agents: List,
        commentator_agent,
        logger=None
    ):
        self.agent_id = letta_agent_id
        self.letta_client = letta_client
        self.shared_memory = shared_memory
        self.message_broker = message_broker
        self.dev_agents = dev_agents
        self.commentator = commentator_agent
        self.logger = logger
        
        # Silence mode - only commentator should print
        self.silent = True
        
        # Workflow state
        self.current_project = None
        self.subtasks = []
        self.current_subtask_index = 0
    
    def _print(self, *args, **kwargs):
        """Print only if not in silent mode."""
        if not self.silent:
            print(*args, **kwargs)
    
    def _force_print(self, *args, **kwargs):
        """Always print regardless of silent mode - for user-facing output."""
        print(*args, **kwargs)
    
    async def start_project(self, user_prompt: str) -> Dict[str, Any]:
        """
        Initialize a new project from user prompt.
        """
        self._print(f"\n{'='*70}")
        self._print(f"🚀 DARWIN: Starting New Project")
        self._print(f"{'='*70}\n")
        self._print(f"📋 User Request: {user_prompt}\n")
        
        self.current_project = {
            "prompt": user_prompt,
            "started_at": datetime.now().isoformat(),
            "subtasks": [],
            "feedback_history": []
        }
        
        if self.logger:
            self.logger.log_session_start(user_prompt)
        
        # 1. Break down task into subtasks using Letta
        self._print("🧠 Orchestrator: Breaking down task into subtasks...")
        self.subtasks = await self._break_down_task(user_prompt)
        
        self._print(f"\n📊 Identified {len(self.subtasks)} subtasks:")
        for i, subtask in enumerate(self.subtasks, 1):
            self._print(f"  {i}. {subtask}")
        self._print()
        
        # Store in shared memory
        await self.shared_memory.write("project", self.current_project)
        await self.shared_memory.write("subtasks", self.subtasks)
        
        return {
            "success": True,
            "project": self.current_project,
            "subtasks": self.subtasks
        }
    
    async def _break_down_task(self, user_prompt: str) -> List[str]:
        """
        Use Letta agent to break down task into subtasks.
        """
        try:
            breakdown_prompt = f"""
You are a project orchestrator. Break down this user request into 3-5 manageable subtasks:

User Request: {user_prompt}

Requirements:
1. Each subtask should be concrete and actionable
2. Subtasks should build on each other sequentially
3. Focus on incremental progress
4. Make subtasks clear enough for specialized teams to implement

Respond with ONLY a JSON array of subtask descriptions, like:
["Subtask 1 description", "Subtask 2 description", ...]
"""
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.letta_client.agents.messages.create(
                    agent_id=self.agent_id,
                    messages=[{"role": "user", "content": breakdown_prompt}]
                )
            )
            
            # Extract subtasks from response
            for msg in response.messages:
                if msg.message_type == "assistant_message":
                    content = msg.content
                    # Try to parse JSON array
                    import re
                    json_match = re.search(r'\[.*\]', content, re.DOTALL)
                    if json_match:
                        subtasks = json.loads(json_match.group())
                        return subtasks
            
            # Fallback
            return self._generate_default_subtasks(user_prompt)
            
        except Exception as e:
            self._print(f"Warning: Could not generate subtasks with Letta: {e}")
            return self._generate_default_subtasks(user_prompt)
    
    def _generate_default_subtasks(self, prompt: str) -> List[str]:
        """Fallback subtask generation."""
        prompt_lower = prompt.lower()
        
        if "website" in prompt_lower or "web" in prompt_lower:
            return [
                "Set up project structure and basic HTML/CSS framework",
                "Implement core functionality and interactivity",
                "Add styling, animations, and visual polish",
                "Optimize performance and add final touches"
            ]
        elif "3d" in prompt_lower or "three" in prompt_lower:
            return [
                "Initialize 3D scene, camera, and renderer",
                "Create and position 3D objects/models",
                "Add lighting, materials, and textures",
                "Implement controls and interactions"
            ]
        else:
            return [
                "Design architecture and set up foundation",
                "Implement core features and functionality",
                "Add refinements and user experience improvements",
                "Polish, test, and finalize implementation"
            ]
        
    async def _monitor_progress(self, subtask_id: int):
        """Monitor teams and provide live commentary while they work."""
        try:
            while True:
                await asyncio.sleep(15)  # Check every 15 seconds
                await self.commentator.monitor_and_comment_on_teams(subtask_id, self.dev_agents)
        except asyncio.CancelledError:
            pass  # Expected when work completes
    
    async def run_subtask(self, subtask_index: int) -> Dict[str, Any]:
        """
        Run a single subtask: all 4 dev agents work in parallel.
        """
        if subtask_index >= len(self.subtasks):
            return {"success": False, "error": "Subtask index out of range"}
        
        subtask = self.subtasks[subtask_index]
        subtask_id = subtask_index + 1
        
        self._print(f"\n{'='*70}")
        self._print(f"🎯 SUBTASK {subtask_id}/{len(self.subtasks)}")
        self._print(f"{'='*70}")
        self._print(f"📝 {subtask}\n")
        
        # All 4 dev agents work in parallel
        self._print("🤖 Activating all 4 dev teams...\n")
        
        # Start monitoring task for live commentary
        monitor_task = asyncio.create_task(self._monitor_progress(subtask_id))
        
        results = await asyncio.gather(*[
            agent.work_on_subtask(subtask_id, subtask)
            for agent in self.dev_agents
        ], return_exceptions=True)
        
        # Cancel monitoring
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass
        
        # Check for errors
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self._print(f"❌ Agent {i+1} encountered error: {result}")
        
        self._print(f"\n✅ All teams completed Subtask {subtask_id}!\n")
        
        # Store results
        await self.shared_memory.write(f"subtask_{subtask_id}_results", {
            "subtask": subtask,
            "results": [r for r in results if not isinstance(r, Exception)],
            "completed_at": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "subtask_id": subtask_id,
            "subtask": subtask,
            "results": results
        }
    
    async def collect_feedback(self, subtask_id: int) -> Dict[str, Any]:
        """
        Commentator presents results, then collect user feedback.
        """
        self._force_print(f"\n{'='*70}")
        self._force_print(f"💬 DELIVERABLES: Subtask {subtask_id}")
        self._force_print(f"{'='*70}\n")
        
        # 1. Generate final commentary from commentator
        await self.commentator.generate_final_commentary(subtask_id, self.dev_agents)
        
        # 2. Collect and save visual artifacts
        self._force_print("\n📦 Generating Visual Artifacts...\n")
        
        artifacts = []
        deliverables_shown = 0
        for agent in self.dev_agents:
            # Get the agent's result from the last subtask
            result = await self.shared_memory.read(f"subtask_{subtask_id}_result_{agent.agent_id}")
            
            if result and result.get("success"):
                summary = result.get("summary", "")
                review_result = result.get("review_result", {})
                
                # Debug: Check what code we got
                final_code = review_result.get("final_code", "")
                if not final_code or final_code == "// Mock code generated":
                    self._force_print(f"⚠️ {agent.name}: No real code generated (mock fallback)")
                
                # Generate visual artifact
                artifact = await agent.generate_artifact_html(subtask_id, summary, review_result)
                artifacts.append(artifact)
                
                # Generate text deliverable
                deliverable = await agent.generate_deliverable(subtask_id, summary, review_result)
                self._force_print(deliverable)
                self._force_print("\n" + "-"*70 + "\n")
                deliverables_shown += 1
        
        # Save artifacts to JSON for viewer
        if artifacts:
            self._save_artifacts_json(subtask_id, artifacts)
            self._force_print(f"\n✅ Visual artifacts saved ({len(artifacts)} teams)! View at: http://localhost:8080/artifact_viewer.html\n")
        else:
            self._force_print(f"\n⚠️ No artifacts generated (list was empty)\n")
        
        if deliverables_shown == 0:
            self._force_print("⚠️ No deliverables available yet.\n")
            return {"success": False, "error": "No deliverables"}
        
        # 3. Collect user feedback
        self._force_print("\n👤 Please provide your feedback:")
        self._force_print("   - What did you like from each team?")
        self._force_print("   - What should be improved?")
        self._force_print("   - Any specific directions for the next subtask?\n")
        
        try:
            user_feedback = input("Your feedback: ").strip()
        except (EOFError, KeyboardInterrupt):
            self._force_print("\n⚠️ No feedback provided, continuing with defaults...")
            user_feedback = "Continue with current approach. Good work on all implementations."
        
        # 4. Process and structure feedback with Letta
        self._print("\n🧠 Orchestrator: Processing your feedback...\n")
        structured_feedback = await self._process_feedback(subtask_id, user_feedback)
        
        # 5. Store in shared memory for all agents to access
        await self.shared_memory.write(
            f"subtask_{subtask_id}_feedback",
            structured_feedback
        )
        
        # 6. Update global learnings
        await self._update_global_learnings(structured_feedback)
        
        self._print("✅ Feedback saved to shared memory!\n")
        
        return {
            "success": True,
            "subtask_id": subtask_id,
            "feedback": structured_feedback
        }
    
    async def _process_feedback(self, subtask_id: int, raw_feedback: str) -> Dict[str, Any]:
        """
        Use Letta to structure and analyze user feedback.
        """
        try:
            analysis_prompt = f"""
Analyze this user feedback for Subtask {subtask_id}:

"{raw_feedback}"

Extract:
1. Specific things the user liked (patterns, approaches, features)
2. Things the user disliked or wants changed
3. General principles to apply going forward

Respond in JSON format:
{{
  "likes": ["item 1", "item 2"],
  "dislikes": ["item 1"],
  "principles": ["principle 1", "principle 2"]
}}
"""
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.letta_client.agents.messages.create(
                    agent_id=self.agent_id,
                    messages=[{"role": "user", "content": analysis_prompt}]
                )
            )
            
            # Extract structured feedback
            for msg in response.messages:
                if msg.message_type == "assistant_message":
                    import re
                    json_match = re.search(r'\{.*\}', msg.content, re.DOTALL)
                    if json_match:
                        analysis = json.loads(json_match.group())
                        return {
                            "raw_feedback": raw_feedback,
                            "likes": analysis.get("likes", []),
                            "dislikes": analysis.get("dislikes", []),
                            "principles": analysis.get("principles", []),
                            "timestamp": datetime.now().isoformat()
                        }
            
            # Fallback
            return self._create_basic_feedback_structure(raw_feedback)
            
        except Exception as e:
            self._print(f"Warning: Could not analyze feedback with Letta: {e}")
            return self._create_basic_feedback_structure(raw_feedback)
    
    def _create_basic_feedback_structure(self, raw_feedback: str) -> Dict[str, Any]:
        """Fallback feedback structure."""
        return {
            "raw_feedback": raw_feedback,
            "likes": [],
            "dislikes": [],
            "principles": ["Apply user's feedback"],
            "timestamp": datetime.now().isoformat()
        }
    
    async def _update_global_learnings(self, feedback: Dict[str, Any]):
        """Update global learnings based on feedback."""
        global_learnings = await self.shared_memory.read("global_learnings") or {
            "preferred_patterns": [],
            "avoid_patterns": []
        }
        
        # Add new learnings
        for like in feedback.get("likes", []):
            if like not in global_learnings["preferred_patterns"]:
                global_learnings["preferred_patterns"].append(like)
        
        for dislike in feedback.get("dislikes", []):
            if dislike not in global_learnings["avoid_patterns"]:
                global_learnings["avoid_patterns"].append(dislike)
        
        await self.shared_memory.write("global_learnings", global_learnings)
    
    def _save_artifacts_json(self, subtask_id: int, artifacts: list):
        """Save artifacts to JSON file for the viewer"""
        try:
            import json
            from pathlib import Path
            
            artifacts_dir = Path(f"artifacts/subtask_{subtask_id}")
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            
            artifacts_file = artifacts_dir / "artifacts.json"
            with open(artifacts_file, 'w', encoding='utf-8') as f:
                json.dump(artifacts, f, indent=2, ensure_ascii=False)
            
            # Also save individual HTML files for direct viewing
            for artifact in artifacts:
                html_file = artifacts_dir / f"{artifact['team_id']}.html"
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(artifact['html'])
                    
        except Exception as e:
            self._print(f"Warning: Could not save artifacts: {e}")
    
    async def run_full_project(self):
        """
        Run the complete project workflow: all subtasks with feedback loops.
        """
        for i in range(len(self.subtasks)):
            # Run subtask
            await self.run_subtask(i)
            
            # Collect feedback
            await self.collect_feedback(i + 1)
            
            # Check if user wants to continue
            if i < len(self.subtasks) - 1:
                continue_prompt = input("\n▶️  Continue to next subtask? (y/n): ").strip().lower()
                if continue_prompt != 'y':
                    self._print("⏸️ Project paused.")
                    break
        
        self._print(f"\n{'='*70}")
        self._print("🎉 PROJECT COMPLETE!")
        self._print(f"{'='*70}\n")
