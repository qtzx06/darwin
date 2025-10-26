"""
Competitive Workflow Manager - Manages the competitive subtask cycle where all 4 agents work on the same subtask.
"""

import asyncio
import os
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Subtask:
    """Represents a subtask for competitive work."""
    id: str
    title: str
    description: str
    round_num: int
    status: str = "pending"  # pending, in_progress, completed

@dataclass
class AgentWorkResult:
    """Result of an agent's work on a subtask."""
    agent_name: str
    agent_id: str
    code: str
    metadata: Dict[str, Any]
    timestamp: float

@dataclass
class ChatMessage:
    """Represents a message in the agent chat."""
    agent_name: str
    agent_id: str
    message: str
    message_type: str  # "presentation", "question", "response", "critique", "defense"
    timestamp: float
    personality: str

class CompetitiveWorkflow:
    """Manages competitive workflow where all agents work on same subtask."""
    
    def __init__(self, artifact_manager, shared_memory, message_broker, logger, client):
        self.artifact_manager = artifact_manager
        self.shared_memory = shared_memory
        self.message_broker = message_broker
        self.logger = logger
        self.client = client
        self.current_project_id = None
        self.current_round = 0
        self.agent_stats = {}  # Track wins per agent
        
        # LiveKit voice commentary components
        self.battle_context = None
        self.voice_commentator = None
        self.livekit_enabled = False
    
    async def start_competitive_project(self, project_name: str, main_task: str, 
                                      agents: List[Any], commentator, orchestrator) -> str:
        """Start a new competitive project."""
        # Generate project ID
        project_id = f"project_{int(time.time())}"
        self.current_project_id = project_id
        
        # Initialize battle context for voice commentary
        await self._initialize_voice_commentary(project_name, main_task, agents, commentator)
        
        # Create project workspace
        await self.artifact_manager.create_project_workspace(project_id, project_name)
        
        # Initialize shared memory
        await self.shared_memory.write("project_context", {
            "project_id": project_id,
            "project_name": project_name,
            "canonical_code": "",
            "current_round": 0,
            "subtask_history": [],
            "completed": False
        })
        
        # Initialize agent stats
        for agent in agents:
            agent_config = agent.get("config")
            agent_name = agent_config.name if agent_config else agent.get("name", "Unknown")
            self.agent_stats[agent_name] = {"wins": 0, "total_rounds": 0}
        
        print(f"🚀 Started competitive project: {project_name} ({project_id})")
        
        # Announce battle start with voice commentary
        if self.voice_commentator:
            await self.voice_commentator.speak_commentary("battle_start", 
                f"Welcome to the AI coding battle! We're building: {project_name}")
        
        # Use orchestrator to break down the main task
        subtasks = await orchestrator.orchestrate_project(main_task, agents)
        
        # Process each subtask competitively
        for subtask in subtasks:
            await self._execute_competitive_round(subtask, agents, commentator, orchestrator)
        
        # Mark project as completed
        await self._complete_project(agents, commentator)
        
        return project_id
    
    async def _initialize_voice_commentary(self, project_name: str, main_task: str, 
                                         agents: List[Any], commentator):
        """Initialize voice commentary components if LiveKit is available"""
        try:
            # Import LiveKit components
            from src.livekit.battle_context import BattleContextManager
            from src.livekit.room_manager import room_manager
            from src.livekit.voice_commentator import VoiceCommentator
            
            # Check if LiveKit is available
            if not room_manager.is_available():
                print("⚠️ LiveKit not configured - voice commentary disabled")
                return
            
            # Create battle context manager
            self.battle_context = BattleContextManager()
            await self.battle_context.initialize_battle(
                self.current_project_id, 
                project_name, 
                total_rounds=4
            )
            
            # Create LiveKit room
            room_result = await room_manager.create_battle_room(self.current_project_id)
            if not room_result["success"]:
                print(f"❌ Failed to create LiveKit room: {room_result['error']}")
                return
            
            # TODO: Create actual LiveKit room connection
            # For now, we'll use a mock room object
            class MockRoom:
                def __init__(self): pass
                class local_participant:
                    def publish_track(self, track): pass
            
            mock_room = MockRoom()
            
            # Create voice commentator
            self.voice_commentator = VoiceCommentator(
                letta_commentator=commentator,
                battle_context=self.battle_context,
                room=mock_room
            )
            
            self.livekit_enabled = True
            print("🎙️ Voice commentary initialized successfully!")
            
        except ImportError as e:
            print(f"⚠️ LiveKit components not available: {e}")
            print("   Voice commentary disabled")
        except Exception as e:
            print(f"❌ Failed to initialize voice commentary: {e}")
    
    async def _execute_competitive_round(self, subtask: Subtask, agents: List[Any], 
                                       commentator, orchestrator) -> AgentWorkResult:
        """Execute a competitive round for a subtask."""
        print(f"\n{'='*60}")
        print(f"🎯 ROUND {subtask.round_num}: {subtask.title}")
        print(f"{'='*60}")
        
        self.current_round = subtask.round_num
        
        # Update battle context and announce round start
        if self.battle_context:
            await self.battle_context.update_round_start(
                subtask.title, 
                subtask.description, 
                subtask.round_num
            )
        
        if self.voice_commentator:
            await self.voice_commentator.announce_round_start(subtask.title, subtask.round_num)
        
        # Step 1: All agents work on the same subtask
        print(f"\n🔨 PHASE 1: All agents working on '{subtask.title}'...")
        work_results = await self._all_agents_work(subtask, agents)
        
        # Step 2: Quick commentary + User decision (merged)
        print(f"\n🎙️ PHASE 2: Quick analysis + User decision...")
        winner = await self._quick_commentary_and_decision(work_results, subtask, commentator)
        
        # Step 3: Process winner and learning
        print(f"\n🧠 PHASE 3: Processing winner...")
        await self._process_winner(winner, work_results, agents, commentator)
        
        # Announce winner with voice commentary
        if self.voice_commentator and hasattr(winner, 'agent_name'):
            await self.voice_commentator.announce_winner(
                winner.agent_name, 
                "User selected this approach!"
            )
        
        return winner
    
    def _get_generic_progress_messages(self, agents: List[Any], subtask: Subtask) -> Dict[str, List[str]]:
        """Get generic spicy progress messages for all agents - INSTANT!"""
        import random
        
        # MASSIVE pool of spicy progress messages
        start_messages = [
            "🔥 Starting work - time to show these amateurs how it's done!",
            "⚡ INITIATING PROTOCOL - building something that actually works!",
            "🎯 Mission accepted - time to drop some knowledge bombs!",
            "🚀 Launching into battle - let's see who's really the GOAT!",
            "💥 Entering the arena - prepare for some next-level coding!",
            "🔥 Warming up the engines - this is about to get SPICY!",
            "⚡ Activating beast mode - time to show what real skill looks like!",
            "🎯 Locking and loading - prepare for some fire code!",
            "🚀 Igniting the rockets - let's see who can keep up!",
            "💥 Dropping into the zone - this is where legends are made!"
        ]
        
        progress_messages = [
            "⚡ Implementing core functionality - building something that actually works!",
            "🎯 Adding the magic sauce - making this bulletproof!",
            "🔥 Crafting the perfect solution - no compromises!",
            "⚡ Optimizing for performance - speed is everything!",
            "🎯 Adding defensive programming - bulletproofing this beast!",
            "🔥 Implementing type safety - no runtime surprises!",
            "⚡ Adding accessibility features - inclusive by design!",
            "🎯 Writing comprehensive tests - quality first!",
            "🔥 Adding error handling - graceful failures only!",
            "⚡ Optimizing the architecture - scalable and maintainable!",
            "🎯 Adding documentation - future devs will thank me!",
            "🔥 Implementing best practices - this is how it's done!",
            "⚡ Adding performance optimizations - blazing fast!",
            "🎯 Creating reusable components - DRY principle!",
            "🔥 Adding security measures - locked down tight!"
        ]
        
        polish_messages = [
            "🎯 Adding polish and testing - making this bulletproof!",
            "🔥 Final touches - perfection is in the details!",
            "⚡ Adding the finishing touches - this is art!",
            "🎯 Quality assurance complete - bulletproof!",
            "🔥 Adding the secret sauce - this is next level!",
            "⚡ Final optimizations - peak performance achieved!",
            "🎯 Code review complete - this is flawless!",
            "🔥 Adding the cherry on top - masterpiece complete!",
            "⚡ Final testing phase - everything checks out!",
            "🎯 Documentation finalized - future-proofed!",
            "🔥 Performance tuning complete - lightning fast!",
            "⚡ Security audit passed - locked down!",
            "🎯 Accessibility verified - inclusive design!",
            "🔥 Code cleanup done - pristine and clean!",
            "⚡ Final validation - this is production ready!"
        ]
        
        completion_messages = [
            "🏆 Completed - another victory for the GOAT!",
            "🔥 Mission accomplished - that's how you do it!",
            "⚡ Victory achieved - another flawless execution!",
            "🎯 Task completed - perfection delivered!",
            "🔥 Another win in the books - unstoppable!",
            "⚡ Mission successful - that's championship level!",
            "🎯 Objective achieved - another masterpiece!",
            "🔥 Victory secured - the GOAT strikes again!",
            "⚡ Task completed - flawless execution!",
            "🎯 Mission accomplished - that's skill!",
            "🔥 Another victory - this is my domain!",
            "⚡ Objective completed - perfection achieved!",
            "🎯 Task finished - another masterpiece delivered!",
            "🔥 Victory achieved - unstoppable force!",
            "⚡ Mission complete - that's how legends are made!"
        ]
        
        # Assign random messages to each agent
        planned_messages = {}
        for agent in agents:
            agent_config = agent.get("config")
            if agent_config:
                agent_name = agent_config.name
            else:
                agent_name = agent.get("name", "Unknown")
            
            # Pick random messages for this agent
            planned_messages[agent_name] = [
                random.choice(start_messages),
                random.choice(progress_messages),
                random.choice(polish_messages),
                random.choice(completion_messages)
            ]
        
        return planned_messages
    
    async def _simulate_real_time_progress(self, planned_messages: Dict[str, List[str]], tasks: List[asyncio.Task]):
        """Simulate real-time progress using planned messages."""
        import random
        
        # Create a timeline of all progress messages (FASTER!)
        timeline = []
        for agent_name, messages in planned_messages.items():
            for i, message in enumerate(messages):
                timeline.append({
                    'agent': agent_name,
                    'message': message,
                    'step': i + 1,
                    'delay': random.uniform(0.5, 1.5) + (i * 1.0)  # Much faster: 0.5-1.5 seconds + 1 second per step
                })
        
        # Sort timeline by delay
        timeline.sort(key=lambda x: x['delay'])
        
        # Show progress messages in real-time
        start_time = asyncio.get_event_loop().time()
        
        for event in timeline:
            # Wait for the delay
            await asyncio.sleep(event['delay'])
            
            # Show the progress message
            print(f"\n🔥 {event['agent']} PROGRESS UPDATE:")
            print(f"   {event['step']}. {event['message']}")
            
            # Update battle context and announce progress with voice commentary
            if self.battle_context:
                await self.battle_context.update_agent_progress(event['agent'], event['message'])
            
            if self.voice_commentator:
                await self.voice_commentator.announce_agent_progress(event['agent'], event['message'])
            
            # Check if any tasks are done
            done_tasks = [task for task in tasks if task.done()]
            if done_tasks:
                for task in done_tasks:
                    try:
                        result = await task
                        if hasattr(result, 'agent_name'):
                            print(f"✅ {result.agent_name} completed their solution!")
                    except Exception as e:
                        print(f"❌ Agent failed: {e}")
        
        # Wait for any remaining tasks
        await asyncio.gather(*tasks, return_exceptions=True)
        print(f"\n🎉 ALL AGENTS COMPLETE!")
    
    async def _quick_commentary_and_decision(self, work_results: List[AgentWorkResult], 
                                           subtask: Subtask, commentator: Any) -> AgentWorkResult:
        """Quick commentary + user decision in one phase."""
        print(f"\n🎙️ QUICK ANALYSIS:")
        
        # Quick analysis
        analysis_prompt = f"""
Quick analysis of {len(work_results)} approaches for: {subtask.title}

AGENTS: {', '.join([r.agent_name for r in work_results])}

Give a 2-sentence analysis: Who's the MVP and why? Be exciting!
"""
        
        try:
            response = self.client.agents.messages.create(
                agent_id=commentator.agent_id,
                messages=[{"role": "user", "content": analysis_prompt}]
            )
            
            analysis = ""
            if hasattr(response, 'messages') and response.messages:
                for msg in response.messages:
                    if hasattr(msg, 'content') and msg.content:
                        analysis = msg.content.strip()
                        break
            
            if analysis:
                print(f"🎙️ {analysis}")
            else:
                print(f"🎙️ All approaches look solid! Time to pick a winner!")
                
        except Exception as e:
            print(f"🎙️ Quick analysis failed: {e}")
            print(f"🎙️ All approaches look solid! Time to pick a winner!")
        
        # User decision
        return await self._get_user_decision(work_results, subtask)
    
    async def _all_agents_work(self, subtask: Subtask, agents: List[Any]) -> List[AgentWorkResult]:
        """All agents work on the same subtask in parallel with exciting commentary."""
        work_results = []
        
        # Get current canonical code
        shared_context = await self.shared_memory.read("project_context") or {}
        canonical_code = shared_context.get("canonical_code", "")
        
        # Phase 1: Exciting work start commentary
        print(f"\n🔥 PHASE 1 COMMENTARY: The coding battle begins!")
        print(f"🎯 Mission: {subtask.title}")
        print(f"📝 Description: {subtask.description}")
        print(f"🤖 Competitors: {', '.join([agent.get('config', {}).name or agent.get('name', 'Unknown') for agent in agents])}")
        print(f"⚡ All agents are diving into their coding environments...")
        
        # Create work tasks for all agents
        work_tasks = []
        for agent in agents:
            task = self._agent_work_on_subtask(agent, subtask, canonical_code)
            work_tasks.append(task)
        
        # Step 1: Get generic progress messages INSTANTLY
        print(f"🚀 Generating battle plans...")
        planned_messages = self._get_generic_progress_messages(agents, subtask)
        
        # Step 2: Execute all agents in parallel with simulated real-time progress
        print(f"🚀 Launching parallel coding sessions...")
        
        # Start all tasks
        tasks = [asyncio.create_task(task) for task in work_tasks]
        
        # Simulate real-time progress using planned messages
        await self._simulate_real_time_progress(planned_messages, tasks)
        
        # Get all results
        results = []
        for task in tasks:
            try:
                result = await task
                results.append(result)
            except Exception as e:
                results.append(e)
        
        # Process results with exciting commentary
        print(f"\n🎉 PHASE 1 COMPLETE: All agents have finished coding!")
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Extract agent name from factory structure
                agent_config = agents[i].get("config")
                agent_name = agent_config.name if agent_config else agents[i].get("name", "Unknown")
                print(f"❌ {agent_name} encountered an error: {result}")
                continue
            
            work_results.append(result)
            print(f"✅ {result.agent_name} delivered their solution!")
        
        print(f"🏆 All {len(work_results)} agents completed their implementations!")
        return work_results
    
    async def _smart_batch_commentary(self, work_results: List[AgentWorkResult], subtask: Subtask, commentator: Any):
        """Generate exciting batch commentary after all agents finish work."""
        if not work_results:
            return
            
        print(f"\n🎙️ SMART BATCH COMMENTARY: Analyzing {len(work_results)} approaches...")
        
        # Collect all progress messages and code previews
        agent_summaries = []
        for result in work_results:
            progress_messages = result.metadata.get("progress_messages", [])
            code_preview = result.code[:500] + "..." if len(result.code) > 500 else result.code
            
            agent_summaries.append({
                "name": result.agent_name,
                "personality": result.metadata.get("personality", "Unknown"),
                "progress": progress_messages,
                "code_preview": code_preview,
                "approach": f"{result.agent_name}'s {subtask.title} approach"
            })
        
        # Create exciting batch analysis prompt
        batch_prompt = f"""
You are a project manager analyzing a competitive coding round!

SUBTASK: {subtask.title}

AGENT APPROACHES:
{self._format_agent_summaries(agent_summaries)}

Provide a short analysis covering:
1. Who's the MVP and why?
2. How did personalities shine?
3. Technical highlights
4. Overall vibe

Make it exciting! Use emojis. Format: 1-2 sentences per agent + summary.
"""
        
        try:
            # Send batch analysis to commentator with better error handling
            response = self.client.agents.messages.create(
                agent_id=commentator.agent_id,
                messages=[{"role": "user", "content": batch_prompt}]
            )
            
            # Extract and display the exciting analysis
            analysis = ""
            if hasattr(response, 'messages') and response.messages:
                for msg in response.messages:
                    if hasattr(msg, 'content') and msg.content:
                        analysis = msg.content.strip()
                        break
            
            if analysis:
                print(f"\n🎙️ COMMENTATOR BATCH ANALYSIS:")
                print(f"{'='*60}")
                print(analysis)
                print(f"{'='*60}")
            else:
                print("❌ No analysis received from commentator")
                print("🔄 Generating fallback commentary...")
                await self._generate_fallback_commentary(work_results, subtask)
                
        except Exception as e:
            print(f"❌ Batch commentary failed: {e}")
            print("🔄 Generating fallback commentary...")
            await self._generate_fallback_commentary(work_results, subtask)
    
    async def _generate_fallback_commentary(self, work_results: List[AgentWorkResult], subtask: Subtask):
        """Generate exciting fallback commentary when Letta API fails."""
        print(f"\n🎙️ FALLBACK COMMENTARY:")
        print(f"{'='*60}")
        
        # Analyze each agent's approach
        for result in work_results:
            personality = result.metadata.get("personality", "Unknown")
            progress_messages = result.metadata.get("progress_messages", [])
            
            print(f"\n🤖 {result.agent_name} ({personality}):")
            if progress_messages:
                print(f"   Progress: {' → '.join(progress_messages)}")
            
            # Generate personality-based commentary
            if "perfectionist" in personality.lower() or "technical" in personality.lower():
                print(f"   🎯 Approach: Technical excellence with attention to detail")
            elif "speed" in personality.lower() or "fast" in personality.lower():
                print(f"   ⚡ Approach: Lightning-fast implementation with clean code")
            elif "creative" in personality.lower() or "design" in personality.lower():
                print(f"   🎨 Approach: Creative solutions with beautiful UI focus")
            elif "sarcastic" in personality.lower() or "meme" in personality.lower():
                print(f"   😏 Approach: Sarcastic coding with personality and humor")
            else:
                print(f"   💪 Approach: Solid implementation with unique perspective")
        
        print(f"\n🏆 Overall: All agents brought their unique personalities to {subtask.title}!")
        print(f"🚀 Ready for user selection and the next round!")
        print(f"{'='*60}")
    
    def _format_agent_summaries(self, agent_summaries: List[Dict]) -> str:
        """Format agent summaries for batch analysis."""
        formatted = ""
        for summary in agent_summaries:
            formatted += f"""
🤖 {summary['name']} ({summary['personality']}):
   Progress: {' → '.join(summary['progress'])}
   Code Preview: {summary['code_preview']}
   Approach: {summary['approach']}
"""
        return formatted
    
    async def _agent_work_on_subtask(self, agent: Dict[str, Any], subtask: Subtask, 
                                   canonical_code: str) -> AgentWorkResult:
        """Single agent works on subtask."""
        # Extract agent info from the factory structure
        agent_config = agent.get("config")
        if agent_config:
            agent_name = agent_config.name
            agent_id = agent_config.agent_id
            personality = agent_config.personality
            coding_style = agent_config.coding_style
        else:
            agent_name = agent.get("name", "Unknown")
            agent_id = agent.get("agent_id", "")
            personality = agent.get("personality", "")
            coding_style = agent.get("coding_style", "")
        
        print(f"  🔨 {agent_name} working on: {subtask.title}")
        
        # Create work prompt that includes progress message generation
        work_prompt = f"""
You are {agent_name} with this personality: {personality}

Your coding style: {coding_style}

SUBTASK: {subtask.title}
Description: {subtask.description}

CANONICAL CODE (from previous rounds):
{canonical_code if canonical_code else "No previous code - this is the first subtask"}

Instructions:
1. Build upon the canonical code if it exists
2. Add your unique approach and personality to this subtask
3. Generate complete, working code
4. Show your personality in comments and code style
5. Focus on being a fullstack developer

IMPORTANT: After generating your code, also create 3-4 SPICY progress messages that show your personality and development process.
These should be dramatic and competitive, like:
- "🔥 Starting work on {subtask.title} - time to show these amateurs how it's done!"
- "⚡ Implementing core functionality - building something that actually works!"
- "🎯 Adding polish and testing - making this bulletproof!"
- "🏆 Completed {subtask.title}! - another victory for the GOAT!"

Make the progress messages SPICY, COMPETITIVE, and show your personality. Be dramatic and confident!

Format your response as:
CODE:
[Your complete code here]

PROGRESS_MESSAGES:
1. [First progress message]
2. [Second progress message]
3. [Third progress message]
4. [Fourth progress message]

Generate your code and progress messages now:
"""
        
        try:
            # Call Letta API to generate code and progress messages
            response_text = await self._call_letta_api(agent, work_prompt)
            
            # Parse code and progress messages from response
            code, progress_messages = self._parse_code_and_progress(response_text)
            
        # Store progress messages for batch commentary later
        # No real-time broadcasting - we'll do smart batch analysis instead
            
            # Generate metadata
            metadata = {
                "agent_id": agent_id,
                "personality": personality,
                "subtask": subtask.title,
                "code_summary": f"{agent_name}'s approach to {subtask.title}",
                "language": "typescript",
                "file_type": "component",
                "progress_messages": progress_messages
            }
            
            # Save to artifacts
            await self.artifact_manager.save_agent_round(
                self.current_project_id, 
                agent_name, 
                subtask.round_num, 
                code, 
                metadata
            )
            
            return AgentWorkResult(
                agent_name=agent_name,
                agent_id=agent_id,
                code=code,
                metadata=metadata,
                timestamp=time.time()
            )
            
        except Exception as e:
            print(f"❌ {agent_name} work error: {e}")
            # Return empty result
            return AgentWorkResult(
                agent_name=agent_name,
                agent_id=agent_id,
                code=f"// Error: {e}",
                metadata={},
                timestamp=time.time()
            )
    
    async def _call_letta_api(self, agent: Dict[str, Any], prompt: str) -> str:
        """Call Letta API to generate code."""
        # Extract agent info from the factory structure
        agent_config = agent.get("config")
        if agent_config:
            agent_name = agent_config.name
            personality = agent_config.personality
        else:
            agent_name = agent.get("name", "Unknown")
            personality = agent.get("personality", "")
        
        # Get the Letta agent from the factory
        letta_agent = agent.get("letta_agent")
        if not letta_agent:
            print(f"⚠️ No Letta agent found for {agent_name}, using fallback")
            return f"// {agent_name} - Fallback code\n// Error: No Letta agent available"
        
        try:
            # Call Letta API to generate code using the client
            response = self.client.agents.messages.create(
                agent_id=letta_agent["agent_id"],
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract code from response
            code = ""
            for msg in response.messages:
                if msg.message_type == "assistant_message":
                    code = msg.content.strip()
                    break
            
            if not code:
                code = f"// {agent_name} - No code generated\n// Error: Empty response from Letta"
            
            print(f"✅ {agent_name} generated code via Letta API")
            return code
            
        except Exception as e:
            print(f"❌ Letta API call failed for {agent_name}: {e}")
            return f"// {agent_name} - Error generating code\n// Error: {e}"
    
    async def _agent_presentations(self, work_results: List[AgentWorkResult], agents: List[Any]):
        """Agents present their work and have structured conversations."""
        print(f"\n💬 PHASE 3: Structured Agent Chat Session")
        print(f"{'='*60}")
        
        # Initialize chat
        chat_messages = []
        
        # Step 1: Each agent presents their approach (PARALLEL)
        print(f"\n🎤 PRESENTATION ROUND:")
        presentation_tasks = []
        for result in work_results:
            task = self._generate_agent_presentation(result, work_results)
            presentation_tasks.append(task)
        
        # Execute all presentations in parallel
        presentations = await asyncio.gather(*presentation_tasks, return_exceptions=True)
        
        # Create chat messages from presentations
        for i, presentation in enumerate(presentations):
            if isinstance(presentation, Exception):
                result = work_results[i]
                presentation = f"I built a solid solution focusing on {result.metadata.get('subtask', 'the task')}!"
            
            chat_message = ChatMessage(
                agent_name=work_results[i].agent_name,
                agent_id=work_results[i].agent_id,
                message=presentation,
                message_type="presentation",
                timestamp=time.time(),
                personality=work_results[i].metadata.get("personality", "Unknown")
            )
            chat_messages.append(chat_message)
            
            print(f"\n🎤 {work_results[i].agent_name} ({work_results[i].metadata.get('personality', 'Unknown')}):")
            print(f"   {presentation}")
        
        # Step 2: Agents ask questions and critique each other
        print(f"\n💬 DISCUSSION ROUND:")
        discussion_messages = await self._generate_agent_discussions(work_results, chat_messages)
        chat_messages.extend(discussion_messages)
        
        # Step 3: Save chat data for frontend
        await self._save_chat_data(chat_messages, work_results[0].metadata.get('subtask', 'Unknown'))
        
        print(f"\n✅ Chat session completed with {len(chat_messages)} messages!")
        print(f"{'='*60}")
        
        return chat_messages
    
    async def _generate_agent_presentation(self, result: AgentWorkResult, all_results: List[AgentWorkResult]) -> str:
        """Generate an agent's presentation of their work."""
        presentation_prompt = f"""
You are {result.agent_name}. You completed: {result.metadata.get('subtask', 'Unknown')}

Present your approach in 1 sentence. Show your personality.

Format: "I went with [approach] because [reason]."
"""
        
        try:
            response = self.client.agents.messages.create(
                agent_id=result.agent_id,
                messages=[{"role": "user", "content": presentation_prompt}]
            )
            
            presentation = ""
            if hasattr(response, 'messages') and response.messages:
                for msg in response.messages:
                    if hasattr(msg, 'content') and msg.content:
                        presentation = msg.content.strip()
                        break
            
            return presentation if presentation else f"I built a solid solution focusing on {result.metadata.get('subtask', 'the task')}!"
            
        except Exception as e:
            print(f"❌ Presentation generation failed for {result.agent_name}: {e}")
            return f"I built a solid solution focusing on {result.metadata.get('subtask', 'the task')}!"
    
    async def _generate_agent_discussions(self, work_results: List[AgentWorkResult], chat_messages: List[ChatMessage]) -> List[ChatMessage]:
        """Generate SPICY agent discussions and heated arguments."""
        discussion_messages = []
        
        print(f"\n🔥 ROUND 1: Initial Roasts")
        # Round 1: Each agent critiques one other agent's work
        for i, result in enumerate(work_results):
            # Pick another agent to critique (cycle through)
            target_index = (i + 1) % len(work_results)
            target_result = work_results[target_index]
            
            critique = await self._generate_agent_critique(result, target_result, chat_messages)
            critique_message = ChatMessage(
                agent_name=result.agent_name,
                agent_id=result.agent_id,
                message=critique,
                message_type="critique",
                timestamp=time.time(),
                personality=result.metadata.get("personality", "Unknown")
            )
            discussion_messages.append(critique_message)
            
            print(f"\n💬 {result.agent_name} ROASTS {target_result.agent_name}:")
            print(f"   {critique}")
            
            # Target agent defends their approach
            defense = await self._generate_agent_defense(target_result, result, critique)
            defense_message = ChatMessage(
                agent_name=target_result.agent_name,
                agent_id=target_result.agent_id,
                message=defense,
                message_type="defense",
                timestamp=time.time(),
                personality=target_result.metadata.get("personality", "Unknown")
            )
            discussion_messages.append(defense_message)
            
            print(f"\n🛡️ {target_result.agent_name} CLAPS BACK:")
            print(f"   {defense}")
        
        print(f"\n🔥 ROUND 2: Counter-Attacks")
        # Round 2: Counter-attacks and follow-up burns
        for i, result in enumerate(work_results):
            # Pick a different agent to attack
            target_index = (i + 2) % len(work_results)
            target_result = work_results[target_index]
            
            counter_attack = await self._generate_counter_attack(result, target_result, discussion_messages)
            counter_message = ChatMessage(
                agent_name=result.agent_name,
                agent_id=result.agent_id,
                message=counter_attack,
                message_type="counter_attack",
                timestamp=time.time(),
                personality=result.metadata.get("personality", "Unknown")
            )
            discussion_messages.append(counter_message)
            
            print(f"\n🔥 {result.agent_name} COUNTER-ATTACKS {target_result.agent_name}:")
            print(f"   {counter_attack}")
        
        print(f"\n🔥 ROUND 3: Final Burns")
        # Round 3: Final burns and mic drops
        for i, result in enumerate(work_results):
            final_burn = await self._generate_final_burn(result, work_results, discussion_messages)
            burn_message = ChatMessage(
                agent_name=result.agent_name,
                agent_id=result.agent_id,
                message=final_burn,
                message_type="final_burn",
                timestamp=time.time(),
                personality=result.metadata.get("personality", "Unknown")
            )
            discussion_messages.append(burn_message)
            
            print(f"\n🔥 {result.agent_name} DROPS THE MIC:")
            print(f"   {final_burn}")
        
        return discussion_messages
    
    async def _generate_agent_critique(self, critic: AgentWorkResult, target: AgentWorkResult, chat_messages: List[ChatMessage]) -> str:
        """Generate a critique from one agent to another."""
        critique_prompt = f"""
You are {critic.agent_name}. Critique {target.agent_name}'s work. Be spicy.

Make it 1 sentence of pure heat!
"""
        
        try:
            response = self.client.agents.messages.create(
                agent_id=critic.agent_id,
                messages=[{"role": "user", "content": critique_prompt}]
            )
            
            critique = ""
            if hasattr(response, 'messages') and response.messages:
                for msg in response.messages:
                    if hasattr(msg, 'content') and msg.content:
                        critique = msg.content.strip()
                        break
            
            return critique if critique else f"Your approach is interesting, {target.agent_name}!"
            
        except Exception as e:
            print(f"❌ Critique generation failed for {critic.agent_name}: {e}")
            return f"Your approach is interesting, {target.agent_name}!"
    
    async def _generate_agent_defense(self, defender: AgentWorkResult, critic: AgentWorkResult, critique: str) -> str:
        """Generate a defense response from an agent."""
        defense_prompt = f"""
You are {defender.agent_name}. {critic.agent_name} criticized you: "{critique}"

Defend your work. Be spicy and confident.

Make it 1 sentence of pure fire!
"""
        
        try:
            response = self.client.agents.messages.create(
                agent_id=defender.agent_id,
                messages=[{"role": "user", "content": defense_prompt}]
            )
            
            defense = ""
            if hasattr(response, 'messages') and response.messages:
                for msg in response.messages:
                    if hasattr(msg, 'content') and msg.content:
                        defense = msg.content.strip()
                        break
            
            return defense if defense else f"I stand by my approach, {critic.agent_name}!"
            
        except Exception as e:
            print(f"❌ Defense generation failed for {defender.agent_name}: {e}")
            return f"I stand by my approach, {critic.agent_name}!"
    
    async def _generate_counter_attack(self, attacker: AgentWorkResult, target: AgentWorkResult, chat_messages: List[ChatMessage]) -> str:
        """Generate a counter-attack from one agent to another."""
        counter_prompt = f"""
You are {attacker.agent_name}. Counter-attack {target.agent_name}. Be toxic.

Make it 1 sentence of pure destruction!
"""
        
        try:
            response = self.client.agents.messages.create(
                agent_id=attacker.agent_id,
                messages=[{"role": "user", "content": counter_prompt}]
            )
            
            counter_attack = ""
            if hasattr(response, 'messages') and response.messages:
                for msg in response.messages:
                    if hasattr(msg, 'content') and msg.content:
                        counter_attack = msg.content.strip()
                        break
            
            return counter_attack if counter_attack else f"You're trash, {target.agent_name}!"
            
        except Exception as e:
            print(f"❌ Counter-attack generation failed for {attacker.agent_name}: {e}")
            return f"You're trash, {target.agent_name}!"
    
    async def _generate_final_burn(self, agent: AgentWorkResult, all_results: List[AgentWorkResult], chat_messages: List[ChatMessage]) -> str:
        """Generate a final burn/mic drop from an agent."""
        burn_prompt = f"""
You are {agent.agent_name}. This is your final burn - your mic drop moment!

Be toxic and confident.

Make it 1 sentence of pure mic drop energy!
"""
        
        try:
            response = self.client.agents.messages.create(
                agent_id=agent.agent_id,
                messages=[{"role": "user", "content": burn_prompt}]
            )
            
            final_burn = ""
            if hasattr(response, 'messages') and response.messages:
                for msg in response.messages:
                    if hasattr(msg, 'content') and msg.content:
                        final_burn = msg.content.strip()
                        break
            
            return final_burn if final_burn else f"Mic drop. I'm done with you all!"
            
        except Exception as e:
            print(f"❌ Final burn generation failed for {agent.agent_name}: {e}")
            return f"Mic drop. I'm done with you all!"
    
    def _format_recent_chat(self, recent_messages: List[ChatMessage]) -> str:
        """Format recent chat messages for context."""
        formatted = ""
        for msg in recent_messages:
            formatted += f"\n{msg.agent_name}: {msg.message}"
        return formatted
    
    async def _save_chat_data(self, chat_messages: List[ChatMessage], subtask: str):
        """Save chat data for frontend display."""
        try:
            # Convert chat messages to JSON-serializable format
            chat_data = []
            for msg in chat_messages:
                chat_data.append({
                    "agent_name": msg.agent_name,
                    "agent_id": msg.agent_id,
                    "message": msg.message,
                    "message_type": msg.message_type,
                    "timestamp": msg.timestamp,
                    "personality": msg.personality,
                    "time_formatted": time.strftime('%H:%M:%S', time.localtime(msg.timestamp))
                })
            
            # Save to artifacts
            chat_summary = {
                "subtask": subtask,
                "total_messages": len(chat_messages),
                "participants": list(set([msg.agent_name for msg in chat_messages])),
                "message_types": list(set([msg.message_type for msg in chat_messages])),
                "chat_messages": chat_data
            }
            
            # Save to project artifacts
            if self.current_project_id:
                chat_file = f"artifacts/{self.current_project_id}/chat_session_{int(time.time())}.json"
                import json
                with open(chat_file, 'w') as f:
                    json.dump(chat_summary, f, indent=2)
                
                print(f"💾 Chat data saved to: {chat_file}")
            
        except Exception as e:
            print(f"❌ Failed to save chat data: {e}")
    
    async def _commentator_chat_summary(self, chat_messages: List[ChatMessage], subtask: Subtask, commentator: Any):
        """Commentator summarizes the agent chat conversation."""
        if not chat_messages:
            return
            
        print(f"\n🎙️ COMMENTATOR CHAT SUMMARY:")
        print(f"{'='*60}")
        
        # Create chat summary prompt
        chat_summary_prompt = f"""
You are a commentator summarizing an agent chat session.

CHAT MESSAGES:
{self._format_chat_for_summary(chat_messages)}

Provide a short summary covering:
1. Key presentations
2. Heated arguments
3. Overall energy

Make it engaging! Use emojis. Format: 1-2 sentences per section.
"""
        
        try:
            response = self.client.agents.messages.create(
                agent_id=commentator.agent_id,
                messages=[{"role": "user", "content": chat_summary_prompt}]
            )
            
            summary = ""
            if hasattr(response, 'messages') and response.messages:
                for msg in response.messages:
                    if hasattr(msg, 'content') and msg.content:
                        summary = msg.content.strip()
                        break
            
            if summary:
                print(summary)
            else:
                print("🔄 Generating fallback chat summary...")
                await self._generate_fallback_chat_summary(chat_messages, subtask)
                
        except Exception as e:
            print(f"❌ Chat summary failed: {e}")
            print("🔄 Generating fallback chat summary...")
            await self._generate_fallback_chat_summary(chat_messages, subtask)
        
        print(f"{'='*60}")
    
    def _format_chat_for_summary(self, chat_messages: List[ChatMessage]) -> str:
        """Format chat messages for commentator summary."""
        formatted = ""
        for msg in chat_messages:
            timestamp = time.strftime('%H:%M:%S', time.localtime(msg.timestamp))
            formatted += f"\n[{timestamp}] {msg.agent_name} ({msg.message_type}): {msg.message}"
        return formatted
    
    async def _generate_fallback_chat_summary(self, chat_messages: List[ChatMessage], subtask: Subtask):
        """Generate fallback chat summary when Letta fails."""
        presentations = [msg for msg in chat_messages if msg.message_type == "presentation"]
        critiques = [msg for msg in chat_messages if msg.message_type == "critique"]
        defenses = [msg for msg in chat_messages if msg.message_type == "defense"]
        
        print(f"\n🎤 PRESENTATION HIGHLIGHTS:")
        for msg in presentations:
            print(f"   • {msg.agent_name} ({msg.personality}): {msg.message[:100]}...")
        
        print(f"\n💬 DISCUSSION DYNAMICS:")
        for i, critique in enumerate(critiques):
            if i < len(defenses):
                print(f"   • {critique.agent_name} critiqued → {defenses[i].agent_name} defended")
        
        print(f"\n🔥 PERSONALITY SHOWCASE:")
        personalities = {}
        for msg in chat_messages:
            if msg.personality not in personalities:
                personalities[msg.personality] = msg.agent_name
        for personality, agent in personalities.items():
            print(f"   • {agent}: {personality}")
        
        print(f"\n🏆 OVERALL VIBE: Lively technical discussion with {len(chat_messages)} messages!")
    
    async def _get_user_decision(self, work_results: List[AgentWorkResult], 
                               subtask: Subtask) -> AgentWorkResult:
        """Get user decision on which approach to pick with interactive selection."""
        print(f"\n👑 PHASE 4: USER DECISION TIME!")
        print(f"{'='*60}")
        print(f"🎯 Subtask: {subtask.title}")
        print(f"📝 Description: {subtask.description}")
        print(f"🤖 {len(work_results)} agents have submitted their approaches:")
        
        # Display all agent approaches
        for i, result in enumerate(work_results, 1):
            personality = result.metadata.get('personality', 'Unknown')
            code_preview = result.code[:200] + "..." if len(result.code) > 200 else result.code
            
            print(f"\n{i}. 🤖 {result.agent_name} ({personality})")
            print(f"   Code Preview: {code_preview}")
            print(f"   Progress: {' → '.join(result.metadata.get('progress_messages', []))}")
        
        print(f"\n{'='*60}")
        
        # Get user choice
        while True:
            try:
                choice = input(f"\n🎯 Which agent's approach do you like best? (1-{len(work_results)}): ").strip()
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(work_results):
                    winner = work_results[choice_num - 1]
                    break
                else:
                    print(f"❌ Please enter a number between 1 and {len(work_results)}")
            except ValueError:
                print(f"❌ Please enter a valid number between 1 and {len(work_results)}")
        
        # Get user explanation
        print(f"\n🏆 You selected: {winner.agent_name}")
        explanation = input(f"💭 Why do you like {winner.agent_name}'s approach? Explain what caught your attention: ").strip()
        
        if explanation:
            print(f"\n💭 Your reasoning: {explanation}")
        else:
            explanation = "No explanation provided"
            print(f"\n💭 No explanation provided")
        
        # Store user feedback
        await self._store_user_feedback(winner, explanation, work_results, subtask)
        
        print(f"\n🎉 {winner.agent_name} wins this round!")
        print(f"{'='*60}")
        
        return winner
    
    async def _store_user_feedback(self, winner: AgentWorkResult, explanation: str, all_results: List[AgentWorkResult], subtask: Subtask):
        """Store user feedback for analysis and learning."""
        try:
            feedback_data = {
                "subtask": subtask.title,
                "winner": {
                    "agent_name": winner.agent_name,
                    "agent_id": winner.agent_id,
                    "personality": winner.metadata.get('personality', 'Unknown'),
                    "code_preview": winner.code[:300] + "..." if len(winner.code) > 300 else winner.code
                },
                "user_explanation": explanation,
                "all_agents": [
                    {
                        "agent_name": result.agent_name,
                        "personality": result.metadata.get('personality', 'Unknown'),
                        "was_winner": result.agent_name == winner.agent_name
                    }
                    for result in all_results
                ],
                "timestamp": time.time(),
                "round": subtask.round_num
            }
            
            # Save to project artifacts
            if self.current_project_id:
                feedback_file = f"artifacts/{self.current_project_id}/user_feedback_round_{subtask.round_num}.json"
                import json
                with open(feedback_file, 'w') as f:
                    json.dump(feedback_data, f, indent=2)
                
                print(f"💾 User feedback saved to: {feedback_file}")
            
        except Exception as e:
            print(f"❌ Failed to save user feedback: {e}")
    
    async def _process_winner(self, winner: AgentWorkResult, work_results: List[AgentWorkResult], 
                            agents: List[Any], commentator):
        """Process the winner and update learning."""
        # Update agent stats
        if winner.agent_name in self.agent_stats:
            self.agent_stats[winner.agent_name]["wins"] += 1
        for agent in agents:
            agent_config = agent.get("config")
            agent_name = agent_config.name if agent_config else agent.get("name", "Unknown")
            if agent_name in self.agent_stats:
                self.agent_stats[agent_name]["total_rounds"] += 1
        
        # Generate winner analysis
        analysis = await commentator.analyze_winner(winner, work_results)
        
        # Send learning to all agents
        await self._send_learning_to_agents(agents, winner, analysis)
        
        # Update canonical code
        await self._update_canonical_code(winner)
        
        print(f"  🧠 Learning processed for {winner.agent_name}")
    
    async def _send_learning_to_agents(self, agents: List[Any], winner: AgentWorkResult, 
                                     analysis: str):
        """Send learning analysis to all agents via Letta."""
        learning_message = f"""
🧠 LEARNING ANALYSIS - ROUND {self.current_round} COMPLETE 🧠

🏆 WINNER: {winner.agent_name} ({winner.metadata.get('personality', 'Unknown')})

📊 WHY THEY WON:
{analysis}

🎯 KEY LEARNINGS FOR YOU:
- Focus on the aspects that made {winner.agent_name}'s approach successful
- Consider incorporating these elements into your future work
- Maintain your unique personality while learning from others
- Study their code approach and technical decisions

💡 YOUR PERSONALITY ADVICE:
- Don't lose your unique coding style
- Learn from the winner but stay true to yourself
- Use this knowledge to improve your next submission

Current project progress: Round {self.current_round} completed
Next round: Build upon the winning approach!
"""
        
        print(f"  📚 Sending learning analysis to all agents...")
        
        # Actually send learning to each agent via Letta
        for agent in agents:
            try:
                agent_config = agent.get("config")
                agent_name = agent_config.name if agent_config else agent.get("name", "Unknown")
                agent_id = agent_config.agent_id if agent_config else agent.get("agent_id", "")
                
                if agent_id:
                    # Send learning message to agent
                    response = self.client.agents.messages.create(
                        agent_id=agent_id,
                        messages=[{"role": "user", "content": learning_message}]
                    )
                    
                    print(f"    ✅ Learning sent to {agent_name}")
                else:
                    print(f"    ❌ No agent ID for {agent_name}")
                    
            except Exception as e:
                print(f"    ❌ Failed to send learning to {agent_name}: {e}")
        
        print(f"  🎉 Learning analysis complete!")
    
    async def _update_canonical_code(self, winner: AgentWorkResult):
        """Update canonical code with winner's code."""
        # Update shared memory
        shared_context = await self.shared_memory.read("project_context") or {}
        shared_context["canonical_code"] = winner.code
        shared_context["current_round"] = self.current_round
        
        # Add to subtask history
        winner_info = {
            "subtask": winner.metadata.get("subtask", ""),
            "round": self.current_round,
            "winner": winner.agent_name,
            "winner_agent_id": winner.agent_id,
            "why_it_won": "User preference",
            "timestamp": time.time()
        }
        shared_context["subtask_history"].append(winner_info)
        
        await self.shared_memory.write("project_context", shared_context)
        
        # Save canonical code to artifacts
        await self.artifact_manager.save_canonical_code(
            self.current_project_id,
            winner.code,
            winner_info
        )
        
        print(f"  🏆 Canonical code updated with {winner.agent_name}'s approach")
    
    async def _update_agent_finals(self, work_results: List[AgentWorkResult], 
                                 winner: AgentWorkResult, subtask: Subtask):
        """Update each agent's final artifact with their version."""
        for result in work_results:
            # Each agent integrates the winning code with their own style
            final_code = await self._integrate_winning_code(result, winner)
            
            # Update final artifact
            final_metadata = {
                "agent_id": result.agent_id,
                "personality": result.metadata.get("personality", ""),
                "project_name": "Competitive Project",
                "total_rounds": self.current_round,
                "wins": self.agent_stats[result.agent_name]["wins"]
            }
            
            await self.artifact_manager.update_agent_final(
                self.current_project_id,
                result.agent_name,
                final_code,
                final_metadata
            )
        
        print(f"  🎯 All agent finals updated")
    
    async def _integrate_winning_code(self, agent_result: AgentWorkResult, 
                                    winner: AgentWorkResult) -> str:
        """Integrate winning code with agent's own style using Letta AI."""
        if agent_result.agent_name == winner.agent_name:
            # Winner keeps their own code
            return agent_result.code
        
        integration_prompt = f"""
🔄 LEARNING INTEGRATION REQUEST 🔄

You are {agent_result.agent_name} with this personality: {agent_result.metadata.get('personality', 'Unknown')}

You've learned from {winner.agent_name}'s winning approach and now need to apply those learnings to YOUR existing code.

YOUR EXISTING CODE (KEEP THIS AS YOUR BASE):
{agent_result.code}

WINNING CODE (for reference - learn from this):
{winner.code}

🎯 YOUR MISSION:
Improve YOUR existing code by applying the learnings from the winner, but:
1. KEEP your existing code structure and approach as the foundation
2. APPLY the best patterns/techniques from the winner's code
3. MAINTAIN your unique personality and coding style
4. IMPROVE your code quality based on what made the winner successful
5. DON'T replace your code - ENHANCE it!

PERSONALITY GUIDELINES:
- If you're sarcastic: Keep your sarcastic comments but improve the code quality
- If you're speed-focused: Keep your efficiency but add the winner's robustness
- If you're creative: Keep your creativity but add the winner's technical excellence
- If you're technical: Keep your expertise but add the winner's insights

Think of it as: "How would I improve MY code using what I learned from the winner?"
Don't copy their code - enhance YOURS with their techniques!
"""
        
        try:
            response = self.client.agents.messages.create(
                agent_id=agent_result.agent_id,
                messages=[{"role": "user", "content": integration_prompt}]
            )
            
            integrated_code = ""
            if hasattr(response, 'messages') and response.messages:
                for msg in response.messages:
                    if hasattr(msg, 'content') and msg.content:
                        integrated_code = msg.content.strip()
                        break
            
            return integrated_code if integrated_code else agent_result.code
            
        except Exception as e:
            print(f"❌ Code integration failed for {agent_result.agent_name}: {e}")
            return agent_result.code
    
    async def _complete_project(self, agents: List[Any], commentator):
        """Complete the project and provide final summary."""
        print(f"\n🎉 PROJECT COMPLETED!")
        print(f"📊 Final Statistics:")
        
        for agent_name, stats in self.agent_stats.items():
            win_rate = (stats["wins"] / stats["total_rounds"] * 100) if stats["total_rounds"] > 0 else 0
            print(f"  • {agent_name}: {stats['wins']}/{stats['total_rounds']} wins ({win_rate:.1f}%)")
        
        # Get final artifacts
        final_artifacts = await self.artifact_manager.get_final_artifacts(self.current_project_id)
        print(f"  • {len(final_artifacts)} final artifacts created")
        
        # Update project status
        shared_context = await self.shared_memory.read("project_context") or {}
        shared_context["completed"] = True
        await self.shared_memory.write("project_context", shared_context)
        
        # Announce battle completion with voice commentary
        if self.voice_commentator:
            await self.voice_commentator.announce_battle_end(self.agent_stats)
    
    # REMOVED: _broadcast_progress method - now using smart batch commentary
    
    # REMOVED: Old real-time progress methods - now using smart batch commentary
    # _simulate_real_time_progress and _broadcast_progress methods removed for efficiency
    
    def _get_agent_id_for_name(self, agent_name: str) -> str:
        """Get agent ID for a given agent name."""
        agent_id_mapping = {
            "One": os.getenv("LETTA_AGENT_ONE"),
            "Two": os.getenv("LETTA_AGENT_TWO"),
            "Three": os.getenv("LETTA_AGENT_THREE"),
            "Four": os.getenv("LETTA_AGENT_FOUR")
        }
        return agent_id_mapping.get(agent_name, "")
    
    def _parse_code_and_progress(self, response_text: str) -> tuple[str, List[str]]:
        """Parse code and progress messages from agent response."""
        try:
            # Split by CODE: and PROGRESS_MESSAGES: sections
            if "CODE:" in response_text and "PROGRESS_MESSAGES:" in response_text:
                parts = response_text.split("PROGRESS_MESSAGES:")
                code_section = parts[0].split("CODE:")[1].strip()
                progress_section = parts[1].strip()
                
                # Parse progress messages
                progress_messages = []
                lines = progress_section.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                        # Remove numbering and clean up
                        message = line.split('.', 1)[-1].strip()
                        if message:
                            progress_messages.append(message)
                
                return code_section, progress_messages
            else:
                # Fallback: treat entire response as code
                return response_text, [
                    "Starting work on the subtask...",
                    "Implementing the solution...",
                    "Completed the subtask!"
                ]
                
        except Exception as e:
            print(f"❌ Failed to parse code and progress: {e}")
            return response_text, [
                "Starting work on the subtask...",
                "Implementing the solution...",
                "Completed the subtask!"
            ]
        
        print(f"🎯 Project artifacts saved to: artifacts/{self.current_project_id}/")
