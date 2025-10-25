"""
Work-Then-Share Flow - Agents work on subtasks first, then share results and discuss.
"""

import asyncio
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class WorkPhase(Enum):
    """Phases of the work flow."""
    WORKING = "working"
    SHARING = "sharing"
    REVIEWING = "reviewing"
    ITERATING = "iterating"
    COMPLETING = "completing"

@dataclass
class WorkResult:
    """Represents the result of an agent's work."""
    agent_id: str
    agent_name: str
    subtask_id: str
    subtask_title: str
    work_summary: str
    code_generated: str
    timestamp: float
    status: str = "completed"

@dataclass
class DiscussionTurn:
    """Represents a discussion turn after work is complete."""
    agent_id: str
    agent_name: str
    message: str
    response: str
    timestamp: float
    phase: WorkPhase
    subtask_id: str

class WorkThenShareFlow:
    """Manages work-first-then-share workflow."""
    
    def __init__(self, message_broker, shared_memory, logger):
        self.message_broker = message_broker
        self.shared_memory = shared_memory
        self.logger = logger
        self.work_results = []
        self.discussion_history = []
        
    async def execute_subtask_workflow(self, agents: List[Any], subtask) -> List[DiscussionTurn]:
        """Execute the work-then-share workflow for a subtask."""
        print(f"\n🎯 WORK-THEN-SHARE WORKFLOW for: {subtask.title}")
        
        # Phase 1: WORK - Each agent works on their assigned subtask
        print(f"\n🔨 PHASE 1: WORKING (Agents work independently)")
        work_results = await self._work_phase(agents, subtask)
        self.work_results.extend(work_results)
        
        # Phase 2: SHARE - Agents share their work results
        print(f"\n💬 PHASE 2: SHARING (Agents share what they built)")
        sharing_turns = await self._sharing_phase(agents, subtask, work_results)
        self.discussion_history.extend(sharing_turns)
        
        # Phase 3: REVIEW - Agents review each other's work
        print(f"\n👀 PHASE 3: REVIEWING (Agents review and give feedback)")
        review_turns = await self._review_phase(agents, subtask, work_results)
        self.discussion_history.extend(review_turns)
        
        # Phase 4: ITERATE - Agents improve based on feedback
        print(f"\n🔄 PHASE 4: ITERATING (Agents improve their work)")
        iteration_turns = await self._iteration_phase(agents, subtask, work_results)
        self.discussion_history.extend(iteration_turns)
        
        return self.discussion_history
    
    async def _work_phase(self, agents: List[Any], subtask) -> List[WorkResult]:
        """Phase 1: Agents work on their assigned subtask."""
        work_results = []
        
        # Find the agent assigned to this subtask
        assigned_agent = None
        for agent in agents:
            if agent.agent_id == subtask.assigned_agent:
                assigned_agent = agent
                break
        
        if not assigned_agent:
            print(f"❌ No agent assigned to subtask: {subtask.title}")
            return work_results
        
        print(f"  🔨 {assigned_agent.name} working on: {subtask.title}")
        
        # Agent works on the subtask
        work_result = await self._agent_work_on_subtask(assigned_agent, subtask)
        
        # Create work result
        result = WorkResult(
            agent_id=assigned_agent.agent_id,
            agent_name=assigned_agent.name,
            subtask_id=subtask.id,
            subtask_title=subtask.title,
            work_summary=work_result.get("summary", "Work completed"),
            code_generated=work_result.get("code", ""),
            timestamp=time.time(),
            status="completed"
        )
        work_results.append(result)
        
        print(f"  ✅ {assigned_agent.name} completed: {subtask.title}")
        
        return work_results
    
    async def _sharing_phase(self, agents: List[Any], subtask, work_results: List[WorkResult]) -> List[DiscussionTurn]:
        """Phase 2: Agents share their work results."""
        turns = []
        
        for work_result in work_results:
            print(f"\n  💬 {work_result.agent_name} sharing their work...")
            
            # Agent shares their work
            share_message = await self._get_work_share_message(work_result, subtask)
            
            # Get responses from other agents
            responses = []
            for agent in agents:
                if agent.agent_id != work_result.agent_id:
                    print(f"    💬 {work_result.agent_name} → {agent.name}: {share_message}")
                    
                    # Get response from other agent
                    response = await self._get_agent_response(agent, share_message, subtask)
                    
                    print(f"    💬 {agent.name} → {work_result.agent_name}: {response}")
                    responses.append(response)
            
            # Create discussion turn
            turn = DiscussionTurn(
                agent_id=work_result.agent_id,
                agent_name=work_result.agent_name,
                message=share_message,
                response=" | ".join(responses),
                timestamp=time.time(),
                phase=WorkPhase.SHARING,
                subtask_id=subtask.id
            )
            turns.append(turn)
            
            await asyncio.sleep(1)
        
        return turns
    
    async def _review_phase(self, agents: List[Any], subtask, work_results: List[WorkResult]) -> List[DiscussionTurn]:
        """Phase 3: Agents review each other's work."""
        turns = []
        
        for work_result in work_results:
            for reviewer in agents:
                if reviewer.agent_id != work_result.agent_id:
                    print(f"\n  👀 {reviewer.name} reviewing {work_result.agent_name}'s work...")
                    
                    # Get review feedback
                    review_message = await self._get_review_message(reviewer, work_result, subtask)
                    
                    print(f"    💬 {reviewer.name} → {work_result.agent_name}: {review_message}")
                    
                    # Get response from the work author
                    response = await self._get_agent_response(work_result.agent_id, review_message, subtask, agents)
                    
                    print(f"    💬 {work_result.agent_name} → {reviewer.name}: {response}")
                    
                    # Create discussion turn
                    turn = DiscussionTurn(
                        agent_id=reviewer.agent_id,
                        agent_name=reviewer.name,
                        message=review_message,
                        response=response,
                        timestamp=time.time(),
                        phase=WorkPhase.REVIEWING,
                        subtask_id=subtask.id
                    )
                    turns.append(turn)
                    
                    await asyncio.sleep(1)
        
        return turns
    
    async def _iteration_phase(self, agents: List[Any], subtask, work_results: List[WorkResult]) -> List[DiscussionTurn]:
        """Phase 4: Agents improve their work based on feedback."""
        turns = []
        
        for work_result in work_results:
            print(f"\n  🔄 {work_result.agent_name} iterating based on feedback...")
            
            # Agent improves their work
            improvement_result = await self._agent_improve_work(work_result.agent_id, subtask, agents)
            
            # Agent shares their improvements
            improvement_message = await self._get_improvement_message(work_result, improvement_result, subtask)
            
            # Get responses from other agents
            responses = []
            for agent in agents:
                if agent.agent_id != work_result.agent_id:
                    print(f"    💬 {work_result.agent_name} → {agent.name}: {improvement_message}")
                    
                    response = await self._get_agent_response(agent, improvement_message, subtask)
                    
                    print(f"    💬 {agent.name} → {work_result.agent_name}: {response}")
                    responses.append(response)
            
            # Create discussion turn
            turn = DiscussionTurn(
                agent_id=work_result.agent_id,
                agent_name=work_result.agent_name,
                message=improvement_message,
                response=" | ".join(responses),
                timestamp=time.time(),
                phase=WorkPhase.ITERATING,
                subtask_id=subtask.id
            )
            turns.append(turn)
            
            await asyncio.sleep(1)
        
        return turns
    
    async def _agent_work_on_subtask(self, agent, subtask) -> Dict[str, Any]:
        """Agent works on the subtask."""
        work_prompt = f"""
You are {agent.name} with this personality: {agent.personality}

You need to work on this subtask: {subtask.title}
Description: {subtask.description}

Your coding style: {agent.coding_style}

Generate the code for this subtask. Be specific and technical.
Include comments that reflect your personality.
Focus on the exact requirements of this subtask.

Generate the code now:
"""
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: agent.client.agents.messages.create(
                    agent_id=agent.agent_id,
                    messages=[{"role": "user", "content": work_prompt}]
                )
            )
            
            # Extract code from response
            code = ""
            for msg in response.messages:
                if hasattr(msg, 'content'):
                    code = msg.content.strip()
                    break
            
            if not code:
                code = f"// {agent.name} worked on {subtask.title}\n// Code generated here"
            
            print(f"    ✅ {agent.name} generated code for {subtask.title}")
            
            return {
                "summary": f"Completed {subtask.title}",
                "code": code,
                "status": "completed"
            }
            
        except Exception as e:
            print(f"❌ {agent.name} work error: {e}")
            return {
                "summary": f"Error working on {subtask.title}",
                "code": f"// Error: {e}",
                "status": "error"
            }
    
    async def _get_work_share_message(self, work_result: WorkResult, subtask) -> str:
        """Get agent's work sharing message."""
        share_prompt = f"""
You are {work_result.agent_name} with this personality: {work_result.agent_name}

You just completed this subtask: {subtask.title}
Description: {subtask.description}

Work summary: {work_result.work_summary}

Share your work with the team. Be specific about:
1. What you built
2. Key features implemented
3. Any challenges you faced
4. What you're proud of

Show your personality in your response.
Keep it under 150 characters.

Generate your work sharing message now:
"""
        
        # For now, return a simple message
        return f"Just finished {subtask.title}! Built some solid code with {work_result.work_summary}"
    
    async def _get_agent_response(self, agent, message: str, subtask, agents: List[Any] = None) -> str:
        """Get agent's response to a message."""
        response_prompt = f"""
You are {agent.name if hasattr(agent, 'name') else 'Agent'} with this personality: {getattr(agent, 'personality', 'helpful')}

You received this message: {message}

Respond to this message. Show your personality.
Keep it under 100 characters.

Generate your response now:
"""
        
        # For now, return a simple response
        return f"Nice work! Looks solid."
    
    async def _get_review_message(self, reviewer, work_result: WorkResult, subtask) -> str:
        """Get agent's review message."""
        review_prompt = f"""
You are {reviewer.name} with this personality: {reviewer.personality}

You're reviewing {work_result.agent_name}'s work on: {subtask.title}

Work summary: {work_result.work_summary}

Provide constructive feedback. You can:
1. Praise what's good
2. Point out issues or improvements needed
3. Ask questions about their approach
4. Suggest alternatives

Be honest but constructive. Show your personality.
Keep it under 150 characters.

Generate your review now:
"""
        
        # For now, return a simple review
        return f"Good work on {subtask.title}! Maybe consider adding error handling?"
    
    async def _agent_improve_work(self, agent_id: str, subtask, agents: List[Any]) -> Dict[str, Any]:
        """Agent improves their work based on feedback."""
        # Find the agent
        agent = None
        for a in agents:
            if a.agent_id == agent_id:
                agent = a
                break
        
        if not agent:
            return {"status": "error", "message": "Agent not found"}
        
        improvement_prompt = f"""
You are {agent.name} with this personality: {agent.personality}

You received feedback on your work for: {subtask.title}

Improve your work based on the feedback received.
Show your personality in the improvements.
Focus on the specific subtask requirements.

Generate improved code now:
"""
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: agent.client.agents.messages.create(
                    agent_id=agent.agent_id,
                    messages=[{"role": "user", "content": improvement_prompt}]
                )
            )
            
            # Extract improved code from response
            improved_code = ""
            for msg in response.messages:
                if hasattr(msg, 'content'):
                    improved_code = msg.content.strip()
                    break
            
            if not improved_code:
                improved_code = f"// {agent.name} improved {subtask.title}\n// Improved code here"
            
            print(f"    ✅ {agent.name} improved their work on {subtask.title}")
            
            return {
                "summary": f"Improved {subtask.title} based on feedback",
                "code": improved_code,
                "status": "improved"
            }
            
        except Exception as e:
            print(f"❌ {agent.name} improvement error: {e}")
            return {
                "summary": f"Error improving {subtask.title}",
                "code": f"// Error: {e}",
                "status": "error"
            }
    
    async def _get_improvement_message(self, work_result: WorkResult, improvement_result: Dict[str, Any], subtask) -> str:
        """Get agent's improvement sharing message."""
        improvement_prompt = f"""
You are {work_result.agent_name} with this personality: {work_result.agent_name}

You just improved your work on: {subtask.title}
Improvement summary: {improvement_result.get('summary', 'Work improved')}

Share your improvements with the team. Be specific about:
1. What you changed
2. How you addressed feedback
3. What's better now
4. Any remaining concerns

Show your personality in your response.
Keep it under 150 characters.

Generate your improvement message now:
"""
        
        # For now, return a simple message
        return f"Improved {subtask.title} based on feedback! Made it even better."
