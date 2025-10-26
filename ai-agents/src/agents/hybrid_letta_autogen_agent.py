"""
Hybrid Letta + AutoGen Dev Agent
Letta agent manages state/memory, AutoGen team handles problem-solving
"""
import os
import json
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from ..core.shared_memory import SharedMemory
from ..core.message_system import MessageBroker, MessageType
from ..artifacts.artifact_manager import ArtifactManager
from ..autogen_integration.autogen_team import AutoGenTeamWrapper
from ..core.live_feed import get_live_feed, LiveFeedEvent


class HybridLettaDevAgent:
    """
    Hybrid agent combining Letta (memory/state) with AutoGen (problem-solving).
    Each agent wraps an AutoGen team and maintains a single growing codebase file.
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        specialization: str,
        team_number: int,  # NEW: Which team (1-4) for Gemini API key
        letta_client,
        shared_memory: SharedMemory,
        message_broker: MessageBroker,
        artifact_manager: ArtifactManager,
        logger=None
    ):
        self.agent_id = agent_id
        self.name = name
        self.specialization = specialization
        self.team_number = team_number
        self.letta_client = letta_client
        self.shared_memory = shared_memory
        self.message_broker = message_broker
        self.artifact_manager = artifact_manager
        self.logger = logger
        
        # Silence mode - only commentator should print
        self.silent = True  # Set to False for debugging
        
        # Live feed for real-time updates
        self.live_feed = get_live_feed()
        
        # Get personality from Letta agent
        personality = self._get_personality_from_letta()
        
        # Initialize AutoGen team with team-specific API key
        self.autogen_team = AutoGenTeamWrapper(
            team_id=agent_id,
            team_name=name,
            specialization=specialization,
            team_number=team_number,  # Pass team number for API key selection
            silent=True,  # Silence AutoGen output
            personality=personality  # Pass PM personality to AutoGen team
        )
        
        # Single growing codebase file
        self.codebase_file = Path(f"artifacts/codebases/{agent_id}_codebase.txt")
        self.codebase_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize empty codebase
        if not self.codebase_file.exists():
            self._write_codebase("")
        
        # Agent state
        self.is_working = False
        self.current_subtask = None
        self.subtasks_completed = 0
    
    def _get_personality_from_letta(self) -> str:
        """Extract personality from Letta agent's system prompt."""
        try:
            # Get agent details from Letta
            import requests
            response = requests.get(
                f"https://api.letta.com/v1/agents/{self.agent_id}",
                headers={"Authorization": f"Bearer {os.getenv('LETTA_API_TOKEN')}"}
            )
            if response.status_code == 200:
                agent_data = response.json()
                system_prompt = agent_data.get("system", "")
                # Extract personality section
                if "PERSONALITY:" in system_prompt:
                    personality_section = system_prompt.split("PERSONALITY:")[1].split("Your role:")[0]
                    return personality_section.strip()
        except Exception as e:
            pass  # Silently fail, use default
        return ""
    
    def _print(self, *args, **kwargs):
        """Print only if not in silent mode."""
        if not self.silent:
            self._print(*args, **kwargs)
    
    def _read_codebase(self) -> str:
        """Read the current codebase from file."""
        try:
            return self.codebase_file.read_text(encoding='utf-8')
        except Exception as e:
            self._print(f"Error reading codebase for {self.name}: {e}")
            return ""
    
    def _write_codebase(self, code: str):
        """Write/update the codebase file."""
        try:
            self.codebase_file.write_text(code, encoding='utf-8')
            if self.logger:
                self.logger.log_artifact_update(
                    self.agent_id,
                    str(self.codebase_file),
                    "codebase_updated",
                    f"Codebase size: {len(code)} chars"
                )
        except Exception as e:
            self._print(f"Error writing codebase for {self.name}: {e}")
    
    async def work_on_subtask(
        self,
        subtask_id: int,
        subtask_description: str
    ) -> Dict[str, Any]:
        """
        Main workflow: Letta agent orchestrates AutoGen team to solve subtask.
        """
        try:
            self._print(f"\n{'='*60}")
            self._print(f"🤖 {self.name} starting Subtask {subtask_id}")
            self._print(f"{'='*60}\n")
            
            self.is_working = True
            self.current_subtask = subtask_description
            
            # LIVE UPDATE: Work started
            await self.live_feed.publish_event(LiveFeedEvent(
                event_type="work_started",
                agent_id=self.agent_id,
                agent_name=self.name,
                content={"subtask_id": subtask_id, "description": subtask_description}
            ))
            
            if self.logger:
                self.logger.log_agent_activity(
                    self.agent_id,
                    "subtask_started",
                    {"subtask_id": subtask_id, "description": subtask_description}
                )
            
            # 1. Get context from Letta shared memory
            context = await self._get_context_from_shared_memory(subtask_id)
            
            # 2. Read existing codebase
            existing_code = self._read_codebase()
            
            # 3. Run AutoGen team (with live updates)
            self._print(f"🔧 {self.name}: Activating AutoGen team...")
            await self.live_feed.publish_event(LiveFeedEvent(
                event_type="autogen_started",
                agent_id=self.agent_id,
                agent_name=self.name,
                content={"status": "AutoGen team discussion starting..."}
            ))
            
            autogen_result = await self.autogen_team.solve_subtask(
                subtask_description=subtask_description,
                existing_codebase=existing_code,
                user_feedback=context.get("user_feedback", ""),
                context=context,
                live_feed=self.live_feed,  # Pass live feed to AutoGen
                agent_name=self.name,
                agent_id=self.agent_id,
                subtask_id=subtask_id  # Pass subtask ID for file naming
            )
            
            # LIVE UPDATE: AutoGen completed
            await self.live_feed.publish_event(LiveFeedEvent(
                event_type="autogen_complete",
                agent_id=self.agent_id,
                agent_name=self.name,
                content={
                    "messages_exchanged": autogen_result.get('message_count', 0),
                    "code_generated": bool(autogen_result.get('code'))
                }
            ))
            
            # 4. LETTA REVIEWS & REVISES AutoGen's work
            self._print(f"🧠 {self.name}: Letta agent reviewing AutoGen's code...")
            await self.live_feed.publish_event(LiveFeedEvent(
                event_type="pm_reviewing",
                agent_id=self.agent_id,
                agent_name=self.name,
                content={"status": "Letta PM reviewing team's work..."}
            ))
            
            review_result = await self._review_and_revise_code(
                subtask_description=subtask_description,
                autogen_conversation=autogen_result.get("conversation", []),
                autogen_code=autogen_result.get("code", ""),
                existing_codebase=existing_code
            )
            
            # LIVE UPDATE: Review complete
            await self.live_feed.publish_event(LiveFeedEvent(
                event_type="review_complete",
                agent_id=self.agent_id,
                agent_name=self.name,
                content={
                    "quality_score": review_result.get('code_quality_score', 0),
                    "team_feedback": review_result.get('team_feedback', '')
                }
            ))
            
            # 5. Update codebase with REVIEWED/REVISED code
            final_code = review_result.get("final_code", autogen_result.get("code", ""))
            if final_code:
                new_codebase = self._merge_code(existing_code, final_code)
                self._write_codebase(new_codebase)
                self._print(f"✅ {self.name}: Codebase updated ({len(new_codebase)} chars)")
            
            # 6. Generate summary using Letta agent (includes feedback to AutoGen team)
            summary = await self._generate_summary_with_letta(
                subtask_description,
                autogen_result,
                review_result
            )
            
            # 7. Save conversation, review notes, and summary to files
            await self._save_artifacts(subtask_id, autogen_result, summary, review_result)
            
            # 8. Update persistent memory block with learnings
            await self._update_persistent_memory(review_result)
            
            # 9. Store result in shared memory for orchestrator to access
            result_data = {
                "success": True,
                "agent_id": self.agent_id,
                "subtask_id": subtask_id,
                "autogen_result": autogen_result,
                "summary": summary,
                "review_result": review_result,
                "codebase_path": str(self.codebase_file),
                "completed_at": datetime.now().isoformat()
            }
            
            await self.shared_memory.write(
                f"subtask_{subtask_id}_result_{self.agent_id}",
                result_data
            )
            
            # 10. Update agent status in shared memory
            await self.shared_memory.update_agent_status(self.agent_id, {
                "status": "completed_subtask",
                "subtask_id": subtask_id,
                "completed_at": datetime.now().isoformat()
            })
            
            self.is_working = False
            self.subtasks_completed += 1
            
            self._print(f"✅ {self.name}: Subtask {subtask_id} complete!\n")
            
            return result_data
            
        except Exception as e:
            self.is_working = False
            self._print(f"❌ {self.name}: Error on subtask {subtask_id}: {e}")
            
            if self.logger:
                self.logger.log_error(f"{self.name} subtask error: {e}")
            
            return {
                "success": False,
                "agent_id": self.agent_id,
                "error": str(e)
            }
    
    async def generate_artifact_html(self, subtask_id: int, summary: str, review_result: Dict) -> Dict[str, Any]:
        """
        Generate a visual HTML artifact that can be rendered in browser.
        Teams MUST produce something visual, not just descriptions.
        """
        try:
            # Get the generated code
            final_code = review_result.get("final_code", "")
            quality_score = review_result.get("code_quality_score", "N/A")
            message_count = review_result.get("message_count", 0)
            
            # Determine artifact type based on code content
            if "<html" in final_code.lower() or "<body" in final_code.lower():
                # Already HTML
                artifact_html = final_code
                artifact_type = "HTML"
            elif "<!DOCTYPE" in final_code or "<div" in final_code:
                # HTML fragment - wrap it
                artifact_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.name} - Subtask {subtask_id}</title>
    <style>
        body {{ 
            margin: 0; 
            padding: 20px; 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
    </style>
</head>
<body>
    {final_code}
</body>
</html>
"""
                artifact_type = "HTML Component"
            else:
                # Pure code - create a visual representation
                artifact_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.name} - Subtask {subtask_id}</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: 'Monaco', 'Courier New', monospace;
            background: #1e1e1e;
            color: #d4d4d4;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: #252526;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #4ec9b0;
            border-bottom: 2px solid #4ec9b0;
            padding-bottom: 10px;
        }}
        pre {{
            background: #1e1e1e;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            border-left: 3px solid #569cd6;
        }}
        code {{
            color: #ce9178;
        }}
        .meta {{
            color: #858585;
            font-size: 0.9em;
            margin-top: 20px;
        }}
        .summary {{
            background: #2d2d30;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            border-left: 3px solid #f48771;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{self.name}</h1>
        <div class="summary">
            <strong>Summary:</strong><br>
            {summary}
        </div>
        <h2 style="color: #569cd6;">Code Implementation</h2>
        <pre><code>{self._escape_html(final_code[:2000])}</code></pre>
        <div class="meta">
            Quality Score: {quality_score}/10 | Messages: {message_count}
        </div>
    </div>
    <script>
        // Add syntax highlighting or interactive elements if needed
        console.log('Artifact loaded: {self.name}');
    </script>
</body>
</html>
"""
                artifact_type = "Code Visualization"
            
            return {
                "team_name": self.name,
                "team_id": self.agent_id,
                "quality_score": quality_score,
                "type": artifact_type,
                "html": artifact_html,
                "summary": summary,
                "messages": message_count
            }
            
        except Exception as e:
            # Fallback artifact
            return {
                "team_name": self.name,
                "team_id": self.agent_id,
                "quality_score": "N/A",
                "type": "Error",
                "html": f"<html><body><h1>Error generating artifact</h1><p>{str(e)}</p></body></html>",
                "summary": summary,
                "messages": 0
            }
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        return (text
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&#039;"))
    
    async def generate_deliverable(self, subtask_id: int, summary: str, review_result: Dict) -> str:
        """
        Generate a user-facing deliverable description.
        This is what the PM presents to the user about what was built.
        """
        try:
            # Get the code that was generated
            code_snippet = review_result.get("final_code", "")[:500]  # First 500 chars
            quality_score = review_result.get("code_quality_score", "N/A")
            
            deliverable = f"""
## {self.name} Deliverable

**Quality Score:** {quality_score}/10

**What we built:**
{summary}

**Code Preview:**
```
{code_snippet}
```

**Full codebase:** {self.codebase_file}
**🌐 View live artifact:** http://localhost:8080/artifact_viewer.html
"""
            return deliverable.strip()
        except Exception as e:
            return f"## {self.name} Deliverable\n\n{summary}"
    
    async def _get_context_from_shared_memory(self, subtask_id: int) -> Dict[str, Any]:
        """Read relevant context from Letta shared memory block."""
        # Get feedback from shared memory
        feedback_key = f"subtask_{subtask_id - 1}_feedback" if subtask_id > 1 else None
        user_feedback = ""
        
        if feedback_key:
            feedback_data = await self.shared_memory.read(feedback_key)
            if feedback_data:
                user_feedback = feedback_data.get("raw_feedback", "")
        
        # Get global learnings
        global_learnings = await self.shared_memory.read("global_learnings") or {}
        
        return {
            "user_feedback": user_feedback,
            "global_learnings": global_learnings,
            "subtask_id": subtask_id
        }
    
    def _merge_code(self, existing: str, new_code: str) -> str:
        """
        Merge new code with existing codebase.
        Strategy: Append new code with clear separator.
        """
        if not existing:
            return new_code
        
        separator = f"\n\n{'='*60}\n// Updated: {datetime.now().isoformat()}\n{'='*60}\n\n"
        return existing + separator + new_code
    
    async def _generate_summary_with_letta(
        self,
        subtask: str,
        autogen_result: Dict[str, Any],
        review_result: Dict[str, Any] = None
    ) -> str:
        """
        Use Letta agent to generate a summary of the AutoGen team's work.
        """
        try:
            # Build prompt for Letta to summarize
            conversation_summary = self._summarize_conversation(
                autogen_result.get("conversation", [])
            )
            
            review_info = ""
            if review_result:
                review_info = f"""
Your Review:
- Quality Score: {review_result.get('code_quality_score', 'N/A')}/10
- Feedback to team: {review_result.get('team_feedback', 'N/A')}
"""
            
            prompt = f"""
Subtask: {subtask}

Your AutoGen team just completed this subtask. Here's what happened:

Team Discussion Summary:
{conversation_summary}

{review_info}

Messages exchanged: {autogen_result.get('message_count', 0)}

Please provide a concise summary (3-4 sentences) of:
1. What approach your team took
2. Key decisions made
3. Why this approach fits your specialization ({self.specialization})
"""
            
            # Call Letta agent for summary
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.letta_client.agents.messages.create(
                    agent_id=self.agent_id,
                    messages=[{"role": "user", "content": prompt}]
                )
            )
            
            # Extract summary from response
            summary = ""
            for msg in response.messages:
                if msg.message_type == "assistant_message":
                    summary = msg.content
                    break
            
            return summary if summary else conversation_summary
            
        except Exception as e:
            self._print(f"Warning: Could not generate Letta summary for {self.name}: {e}")
            # Fallback to basic summary
            return self._summarize_conversation(autogen_result.get("conversation", []))
    
    def _summarize_conversation(self, conversation: list) -> str:
        """Fallback: Basic conversation summary."""
        if not conversation:
            return "No conversation recorded"
        
        summary_parts = [
            f"Team Discussion ({len(conversation)} messages):",
            f"- Planner: Set strategy and approach",
            f"- Coder: Implemented solution",
            f"- Critic: Reviewed and refined",
            f"Final approach: {self.specialization}-focused solution"
        ]
        
        return "\n".join(summary_parts)
    
    async def _save_artifacts(
        self,
        subtask_id: int,
        autogen_result: Dict[str, Any],
        summary: str,
        review_result: Dict[str, Any] = None
    ):
        """Save conversation (raw), review notes, and summary to separate files."""
        base_path = Path(f"artifacts/subtask_{subtask_id}")
        base_path.mkdir(parents=True, exist_ok=True)
        
        # Save raw conversation
        conversation_file = base_path / "raw" / f"{self.agent_id}_conversation.json"
        conversation_file.parent.mkdir(parents=True, exist_ok=True)
        with open(conversation_file, 'w', encoding='utf-8') as f:
            json.dump(autogen_result, f, indent=2)
        
        # Save review notes if available
        if review_result:
            review_file = base_path / "reviews" / f"{self.agent_id}_review.json"
            review_file.parent.mkdir(parents=True, exist_ok=True)
            with open(review_file, 'w', encoding='utf-8') as f:
                json.dump(review_result, f, indent=2)
        
        # Save summary
        summary_file = base_path / "summaries" / f"{self.agent_id}_summary.md"
        summary_file.parent.mkdir(parents=True, exist_ok=True)
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# {self.name} - Subtask {subtask_id}\n\n")
            f.write(f"**Specialization:** {self.specialization}\n\n")
            f.write(f"## Summary\n\n{summary}\n\n")
            
            if review_result:
                f.write(f"## Code Review\n\n")
                f.write(f"**Quality Score:** {review_result.get('code_quality_score', 'N/A')}/10\n\n")
                f.write(f"**Team Feedback:** {review_result.get('team_feedback', 'N/A')}\n\n")
            
            f.write(f"**Messages:** {autogen_result.get('message_count', 0)}\n")
            f.write(f"**Timestamp:** {autogen_result.get('timestamp', 'N/A')}\n")
        
        self._print(f"📁 {self.name}: Saved artifacts to {base_path}")
        
        if self.logger:
            self.logger.log_artifact_creation(
                self.agent_id,
                str(conversation_file),
                "conversation",
                f"Subtask {subtask_id} conversation saved"
            )
    
    async def _review_and_revise_code(
        self,
        subtask_description: str,
        autogen_conversation: list,
        autogen_code: str,
        existing_codebase: str
    ) -> Dict[str, Any]:
        """
        Letta agent reviews AutoGen's work, fixes issues, and provides feedback.
        This is where Letta's intelligence comes in - it's smarter than AutoGen.
        """
        try:
            # Build review prompt for Letta
            review_prompt = f"""
You are the senior engineer overseeing your AutoGen team.

**Subtask:** {subtask_description}

**Your team's proposed code:**
```
{autogen_code[:2000]}  # Limit for context
```

**Your responsibilities:**
1. Review the code for correctness, bugs, and quality
2. Fix any issues you find
3. Provide feedback to your team (compliments or scolding as needed)
4. Extract key learnings for your persistent memory

**Respond with:**
- code_quality: (1-10 score)
- issues_found: (list of problems)
- fixed_code: (improved version if needed, or "APPROVED" if good)
- team_feedback: (what you'd tell your team - be direct!)
- learnings: (patterns/insights for future projects)
"""
            
            # Get Letta's review
            response = self.letta_client.send_message(
                agent_id=self.agent_id,
                message=review_prompt,
                role="user"
            )
            
            # Extract response (simplified - in real impl, parse structured output)
            review_text = str(response.messages[-1].content if response.messages else "")
            
            return {
                "review_text": review_text,
                "final_code": autogen_code,  # For now, keep AutoGen's code
                "code_quality_score": 7,  # Placeholder
                "team_feedback": "Good work team!",  # Placeholder
                "learnings": []  # Placeholder
            }
            
        except Exception as e:
            self._print(f"Warning: Review failed for {self.name}: {e}")
            return {
                "review_text": "Review skipped due to error",
                "final_code": autogen_code,
                "code_quality_score": 5,
                "team_feedback": "",
                "learnings": []
            }
    
    async def _update_persistent_memory(self, review_result: Dict[str, Any]):
        """
        Update the agent's persistent memory block with learnings.
        This memory survives project resets!
        """
        try:
            learnings = review_result.get("learnings", [])
            if not learnings:
                return
            
            # Get current memory blocks
            agent_info = self.letta_client.agents.get(agent_id=self.agent_id)
            blocks = agent_info.blocks if hasattr(agent_info, 'blocks') else agent_info.get('blocks', [])
            
            if not blocks:
                self._print(f"Warning: No memory blocks found for {self.name}")
                return
            
            # Find the persistent memory block (labeled "Team Knowledge Base")
            persistent_block = None
            for block in blocks:
                block_label = block.label if hasattr(block, 'label') else block.get('label')
                if block_label == "Team Knowledge Base":
                    persistent_block = block
                    break
            
            if not persistent_block:
                self._print(f"Warning: No persistent memory block found for {self.name}")
                return
            
            # Append learnings to the block
            block_id = persistent_block.id if hasattr(persistent_block, 'id') else persistent_block['id']
            current_value = persistent_block.value if hasattr(persistent_block, 'value') else persistent_block['value']
            
            new_learning = f"\n### {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            for learning in learnings:
                new_learning += f"- {learning}\n"
            
            updated_value = current_value + new_learning
            
            # Update the block
            self.letta_client.blocks.update(
                block_id=block_id,
                value=updated_value
            )
            
            self._print(f"💾 {self.name}: Updated persistent memory with {len(learnings)} learnings")
            
        except Exception as e:
            self._print(f"Warning: Could not update persistent memory for {self.name}: {e}")

