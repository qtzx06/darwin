"""
Commentator Agent - Narrates the conversation and collaboration between coding agents.
"""

import asyncio
import time
from typing import List, Dict, Any
from letta_client import Letta

class CommentatorAgent:
    """Narrates the conversation and collaboration happening between agents."""
    
    def __init__(self, client: Letta, agent_id: str, logger):
        self.client = client
        self.agent_id = agent_id
        self.logger = logger
        self.conversation_history = []
        self.project_context = {}
        
    async def narrate_conversation(self, agents: List[Any], message_broker, shared_memory):
        """Narrate the ongoing conversation between agents."""
        print(f"\n🎙️ COMMENTATOR: Let me observe what's happening in the team...")
        
        # Get recent messages
        recent_messages = await message_broker.get_recent_messages(limit=5)
        
        if not recent_messages:
            print(f"🎙️ COMMENTATOR: The team is just getting started...")
            return
        
        # Analyze the conversation
        conversation_summary = await self._analyze_conversation(recent_messages, agents)
        
        # Narrate what's happening
        await self._narrate_activity(conversation_summary, agents)
        
        # Store in conversation history
        self.conversation_history.append({
            "timestamp": time.time(),
            "summary": conversation_summary,
            "messages_count": len(recent_messages)
        })
    
    async def _analyze_conversation(self, messages: List[Any], agents: List[Any]) -> Dict[str, Any]:
        """Analyze the conversation to understand what's happening."""
        analysis_prompt = f"""
You are a project manager commentator observing a development team conversation.

Recent messages between agents:
{self._format_messages_for_analysis(messages)}

Team members:
{self._format_agents_for_analysis(agents)}

Analyze this conversation and provide insights about:
1. What technical topics are being discussed
2. What collaboration is happening
3. Any conflicts or disagreements
4. The overall team dynamics
5. What progress is being made

Format your analysis as a brief, engaging commentary (2-3 sentences max).
Be conversational and insightful, like a real PM observing the team.
"""
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.agents.messages.create(
                    agent_id=self.agent_id,
                    messages=[{"role": "user", "content": analysis_prompt}]
                )
            )
            
            # Extract analysis from response
            analysis = ""
            for msg in response.messages:
                if hasattr(msg, 'content'):
                    analysis = msg.content.strip()
                    break
            
            if not analysis:
                analysis = "The team is actively collaborating on the project."
            
            return {
                "analysis": analysis,
                "message_count": len(messages),
                "topics": self._extract_topics(messages),
                "collaboration_level": self._assess_collaboration(messages)
            }
            
        except Exception as e:
            print(f"❌ Commentator analysis error: {e}")
            return {
                "analysis": "The team is working together on the project.",
                "message_count": len(messages),
                "topics": ["development"],
                "collaboration_level": "moderate"
            }
    
    def _format_messages_for_analysis(self, messages: List[Any]) -> str:
        """Format messages for analysis."""
        formatted = []
        for msg in messages:
            formatted.append(f"{msg.from_agent}: {msg.content}")
        return "\n".join(formatted)
    
    def _format_agents_for_analysis(self, agents: List[Any]) -> str:
        """Format agent info for analysis."""
        formatted = []
        for agent in agents:
            formatted.append(f"- {agent.name}: {agent.personality}")
        return "\n".join(formatted)
    
    def _extract_topics(self, messages: List[Any]) -> List[str]:
        """Extract technical topics from messages."""
        topics = set()
        for msg in messages:
            content = msg.content.lower()
            if "react" in content or "frontend" in content:
                topics.add("frontend")
            if "api" in content or "backend" in content:
                topics.add("backend")
            if "database" in content or "db" in content:
                topics.add("database")
            if "ui" in content or "design" in content:
                topics.add("ui/design")
            if "performance" in content or "optimization" in content:
                topics.add("performance")
        return list(topics)
    
    def _assess_collaboration(self, messages: List[Any]) -> str:
        """Assess the level of collaboration."""
        if len(messages) < 3:
            return "low"
        elif len(messages) < 8:
            return "moderate"
        else:
            return "high"
    
    async def _narrate_activity(self, summary: Dict[str, Any], agents: List[Any]):
        """Narrate the current activity."""
        print(f"\n🎙️ COMMENTATOR: {summary['analysis']}")
        
        if summary['topics']:
            print(f"🎙️ COMMENTATOR: I can see they're discussing: {', '.join(summary['topics'])}")
        
        if summary['collaboration_level'] == "high":
            print(f"🎙️ COMMENTATOR: Great collaboration happening! {summary['message_count']} messages exchanged.")
        elif summary['collaboration_level'] == "moderate":
            print(f"🎙️ COMMENTATOR: Good team communication with {summary['message_count']} messages.")
        else:
            print(f"🎙️ COMMENTATOR: Team is just getting started with {summary['message_count']} messages.")
    
    async def provide_project_summary(self, orchestrator, agents: List[Any]):
        """Provide a summary of the entire project."""
        print(f"\n🎙️ COMMENTATOR: Let me give you a project summary...")
        
        # Get project status
        status = orchestrator.get_project_status()
        
        # Get agent stats
        agent_stats = []
        for agent in agents:
            agent_status = await agent.get_status()
            agent_stats.append({
                "name": agent_status['name'],
                "messages": agent_status['messages_sent'],
                "working": agent_status['is_working']
            })
        
        # Generate summary
        summary_prompt = f"""
You are a project manager providing a final project summary.

Project Status:
- Total subtasks: {status['total_subtasks']}
- Completed: {status['completed_subtasks']}
- Progress: {status['progress_percentage']:.1f}%

Team Performance:
{self._format_agent_stats(agent_stats)}

Provide a brief, professional summary of the project completion and team performance.
Be encouraging but honest about the results.
"""
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.agents.messages.create(
                    agent_id=self.agent_id,
                    messages=[{"role": "user", "content": summary_prompt}]
                )
            )
            
            # Extract summary from response
            summary = ""
            for msg in response.messages:
                if hasattr(msg, 'content'):
                    summary = msg.content.strip()
                    break
            
            if not summary:
                summary = f"Project completed with {status['progress_percentage']:.1f}% progress."
            
            print(f"🎙️ COMMENTATOR: {summary}")
            
        except Exception as e:
            print(f"❌ Commentator summary error: {e}")
            print(f"🎙️ COMMENTATOR: Project completed with {status['progress_percentage']:.1f}% progress.")
    
    def _format_agent_stats(self, agent_stats: List[Dict]) -> str:
        """Format agent statistics for summary."""
        formatted = []
        for stats in agent_stats:
            status = "working" if stats['working'] else "idle"
            formatted.append(f"- {stats['name']}: {stats['messages']} messages, {status}")
        return "\n".join(formatted)
