"""
Conversation Flow - Manages synchronous, turn-based conversations between agents.
"""

import asyncio
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ConversationPhase(Enum):
    """Phases of the conversation."""
    PLANNING = "planning"
    WORKING = "working"
    REVIEWING = "reviewing"
    ITERATING = "iterating"
    COMPLETING = "completing"

@dataclass
class ConversationTurn:
    """Represents a turn in the conversation."""
    agent_id: str
    agent_name: str
    message: str
    timestamp: float
    phase: ConversationPhase
    subtask_id: Optional[str] = None

class ConversationFlow:
    """Manages synchronous conversation flow between agents."""
    
    def __init__(self, message_broker, shared_memory, logger):
        self.message_broker = message_broker
        self.shared_memory = shared_memory
        self.logger = logger
        self.conversation_history = []
        self.current_phase = ConversationPhase.PLANNING
        self.turn_order = []
        self.current_turn_index = 0
        
    async def start_conversation(self, agents: List[Any], subtask) -> List[ConversationTurn]:
        """Start a synchronous conversation about a specific subtask."""
        print(f"\n💬 Starting CONVERSATION about: {subtask.title}")
        
        # Set up turn order
        self.turn_order = [agent.agent_id for agent in agents]
        self.current_turn_index = 0
        self.current_phase = ConversationPhase.PLANNING
        
        # Each agent gets a turn to discuss the subtask
        conversation_turns = []
        
        # Phase 1: Planning - Each agent shares their approach
        print(f"\n📋 PHASE 1: Planning Discussion")
        planning_turns = await self._planning_phase(agents, subtask)
        conversation_turns.extend(planning_turns)
        
        # Phase 2: Working - Agents work and share progress
        print(f"\n🔨 PHASE 2: Working & Sharing Progress")
        working_turns = await self._working_phase(agents, subtask)
        conversation_turns.extend(working_turns)
        
        # Phase 3: Reviewing - Agents review each other's work
        print(f"\n👀 PHASE 3: Review & Feedback")
        review_turns = await self._review_phase(agents, subtask)
        conversation_turns.extend(review_turns)
        
        # Phase 4: Iterating - Agents improve based on feedback
        print(f"\n🔄 PHASE 4: Iteration & Improvement")
        iteration_turns = await self._iteration_phase(agents, subtask)
        conversation_turns.extend(iteration_turns)
        
        return conversation_turns
    
    async def _planning_phase(self, agents: List[Any], subtask) -> List[ConversationTurn]:
        """Planning phase - agents discuss their approach."""
        turns = []
        self.current_phase = ConversationPhase.PLANNING
        
        for agent in agents:
            print(f"\n🎯 {agent.name}'s turn to plan...")
            
            # Agent shares their approach
            approach_message = await self._get_agent_approach(agent, subtask)
            
            # Create turn
            turn = ConversationTurn(
                agent_id=agent.agent_id,
                agent_name=agent.name,
                message=approach_message,
                timestamp=time.time(),
                phase=self.current_phase,
                subtask_id=subtask.id
            )
            turns.append(turn)
            
            # Send message to other agents
            await self._send_message_to_team(agent, approach_message, agents)
            
            # Wait a moment for realism
            await asyncio.sleep(1)
        
        return turns
    
    async def _working_phase(self, agents: List[Any], subtask) -> List[ConversationTurn]:
        """Working phase - agents work and share progress."""
        turns = []
        self.current_phase = ConversationPhase.WORKING
        
        for agent in agents:
            print(f"\n🔨 {agent.name} working on {subtask.title}...")
            
            # Agent works on the subtask
            work_result = await self._agent_work_on_subtask(agent, subtask)
            
            # Agent shares their progress
            progress_message = await self._get_agent_progress(agent, subtask, work_result)
            
            # Create turn
            turn = ConversationTurn(
                agent_id=agent.agent_id,
                agent_name=agent.name,
                message=progress_message,
                timestamp=time.time(),
                phase=self.current_phase,
                subtask_id=subtask.id
            )
            turns.append(turn)
            
            # Send message to other agents
            await self._send_message_to_team(agent, progress_message, agents)
            
            # Wait a moment for realism
            await asyncio.sleep(2)
        
        return turns
    
    async def _review_phase(self, agents: List[Any], subtask) -> List[ConversationTurn]:
        """Review phase - agents review each other's work."""
        turns = []
        self.current_phase = ConversationPhase.REVIEWING
        
        # Each agent reviews the work of others
        for reviewer in agents:
            for reviewee in agents:
                if reviewer.agent_id != reviewee.agent_id:
                    print(f"\n👀 {reviewer.name} reviewing {reviewee.name}'s work...")
                    
                    # Get review feedback
                    review_message = await self._get_agent_review(reviewer, reviewee, subtask)
                    
                    # Create turn
                    turn = ConversationTurn(
                        agent_id=reviewer.agent_id,
                        agent_name=reviewer.name,
                        message=review_message,
                        timestamp=time.time(),
                        phase=self.current_phase,
                        subtask_id=subtask.id
                    )
                    turns.append(turn)
                    
                    # Send message to the reviewee
                    await self._send_message_to_agent(reviewer, reviewee, review_message)
                    
                    # Wait a moment for realism
                    await asyncio.sleep(1)
        
        return turns
    
    async def _iteration_phase(self, agents: List[Any], subtask) -> List[ConversationTurn]:
        """Iteration phase - agents improve based on feedback."""
        turns = []
        self.current_phase = ConversationPhase.ITERATING
        
        for agent in agents:
            print(f"\n🔄 {agent.name} iterating based on feedback...")
            
            # Agent improves their work
            improvement_result = await self._agent_improve_work(agent, subtask)
            
            # Agent shares their improvements
            improvement_message = await self._get_agent_improvement(agent, subtask, improvement_result)
            
            # Create turn
            turn = ConversationTurn(
                agent_id=agent.agent_id,
                agent_name=agent.name,
                message=improvement_message,
                timestamp=time.time(),
                phase=self.current_phase,
                subtask_id=subtask.id
            )
            turns.append(turn)
            
            # Send message to other agents
            await self._send_message_to_team(agent, improvement_message, agents)
            
            # Wait a moment for realism
            await asyncio.sleep(1)
        
        return turns
    
    async def _get_agent_approach(self, agent, subtask) -> str:
        """Get agent's approach to the subtask."""
        approach_prompt = f"""
You are {agent.name} with this personality: {agent.personality}

You need to work on this subtask: {subtask.title}
Description: {subtask.description}

Share your approach with the team. Be specific about:
1. Your technical approach
2. What you plan to build
3. Any concerns or questions
4. How you'll collaborate with others

Show your personality in your response.
Keep it under 150 characters.

Generate your approach now:
"""
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: agent.client.agents.messages.create(
                    agent_id=agent.agent_id,
                    messages=[{"role": "user", "content": approach_prompt}]
                )
            )
            
            # Extract message from response
            message = ""
            for msg in response.messages:
                if hasattr(msg, 'content'):
                    message = msg.content.strip()
                    break
            
            if not message:
                message = f"My approach to {subtask.title}: I'll build it step by step."
            
            return message
            
        except Exception as e:
            print(f"❌ {agent.name} approach error: {e}")
            return f"My approach to {subtask.title}: I'll build it step by step."
    
    async def _agent_work_on_subtask(self, agent, subtask) -> Dict[str, Any]:
        """Agent works on the subtask."""
        # This would call the agent's actual work method
        # For now, return a placeholder
        return {"status": "working", "subtask_id": subtask.id}
    
    async def _get_agent_progress(self, agent, subtask, work_result) -> str:
        """Get agent's progress update."""
        progress_prompt = f"""
You are {agent.name} with this personality: {agent.personality}

You just worked on: {subtask.title}
Work result: {work_result}

Share your progress with the team. Be specific about:
1. What you built
2. Any challenges you faced
3. What's working well
4. What you need help with

Show your personality in your response.
Keep it under 150 characters.

Generate your progress update now:
"""
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: agent.client.agents.messages.create(
                    agent_id=agent.agent_id,
                    messages=[{"role": "user", "content": progress_prompt}]
                )
            )
            
            # Extract message from response
            message = ""
            for msg in response.messages:
                if hasattr(msg, 'content'):
                    message = msg.content.strip()
                    break
            
            if not message:
                message = f"Progress on {subtask.title}: Made good progress!"
            
            return message
            
        except Exception as e:
            print(f"❌ {agent.name} progress error: {e}")
            return f"Progress on {subtask.title}: Made good progress!"
    
    async def _get_agent_review(self, reviewer, reviewee, subtask) -> str:
        """Get agent's review of another agent's work."""
        review_prompt = f"""
You are {reviewer.name} with this personality: {reviewer.personality}

You're reviewing {reviewee.name}'s work on: {subtask.title}

Provide constructive feedback. You can:
1. Praise what's good
2. Point out issues or improvements needed
3. Ask questions about their approach
4. Suggest alternatives

Be honest but constructive. Show your personality.
Keep it under 150 characters.

Generate your review now:
"""
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: reviewer.client.agents.messages.create(
                    agent_id=reviewer.agent_id,
                    messages=[{"role": "user", "content": review_prompt}]
                )
            )
            
            # Extract message from response
            message = ""
            for msg in response.messages:
                if hasattr(msg, 'content'):
                    message = msg.content.strip()
                    break
            
            if not message:
                message = f"Review of {reviewee.name}'s work: Looks good overall!"
            
            return message
            
        except Exception as e:
            print(f"❌ {reviewer.name} review error: {e}")
            return f"Review of {reviewee.name}'s work: Looks good overall!"
    
    async def _agent_improve_work(self, agent, subtask) -> Dict[str, Any]:
        """Agent improves their work based on feedback."""
        # This would call the agent's improvement method
        # For now, return a placeholder
        return {"status": "improved", "subtask_id": subtask.id}
    
    async def _get_agent_improvement(self, agent, subtask, improvement_result) -> str:
        """Get agent's improvement update."""
        improvement_prompt = f"""
You are {agent.name} with this personality: {agent.personality}

You just improved your work on: {subtask.title}
Improvement result: {improvement_result}

Share your improvements with the team. Be specific about:
1. What you changed
2. How you addressed feedback
3. What's better now
4. Any remaining concerns

Show your personality in your response.
Keep it under 150 characters.

Generate your improvement update now:
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
            
            # Extract message from response
            message = ""
            for msg in response.messages:
                if hasattr(msg, 'content'):
                    message = msg.content.strip()
                    break
            
            if not message:
                message = f"Improved {subtask.title}: Made it better based on feedback!"
            
            return message
            
        except Exception as e:
            print(f"❌ {agent.name} improvement error: {e}")
            return f"Improved {subtask.title}: Made it better based on feedback!"
    
    async def _send_message_to_team(self, sender, message, agents):
        """Send message to all other agents."""
        from src.core.message_system import MessageType
        
        for agent in agents:
            if agent.agent_id != sender.agent_id:
                await self.message_broker.send_message(
                    sender.agent_id,
                    agent.agent_id,
                    message,
                    MessageType.COORDINATION
                )
    
    async def _send_message_to_agent(self, sender, receiver, message):
        """Send message to a specific agent."""
        from src.core.message_system import MessageType
        
        await self.message_broker.send_message(
            sender.agent_id,
            receiver.agent_id,
            message,
            MessageType.COORDINATION
        )
