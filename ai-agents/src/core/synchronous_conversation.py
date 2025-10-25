"""
Synchronous Conversation System using Letta's built-in multi-agent tools.
Based on: https://docs.letta.com/guides/agents/multi-agent#messaging-another-agent-wait-for-reply
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
    response: str
    timestamp: float
    phase: ConversationPhase
    subtask_id: Optional[str] = None

class SynchronousConversation:
    """Manages synchronous conversations using Letta's built-in multi-agent tools."""
    
    def __init__(self, message_broker, shared_memory, logger):
        self.message_broker = message_broker
        self.shared_memory = shared_memory
        self.logger = logger
        self.conversation_history = []
        self.current_phase = ConversationPhase.PLANNING
        
    async def start_conversation(self, agents: List[Any], subtask) -> List[ConversationTurn]:
        """Start a SYNCHRONOUS conversation about a specific subtask using Letta tools."""
        print(f"\n💬 Starting SYNCHRONOUS CONVERSATION about: {subtask.title}")
        print(f"Using Letta's built-in multi-agent tools for real conversations!")
        
        conversation_turns = []
        
        # Phase 1: Planning - Each agent shares their approach and gets responses
        print(f"\n📋 PHASE 1: Planning Discussion (SYNCHRONOUS)")
        planning_turns = await self._planning_phase_sync(agents, subtask)
        conversation_turns.extend(planning_turns)
        
        # Phase 2: Working - Agents work and share progress with responses
        print(f"\n🔨 PHASE 2: Working & Sharing Progress (SYNCHRONOUS)")
        working_turns = await self._working_phase_sync(agents, subtask)
        conversation_turns.extend(working_turns)
        
        # Phase 3: Reviewing - Agents review each other's work with responses
        print(f"\n👀 PHASE 3: Review & Feedback (SYNCHRONOUS)")
        review_turns = await self._review_phase_sync(agents, subtask)
        conversation_turns.extend(review_turns)
        
        # Phase 4: Iterating - Agents improve based on feedback
        print(f"\n🔄 PHASE 4: Iteration & Improvement (SYNCHRONOUS)")
        iteration_turns = await self._iteration_phase_sync(agents, subtask)
        conversation_turns.extend(iteration_turns)
        
        return conversation_turns
    
    async def _planning_phase_sync(self, agents: List[Any], subtask) -> List[ConversationTurn]:
        """Planning phase with SYNCHRONOUS responses using Letta tools."""
        turns = []
        self.current_phase = ConversationPhase.PLANNING
        
        # Each agent gets a turn to discuss their approach
        for i, agent in enumerate(agents):
            print(f"\n🎯 {agent.name}'s turn to plan...")
            
            # Agent shares their approach
            approach_message = await self._get_agent_approach(agent, subtask)
            
            # Get responses from other agents using Letta's synchronous messaging
            responses = []
            for other_agent in agents:
                if other_agent.agent_id != agent.agent_id:
                    print(f"  💬 {agent.name} → {other_agent.name}: {approach_message}")
                    
                    # Use Letta's send_message_to_agent_and_wait_for_reply
                    response = await self._send_message_and_wait_for_reply(
                        agent, other_agent, approach_message, subtask
                    )
                    
                    print(f"  💬 {other_agent.name} → {agent.name}: {response}")
                    responses.append(response)
            
            # Create turn with responses
            turn = ConversationTurn(
                agent_id=agent.agent_id,
                agent_name=agent.name,
                message=approach_message,
                response=" | ".join(responses),
                timestamp=time.time(),
                phase=self.current_phase,
                subtask_id=subtask.id
            )
            turns.append(turn)
            
            # Wait a moment for realism
            await asyncio.sleep(1)
        
        return turns
    
    async def _working_phase_sync(self, agents: List[Any], subtask) -> List[ConversationTurn]:
        """Working phase with SYNCHRONOUS responses."""
        turns = []
        self.current_phase = ConversationPhase.WORKING
        
        for agent in agents:
            print(f"\n🔨 {agent.name} working on {subtask.title}...")
            
            # Agent works on the subtask
            work_result = await self._agent_work_on_subtask(agent, subtask)
            
            # Agent shares their progress
            progress_message = await self._get_agent_progress(agent, subtask, work_result)
            
            # Get responses from other agents
            responses = []
            for other_agent in agents:
                if other_agent.agent_id != agent.agent_id:
                    print(f"  💬 {agent.name} → {other_agent.name}: {progress_message}")
                    
                    response = await self._send_message_and_wait_for_reply(
                        agent, other_agent, progress_message, subtask
                    )
                    
                    print(f"  💬 {other_agent.name} → {agent.name}: {response}")
                    responses.append(response)
            
            # Create turn with responses
            turn = ConversationTurn(
                agent_id=agent.agent_id,
                agent_name=agent.name,
                message=progress_message,
                response=" | ".join(responses),
                timestamp=time.time(),
                phase=self.current_phase,
                subtask_id=subtask.id
            )
            turns.append(turn)
            
            await asyncio.sleep(2)
        
        return turns
    
    async def _review_phase_sync(self, agents: List[Any], subtask) -> List[ConversationTurn]:
        """Review phase with SYNCHRONOUS responses."""
        turns = []
        self.current_phase = ConversationPhase.REVIEWING
        
        # Each agent reviews the work of others
        for reviewer in agents:
            for reviewee in agents:
                if reviewer.agent_id != reviewee.agent_id:
                    print(f"\n👀 {reviewer.name} reviewing {reviewee.name}'s work...")
                    
                    # Get review feedback
                    review_message = await self._get_agent_review(reviewer, reviewee, subtask)
                    
                    print(f"  💬 {reviewer.name} → {reviewee.name}: {review_message}")
                    
                    # Get response from reviewee
                    response = await self._send_message_and_wait_for_reply(
                        reviewer, reviewee, review_message, subtask
                    )
                    
                    print(f"  💬 {reviewee.name} → {reviewer.name}: {response}")
                    
                    # Create turn with response
                    turn = ConversationTurn(
                        agent_id=reviewer.agent_id,
                        agent_name=reviewer.name,
                        message=review_message,
                        response=response,
                        timestamp=time.time(),
                        phase=self.current_phase,
                        subtask_id=subtask.id
                    )
                    turns.append(turn)
                    
                    await asyncio.sleep(1)
        
        return turns
    
    async def _iteration_phase_sync(self, agents: List[Any], subtask) -> List[ConversationTurn]:
        """Iteration phase with SYNCHRONOUS responses."""
        turns = []
        self.current_phase = ConversationPhase.ITERATING
        
        for agent in agents:
            print(f"\n🔄 {agent.name} iterating based on feedback...")
            
            # Agent improves their work
            improvement_result = await self._agent_improve_work(agent, subtask)
            
            # Agent shares their improvements
            improvement_message = await self._get_agent_improvement(agent, subtask, improvement_result)
            
            # Get responses from other agents
            responses = []
            for other_agent in agents:
                if other_agent.agent_id != agent.agent_id:
                    print(f"  💬 {agent.name} → {other_agent.name}: {improvement_message}")
                    
                    response = await self._send_message_and_wait_for_reply(
                        agent, other_agent, improvement_message, subtask
                    )
                    
                    print(f"  💬 {other_agent.name} → {agent.name}: {response}")
                    responses.append(response)
            
            # Create turn with responses
            turn = ConversationTurn(
                agent_id=agent.agent_id,
                agent_name=agent.name,
                message=improvement_message,
                response=" | ".join(responses),
                timestamp=time.time(),
                phase=self.current_phase,
                subtask_id=subtask.id
            )
            turns.append(turn)
            
            await asyncio.sleep(1)
        
        return turns
    
    async def _send_message_and_wait_for_reply(self, sender, receiver, message, subtask) -> str:
        """Use Letta's built-in send_message_to_agent_and_wait_for_reply tool."""
        try:
            # Create a prompt that includes the multi-agent tool call
            tool_prompt = f"""
You are {sender.name} with this personality: {sender.personality}

You need to send a message to {receiver.name} about this subtask: {subtask.title}

Message to send: {message}

Use the send_message_to_agent_and_wait_for_reply tool to send this message to {receiver.agent_id} and wait for their response.

The tool signature is:
send_message_to_agent_and_wait_for_reply(message: string, otherAgentId: string): string

Call the tool now and return the response you receive.
"""
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: sender.client.agents.messages.create(
                    agent_id=sender.agent_id,
                    messages=[{"role": "user", "content": tool_prompt}]
                )
            )
            
            # Extract response from Letta
            response_text = ""
            for msg in response.messages:
                if hasattr(msg, 'content'):
                    response_text = msg.content.strip()
                    break
            
            if not response_text:
                response_text = "Thanks for the message!"
            
            return response_text
            
        except Exception as e:
            print(f"❌ {sender.name} → {receiver.name} messaging error: {e}")
            return "Thanks for the message!"
    
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
