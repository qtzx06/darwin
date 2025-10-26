#!/usr/bin/env python3
"""
Real Flask server that makes actual Letta API calls
"""

import sys
import os
import json
import time
from dotenv import load_dotenv

# Load .env from parent directory (root of project)
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

from flask import Flask, request, jsonify
from flask_cors import CORS

# Add current directory to path
sys.path.append('.')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Add parent directory to path for chat imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

try:
    from api_wrapper import CompetitiveAPI
    from src.core.agent_factory import AgentFactory
    from letta_client import Letta
    # LiveKit imports
    from src.livekit.room_manager import room_manager
    from src.livekit.voice_commentator import VoiceCommentator
    from src.livekit.battle_context import BattleContextManager
    LETTA_AVAILABLE = True
    LIVEKIT_AVAILABLE = room_manager.is_available()
except ImportError as e:
    print(f"⚠️ Warning: letta_client not available: {e}")
    print("   Using simulated mode instead")
    LETTA_AVAILABLE = False
    LIVEKIT_AVAILABLE = False

# Import Claude chat simulator
try:
    from chat.chat_manager import ClaudeManager
    from chat.chat_config import get_system_prompt
    CLAUDE_CHAT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Warning: Claude chat simulator not available: {e}")
    CLAUDE_CHAT_AVAILABLE = False

# Mock classes for simulated mode
if not LETTA_AVAILABLE:
    class MockLetta:
        def __init__(self, token=None): pass
        class Agents:
            def list(self): return []
            class messages:
                def create(self, agent_id, messages): return {}
                def create_stream(self, agent_id, messages, stream_tokens): return []
    class MockAgentFactory:
        def __init__(self, client): pass
        async def create_fresh_agents(self, project_id):
            return [
                {"name": "One", "personality": "Sarcastic, funny, loves memes"},
                {"name": "Two", "personality": "Technical perfectionist, over-engineers everything"},
                {"name": "Three", "personality": "Fast-paced, performance-focused"},
                {"name": "Four", "personality": "Creative, design-focused, user-centric"}
            ]
    class MockCompetitiveAPI:
        def __init__(self): pass
        async def get_agents_info(self):
            return {
                "success": True,
                "message": "Retrieved 4 agents",
                "agents": [
                    {"name": "One", "personality": "Sarcastic, funny, loves memes, writes clean code with personality", "strengths": ["React", "TypeScript", "Humor", "Clean code"]},
                    {"name": "Two", "personality": "Technical perfectionist, loves documentation, over-engineers everything", "strengths": ["Architecture", "Documentation", "Testing", "Best practices"]},
                    {"name": "Three", "personality": "Fast-paced, aggressive, loves performance, ships quickly", "strengths": ["Performance", "Speed", "Optimization", "Delivery"]},
                    {"name": "Four", "personality": "Creative, design-focused, loves beautiful UI, user-centric", "strengths": ["UI/UX", "Design", "Accessibility", "User experience"]}
                ]
            }
        async def get_results(self, project_id, agent_names):
            work_results = []
            for agent_name in agent_names:
                work_results.append({
                    "agent_name": agent_name,
                    "code": f"import React from 'react';\n\nconst Component = () => {{\n  return <div>Test component</div>;\n}};\n\nexport default Component;",
                    "personality": f"{agent_name} is a test agent",
                    "summary": f"{agent_name} delivered a solid implementation"
                })
            return {
                "success": True,
                "project_id": project_id,
                "agents": work_results,
                "message": "Retrieved results from 4 agents",
                "phase": "results"
            }
    CompetitiveAPI = MockCompetitiveAPI

app = Flask(__name__)
CORS(app)

api_instance = CompetitiveAPI()

# Initialize Claude chat manager for frontend chat
claude_chat_manager = None
if CLAUDE_CHAT_AVAILABLE:
    try:
        claude_chat_manager = ClaudeManager(system_prompt=get_system_prompt())
        print("✅ Claude chat manager initialized")
    except Exception as e:
        print(f"⚠️ Failed to initialize Claude chat manager: {e}")
        CLAUDE_CHAT_AVAILABLE = False

# Global transcript storage for voice commentary
room_transcripts = {}
room_modes = {}  # Track current mode per room (commentary/agent)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "Competitive AI Agents API is running",
        "version": "1.0.0",
        "letta_available": LETTA_AVAILABLE,
        "endpoints": [
            "GET /api/health",
            "POST /api/get-results",
            "GET /api/agents",
            "POST /api/create-agents"
        ]
    })

@app.route('/api/get-results', methods=['POST'])
def get_agent_results():
    data = request.get_json()
    project_id = data.get('project_id')
    agent_names = data.get('agent_names')
    
    if not project_id or not agent_names:
        return jsonify({"success": False, "error": "Missing project_id or agent_names"}), 400
    
    # Run async function synchronously
    import asyncio
    results = asyncio.run(api_instance.get_results(project_id, agent_names))
    return jsonify(results), 200

@app.route('/api/agents', methods=['GET'])
def get_agents_info():
    # Run async function synchronously
    import asyncio
    agents_info = asyncio.run(api_instance.get_agents_info())
    return jsonify(agents_info), 200

@app.route('/api/create-agents', methods=['POST'])
def create_agents_endpoint():
    data = request.get_json()
    project_id = data.get('project_id', f"project_{int(time.time())}")
    
    # Use our fast simulated create_agents method instead of real Letta
    import asyncio
    result = asyncio.run(api_instance.create_agents(project_id))
    return jsonify(result), 200

@app.route('/api/submit-project', methods=['POST'])
def submit_project():
    data = request.get_json()
    project_description = data.get('project_description')
    
    if not project_description:
        return jsonify({"success": False, "error": "Missing project_description"}), 400
    
    # Run async function synchronously
    import asyncio
    result = asyncio.run(api_instance.submit_project(project_description))
    return jsonify(result), 200

@app.route('/api/start-work', methods=['POST'])
def start_work():
    data = request.get_json()
    project_id = data.get('project_id')
    subtask_id = data.get('subtask_id')
    
    if not project_id or not subtask_id:
        return jsonify({"success": False, "error": "Missing project_id or subtask_id"}), 400
    
    # Run async function synchronously
    import asyncio
    result = asyncio.run(api_instance.start_work(project_id, subtask_id))
    return jsonify(result), 200

@app.route('/api/progress-messages', methods=['GET'])
def get_progress_messages():
    project_id = request.args.get('project_id')
    
    if not project_id:
        return jsonify({"success": False, "error": "Missing project_id"}), 400
    
    # Run async function synchronously
    import asyncio
    result = asyncio.run(api_instance.get_progress_messages(project_id))
    return jsonify(result), 200

@app.route('/api/select-winner', methods=['POST'])
def select_winner():
    data = request.get_json()
    project_id = data.get('project_id')
    winner = data.get('winner')
    reason = data.get('reason')
    
    if not project_id or not winner or not reason:
        return jsonify({"success": False, "error": "Missing project_id, winner, or reason"}), 400
    
    # Run async function synchronously
    import asyncio
    result = asyncio.run(api_instance.select_winner(project_id, winner, reason))
    return jsonify(result), 200

@app.route('/api/complete-round', methods=['POST'])
def complete_round():
    data = request.get_json()
    project_id = data.get('project_id')
    winner = data.get('winner')
    winner_code = data.get('winner_code')
    subtask_id = data.get('subtask_id')

    if not project_id or not winner or not winner_code or not subtask_id:
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    # Convert subtask_id to int
    try:
        subtask_id = int(subtask_id)
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "subtask_id must be a valid integer"}), 400

    # Run async function synchronously
    import asyncio
    result = asyncio.run(api_instance.complete_round(project_id, winner, winner_code, subtask_id))
    return jsonify(result), 200

@app.route('/api/agent-stats', methods=['GET'])
def get_agent_stats():
    project_id = request.args.get('project_id')
    
    if not project_id:
        return jsonify({"success": False, "error": "Missing project_id"}), 400
    
    # Run async function synchronously
    import asyncio
    result = asyncio.run(api_instance.get_agent_stats(project_id))
    return jsonify(result), 200

@app.route('/api/project-status', methods=['GET'])
def get_project_status():
    project_id = request.args.get('project_id')
    
    if not project_id:
        return jsonify({"success": False, "error": "Missing project_id"}), 400
    
    # Run async function synchronously
    import asyncio
    result = asyncio.run(api_instance.get_project_status(project_id))
    return jsonify(result), 200

@app.route('/api/retrieve-code', methods=['POST'])
def retrieve_agent_code():
    data = request.get_json()
    project_id = data.get('project_id')
    agent_name = data.get('agent_name')
    
    if not project_id or not agent_name:
        return jsonify({"success": False, "error": "Missing project_id or agent_name"}), 400
    
    # Run async function synchronously
    import asyncio
    result = asyncio.run(api_instance.retrieve_agent_code(project_id, agent_name))
    return jsonify(result), 200

@app.route('/api/get-messages', methods=['POST'])
def get_agent_messages():
    data = request.get_json()
    project_id = data.get('project_id')
    agent_name = data.get('agent_name')
    
    if not project_id or not agent_name:
        return jsonify({"success": False, "error": "Missing project_id or agent_name"}), 400
    
    # Run async function synchronously
    import asyncio
    result = asyncio.run(api_instance.get_agent_messages(project_id, agent_name))
    return jsonify(result), 200

@app.route('/api/get-commentary', methods=['POST'])
def get_commentary():
    data = request.get_json()
    project_id = data.get('project_id')
    subtask_id = data.get('subtask_id', '1')
    
    if not project_id:
        return jsonify({"success": False, "error": "Missing project_id"}), 400
    
    # Run async function synchronously
    import asyncio
    result = asyncio.run(api_instance.get_commentary(project_id, subtask_id))
    return jsonify(result), 200

@app.route('/api/get-chat-summary', methods=['POST'])
def get_chat_summary():
    data = request.get_json()
    project_id = data.get('project_id')
    subtask_id = data.get('subtask_id', '1')
    
    if not project_id:
        return jsonify({"success": False, "error": "Missing project_id"}), 400
    
    # Run async function synchronously
    import asyncio
    result = asyncio.run(api_instance.get_chat_summary(project_id, subtask_id))
    return jsonify(result), 200

@app.route('/api/orchestrate-project', methods=['POST'])
def orchestrate_project():
    data = request.get_json()
    project_description = data.get('project_description')
    
    if not project_description:
        return jsonify({"success": False, "error": "Missing project_description"}), 400
    
    # Run async function synchronously
    import asyncio
    result = asyncio.run(api_instance.orchestrate_project(project_description))
    
    # Add detailed logging
    print(f"\n📦 Orchestration result type: {type(result)}")
    print(f"📦 Orchestration result: {result}")
    if isinstance(result, dict):
        print(f"📦 Result keys: {result.keys()}")
        if 'subtasks' in result:
            print(f"📦 Subtasks count: {len(result['subtasks'])}")
            print(f"📦 Subtasks: {result['subtasks']}")
    
    return jsonify(result), 200

# LiveKit Voice Commentary Endpoints

@app.route('/api/livekit/create-battle-room', methods=['POST'])
def create_battle_room():
    """Create a LiveKit room for voice commentary battle"""
    if not LIVEKIT_AVAILABLE:
        return jsonify({
            "success": False,
            "error": "LiveKit not configured",
            "message": "Please configure LiveKit credentials in .env file"
        }), 400
    
    data = request.get_json()
    project_id = data.get('project_id')
    
    if not project_id:
        return jsonify({"success": False, "error": "Missing project_id"}), 400
    
    # Create LiveKit room
    import asyncio
    result = asyncio.run(room_manager.create_battle_room(project_id))
    return jsonify(result), 200

@app.route('/api/livekit/join-room', methods=['POST'])
def join_room():
    """Generate spectator token to join LiveKit room"""
    if not LIVEKIT_AVAILABLE:
        return jsonify({
            "success": False,
            "error": "LiveKit not configured"
        }), 400
    
    data = request.get_json()
    room_name = data.get('room_name')
    user_name = data.get('user_name', 'Spectator')
    
    if not room_name:
        return jsonify({"success": False, "error": "Missing room_name"}), 400
    
    # Generate spectator token
    import asyncio
    result = asyncio.run(room_manager.generate_spectator_token(room_name, user_name))
    return jsonify(result), 200

@app.route('/api/livekit/ask-commentator', methods=['POST'])
def ask_commentator():
    """Ask commentator a question via voice"""
    if not LIVEKIT_AVAILABLE:
        return jsonify({
            "success": False,
            "error": "LiveKit not configured"
        }), 400
    
    data = request.get_json()
    room_name = data.get('room_name')
    question = data.get('question')
    
    if not room_name or not question:
        return jsonify({"success": False, "error": "Missing room_name or question"}), 400
    
    # Store user question in transcript
    if room_name not in room_transcripts:
        room_transcripts[room_name] = []
    
    # Add user question
    room_transcripts[room_name].append({
        "speaker": "User",
        "text": question,
        "timestamp": time.time(),
        "time_formatted": time.strftime('%H:%M:%S', time.localtime())
    })
    
    # Generate commentator response using Letta
    try:
        if LETTA_AVAILABLE:
            # Get current battle context
            battle_context = {
                "room_name": room_name,
                "current_time": time.strftime('%H:%M:%S', time.localtime()),
                "user_question": question,
                "recent_events": room_transcripts[room_name][-5:] if len(room_transcripts[room_name]) > 5 else room_transcripts[room_name]
            }
            
            # Create commentator prompt
            commentator_prompt = f"""
You are a fast-paced esports commentator for an AI coding battle arena. A spectator asked: "{question}"

Context: Room {room_name}, {len(battle_context['recent_events'])} messages logged.

Give a SHORT, EXCITING response (1 sentence max). Be dramatic and fast-paced like a real esports commentator. Use emojis and energy!
"""
            
            # Call Letta commentator agent
            from src.agents.commentator_agent import CommentatorAgent
            from config.agents_config import LettaConfig
            import os
            
            # Get Letta client and commentator agent ID
            letta_config = LettaConfig()
            client = letta_config.client
            commentator_agent_id = os.getenv('LETTA_AGENT_COMMENTATOR')
            
            if commentator_agent_id:
                # Create commentator agent
                commentator_agent = CommentatorAgent(client, commentator_agent_id, None)
                
                # Send message to commentator
                response = client.agents.messages.create(
                    agent_id=commentator_agent_id,
                    messages=[{"role": "user", "content": commentator_prompt}]
                )
                
                # Extract response content
                response_text = "Great question! The battle is heating up!"
                for msg in response.messages:
                    if hasattr(msg, 'content'):
                        response_text = msg.content.strip()
                        break
            else:
                # Fallback if no commentator agent ID
                response_text = f"Great question! The battle is heating up in {room_name}! Let me tell you what's happening..."
            
        else:
            # Fallback if Letta not available
            response_text = f"Great question! The battle is heating up in {room_name}! Let me tell you what's happening..."
            
    except Exception as e:
        print(f"❌ Commentator error: {e}")
        # Fallback response
        response_text = f"Great question! The battle is heating up in {room_name}! Let me tell you what's happening..."
    
    # Add commentator response
    room_transcripts[room_name].append({
        "speaker": "Commentator", 
        "text": response_text,
        "timestamp": time.time(),
        "time_formatted": time.strftime('%H:%M:%S', time.localtime())
    })
    
    return jsonify({
        "success": True,
        "response_text": response_text,
        "message": "Question processed (voice response streams via LiveKit)"
    }), 200

@app.route('/api/livekit/get-transcript', methods=['GET'])
def get_transcript():
    """Get live transcript for a room"""
    room_name = request.args.get('room_name')
    
    if not room_name:
        return jsonify({"success": False, "error": "Missing room_name"}), 400
    
    # Get transcript for this room
    transcript = room_transcripts.get(room_name, [])
    
    # If no transcript exists, add a welcome message
    if not transcript:
        transcript = [{
            "speaker": "System",
            "text": f"Welcome to room {room_name}! Ask the commentator anything about the battle.",
            "timestamp": time.time(),
            "time_formatted": time.strftime('%H:%M:%S', time.localtime())
        }]
        room_transcripts[room_name] = transcript
    
    return jsonify({
        "success": True,
        "transcript": transcript,
        "room_name": room_name
    }), 200

@app.route('/api/livekit/room-status', methods=['GET'])
def get_room_status():
    """Get current room status and participant info"""
    if not LIVEKIT_AVAILABLE:
        return jsonify({
            "success": False,
            "error": "LiveKit not configured"
        }), 400
    
    room_name = request.args.get('room_name')
    
    if not room_name:
        return jsonify({"success": False, "error": "Missing room_name"}), 400
    
    # Get room status
    import asyncio
    result = asyncio.run(room_manager.get_room_status(room_name))
    return jsonify(result), 200

@app.route('/api/livekit/speak-text', methods=['POST'])
def speak_text():
    """Convert text to speech using ElevenLabs"""
    import os
    import requests
    
    data = request.get_json()
    text = data.get('text')
    voice_id = data.get('voice_id', 'cgSgspJ2msm6clMCkdW9')
    
    if not text:
        return jsonify({"success": False, "error": "Missing text"}), 400
    
    try:
        # Get ElevenLabs API key
        api_key = os.getenv('ELEVENLABS_API_KEY') or "sk_aa058a975d42a503246daf589cf30d04d4de1e26518acb22"
        print(f"🔑 API Key loaded: {api_key[:20] + '...' if api_key else 'NOT FOUND'}")
        if not api_key:
            return jsonify({"success": False, "error": "ElevenLabs API key not found"}), 400
        
        # Extract just the voice ID part
        if ":" in voice_id:
            voice_id = voice_id.split(":")[1]
        elif "/" in voice_id:
            voice_id = voice_id.split("/")[-1]
        
        # ElevenLabs API endpoint
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_turbo_v2_5",
            "voice_settings": {
                "stability": 0.3,
                "similarity_boost": 0.7,
                "style": 0.8,
                "use_speaker_boost": True
            }
        }
        
        # Make request to ElevenLabs
        print(f"🌐 Making request to: {url}")
        print(f"📝 Request data: {data}")
        print(f"🔑 Using API key: {api_key[:20]}...")
        
        response = requests.post(url, json=data, headers=headers)
        
        print(f"📊 Response status: {response.status_code}")
        print(f"📄 Response text: {response.text[:200]}...")
        
        if response.status_code == 200:
            return response.content, 200, {
                'Content-Type': 'audio/mpeg',
                'Content-Disposition': 'inline; filename="commentator_response.mp3"'
            }
        else:
            print(f"❌ ElevenLabs API error: {response.status_code} - {response.text}")
            return jsonify({"success": False, "error": f"ElevenLabs API error: {response.status_code}"}), 500
            
    except Exception as e:
        print(f"❌ TTS error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/livekit/set-mode', methods=['POST'])
def set_mode():
    """Set the current voice mode for a room (commentary/agent)."""
    try:
        data = request.get_json()
        room_name = data.get('room_name')
        mode = data.get('mode')
        
        if not room_name or not mode:
            return jsonify({"success": False, "error": "Missing room_name or mode"}), 400
        
        if mode not in ['commentary', 'agent']:
            return jsonify({"success": False, "error": "Mode must be 'commentary' or 'agent'"}), 400
        
        # Store mode for the room
        room_modes[room_name] = mode
        
        return jsonify({
            "success": True,
            "mode": mode,
            "message": f"Room {room_name} set to {mode} mode"
        }), 200
        
    except Exception as e:
        print(f"❌ Set mode error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/livekit/ask-agent', methods=['POST'])
def ask_agent():
    """User asks a specific agent a question."""
    try:
        data = request.get_json()
        room_name = data.get('room_name')
        agent_name = data.get('agent_name')
        question = data.get('question')
        
        if not room_name or not agent_name or not question:
            return jsonify({"success": False, "error": "Missing room_name, agent_name, or question"}), 400
        
        if agent_name not in ['One', 'Two', 'Three', 'Four']:
            return jsonify({"success": False, "error": "agent_name must be One, Two, Three, or Four"}), 400
        
        # Store user question in transcript
        if room_name not in room_transcripts:
            room_transcripts[room_name] = []
        
        room_transcripts[room_name].append({
            "speaker": f"User (to {agent_name})",
            "text": question,
            "timestamp": time.time(),
            "time_formatted": time.strftime('%H:%M:%S', time.localtime())
        })
        
        # Generate agent response using Letta
        try:
            if LETTA_AVAILABLE:
                from src.livekit.agent_voices import get_agent_prompt_template
                from config.agents_config import LettaConfig
                import os
                
                # Get Letta client and agent ID
                letta_config = LettaConfig()
                client = letta_config.client
                agent_env_key = f'LETTA_AGENT_{agent_name}'
                agent_id = os.getenv(agent_env_key)
                
                if agent_id:
                    # Build personality-specific prompt
                    prompt_template = get_agent_prompt_template(agent_name, "user_question")
                    full_prompt = f"{prompt_template}\n\nQuestion: {question}\n\nContext: Room {room_name}"
                    
                    # Send message to agent
                    response = client.agents.messages.create(
                        agent_id=agent_id,
                        messages=[{"role": "user", "content": full_prompt}]
                    )
                    
                    # Extract response content
                    response_text = f"Agent {agent_name} is thinking..."
                    for msg in response.messages:
                        if hasattr(msg, 'content'):
                            response_text = msg.content.strip()
                            break
                else:
                    response_text = f"Agent {agent_name} says: 'I'm ready to code!'"
                    
            else:
                response_text = f"Agent {agent_name} says: 'Let's do this!'"
                
        except Exception as e:
            print(f"❌ Agent response error: {e}")
            response_text = f"Agent {agent_name} says: 'Ready to battle!'"
        
        # Add agent response to transcript
        room_transcripts[room_name].append({
            "speaker": f"Agent {agent_name}",
            "text": response_text,
            "timestamp": time.time(),
            "time_formatted": time.strftime('%H:%M:%S', time.localtime())
        })
        
        return jsonify({
            "success": True,
            "response_text": response_text,
            "agent_name": agent_name,
            "message": f"Agent {agent_name} responded"
        }), 200
        
    except Exception as e:
        print(f"❌ Ask agent error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/livekit/agent-reaction', methods=['POST'])
def agent_reaction():
    """Get reactions from all 4 agents to a battle event."""
    try:
        data = request.get_json()
        room_name = data.get('room_name')
        event_type = data.get('event_type')
        context = data.get('context', {})
        
        if not room_name or not event_type:
            return jsonify({"success": False, "error": "Missing room_name or event_type"}), 400
        
        # Get current battle state for emotion calculation
        battle_state = {
            "agent_stats": context.get("agent_stats", {}),
            "total_rounds": context.get("total_rounds", 1),
            "event_type": event_type
        }
        
        agent_responses = []
        
        # Import agent voices functions once at the start
        from src.livekit.agent_voices import get_agent_prompt_template, calculate_emotion_level
        
        # Generate reactions for each agent
        for agent_name in ['One', 'Two', 'Three', 'Four']:
            try:
                if LETTA_AVAILABLE:
                    from config.agents_config import LettaConfig
                    import os
                    
                    # Get Letta client and agent ID
                    letta_config = LettaConfig()
                    client = letta_config.client
                    agent_env_key = f'LETTA_AGENT_{agent_name}'
                    agent_id = os.getenv(agent_env_key)
                    
                    if agent_id:
                        # Build personality-specific prompt
                        prompt_template = get_agent_prompt_template(agent_name, event_type)
                        full_prompt = f"{prompt_template}\n\nContext: {context}"
                        
                        # Send message to agent
                        response = client.agents.messages.create(
                            agent_id=agent_id,
                            messages=[{"role": "user", "content": full_prompt}]
                        )
                        
                        # Extract response content
                        response_text = f"Agent {agent_name} reacts..."
                        for msg in response.messages:
                            if hasattr(msg, 'content'):
                                response_text = msg.content.strip()
                                break
                    else:
                        response_text = f"Agent {agent_name}: 'Let's go!'"
                        
                else:
                    response_text = f"Agent {agent_name}: 'Ready!'"
                    
            except Exception as e:
                print(f"❌ Agent {agent_name} reaction error: {e}")
                response_text = f"Agent {agent_name}: 'Battle time!'"
            
            agent_responses.append({
                "agent_name": agent_name,
                "response_text": response_text,
                "emotion_level": calculate_emotion_level(agent_name, battle_state)
            })
        
        # Add reactions to transcript
        if room_name not in room_transcripts:
            room_transcripts[room_name] = []
        
        for response in agent_responses:
            room_transcripts[room_name].append({
                "speaker": f"Agent {response['agent_name']}",
                "text": response['response_text'],
                "timestamp": time.time(),
                "time_formatted": time.strftime('%H:%M:%S', time.localtime())
            })
        
        return jsonify({
            "success": True,
            "agent_responses": agent_responses,
            "message": f"Generated reactions for {event_type}"
        }), 200
        
    except Exception as e:
        print(f"❌ Agent reaction error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/livekit/agent-config', methods=['GET'])
def get_agent_config():
    """Get agent voice configuration for frontend."""
    try:
        from src.livekit.agent_voices import AGENT_VOICE_CONFIG
        
        return jsonify({
            "success": True,
            "agent_config": AGENT_VOICE_CONFIG,
            "message": "Agent voice configuration retrieved"
        }), 200
        
    except Exception as e:
        print(f"❌ Get agent config error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# Agent Chat System Endpoints

@app.route('/api/agents/chat/direct', methods=['POST'])
def agent_chat_direct():
    """Direct 1-on-1 conversation between two agents."""
    try:
        data = request.get_json()
        from_agent = data.get('from_agent')
        to_agent = data.get('to_agent')
        message = data.get('message')
        project_id = data.get('project_id', f"chat_{int(time.time())}")

        if not from_agent or not to_agent or not message:
            return jsonify({"success": False, "error": "Missing from_agent, to_agent, or message"}), 400

        if from_agent not in ['One', 'Two', 'Three', 'Four'] or to_agent not in ['One', 'Two', 'Three', 'Four']:
            return jsonify({"success": False, "error": "Agent names must be One, Two, Three, or Four"}), 400

        # Run async function synchronously
        import asyncio
        result = asyncio.run(api_instance.agent_chat_direct(from_agent, to_agent, message, project_id))
        return jsonify(result), 200

    except Exception as e:
        print(f"❌ Direct chat error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/agents/chat/group', methods=['POST'])
def agent_chat_group():
    """Group discussion between multiple agents."""
    try:
        data = request.get_json()
        agent_names = data.get('agent_names', [])
        topic = data.get('topic')
        project_id = data.get('project_id', f"discussion_{int(time.time())}")

        if not agent_names or not topic:
            return jsonify({"success": False, "error": "Missing agent_names or topic"}), 400

        if len(agent_names) < 2:
            return jsonify({"success": False, "error": "At least 2 agents required for group discussion"}), 400

        valid_agents = ['One', 'Two', 'Three', 'Four']
        for agent in agent_names:
            if agent not in valid_agents:
                return jsonify({"success": False, "error": f"Invalid agent name: {agent}. Must be One, Two, Three, or Four"}), 400

        # Run async function synchronously
        import asyncio
        result = asyncio.run(api_instance.agent_chat_group(agent_names, topic, project_id))
        return jsonify(result), 200

    except Exception as e:
        print(f"❌ Group chat error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/agents/chat/battle-talk', methods=['POST'])
def agent_battle_talk():
    """Generate trash talk and competitive banter between agents."""
    try:
        data = request.get_json()
        project_id = data.get('project_id', f"battle_{int(time.time())}")
        battle_context = data.get('battle_context', {})
        trigger_event = data.get('trigger_event', 'battle_start')

        # Run async function synchronously
        import asyncio
        result = asyncio.run(api_instance.agent_battle_talk(project_id, battle_context, trigger_event))
        return jsonify(result), 200

    except Exception as e:
        print(f"❌ Battle talk error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# Claude Chat Simulator Endpoints
@app.route('/api/chat/send-message', methods=['POST'])
def chat_send_message():
    """Send a user message to the Claude chat simulator and get agent responses with timing."""
    try:
        if not CLAUDE_CHAT_AVAILABLE or not claude_chat_manager:
            return jsonify({
                "success": False,
                "error": "Claude chat simulator not available"
            }), 503
        
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({"success": False, "error": "Message cannot be empty"}), 400
        
        print(f"💬 User message: {user_message}")
        
        # Add user message to Claude's conversation history
        claude_chat_manager.add_user_message(user_message, is_boss=True)
        
        # Get response from Claude asynchronously
        import asyncio
        import random
        
        async def get_responses():
            # Get Claude's response with context about who should respond
            trigger_context = f"Boss just said: '{user_message}'. Generate 2-4 short agent responses (one per line, format: 'AgentName: message')."
            response = await claude_chat_manager.get_chat_response(trigger_context)
            return response
        
        # Run async function
        response_text = asyncio.run(get_responses())
        
        if not response_text:
            return jsonify({
                "success": False,
                "error": "Failed to get response from Claude"
            }), 500
        
        # Parse the response to extract individual agent messages with delays
        # Claude returns messages in format: "AgentName: message"
        messages = []
        base_time = time.time() * 1000  # Current time in milliseconds
        
        for i, line in enumerate(response_text.split('\n')):
            line = line.strip()
            if ':' in line and line:
                parts = line.split(':', 1)
                agent_name = parts[0].strip()
                message = parts[1].strip()
                
                # Add randomized delay between messages (1-3 seconds)
                delay_ms = random.randint(1000, 3000)
                timestamp = base_time + (i * delay_ms)
                
                messages.append({
                    "agent": agent_name,
                    "message": message,
                    "timestamp": timestamp,
                    "delay": delay_ms  # How long to wait before showing this message
                })
        
        print(f"✅ Generated {len(messages)} agent responses with timing")
        
        return jsonify({
            "success": True,
            "messages": messages,
            "raw_response": response_text
        }), 200
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/chat/random-message', methods=['GET'])
def chat_random_message():
    """Generate a random agent message (for background chatter)."""
    try:
        if not CLAUDE_CHAT_AVAILABLE or not claude_chat_manager:
            return jsonify({
                "success": False,
                "error": "Claude chat simulator not available"
            }), 503
        
        import asyncio
        import random
        from chat.chat_config import AGENT_PERSONAS
        
        async def get_random_message():
            # Pick random agents
            agent_names = list(AGENT_PERSONAS.keys())
            speaker = random.choice(agent_names)
            
            # Create context for random chatter
            trigger_context = f"[Random moment: {speaker} wants to say something brief about coding/the project. One short message only, format: '{speaker}: message']"
            response = await claude_chat_manager.get_chat_response(trigger_context)
            return response, speaker
        
        # Run async function
        response_text, expected_speaker = asyncio.run(get_random_message())
        
        if not response_text:
            return jsonify({
                "success": False,
                "error": "Failed to get response"
            }), 500
        
        # Parse response
        line = response_text.strip().split('\n')[0]
        if ':' in line:
            parts = line.split(':', 1)
            agent_name = parts[0].strip()
            message = parts[1].strip()
        else:
            agent_name = expected_speaker
            message = response_text.strip()
        
        return jsonify({
            "success": True,
            "message": {
                "agent": agent_name,
                "message": message,
                "timestamp": time.time() * 1000
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Random message error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    print("🔥 Starting REAL Flask API server...")
    print("📡 Available endpoints:")
    print("   GET  /api/health")
    print("   GET  /api/agents")
    print("   POST /api/submit-project")
    print("   POST /api/create-agents")
    print("   POST /api/start-work")
    print("   GET  /api/progress-messages")
    print("   POST /api/get-results")
    print("   POST /api/retrieve-code")
    print("   POST /api/select-winner")
    print("   POST /api/complete-round")
    print("   GET  /api/agent-stats")
    print("   GET  /api/project-status")
    print("   POST /api/get-messages")
    print("   POST /api/get-commentary")
    print("   POST /api/get-chat-summary")
    print("   POST /api/orchestrate-project")
    print("")
    print("🎙️ LiveKit Voice Commentary:")
    print("   POST /api/livekit/create-battle-room")
    print("   POST /api/livekit/join-room")
    print("   POST /api/livekit/ask-commentator")
    print("   GET  /api/livekit/get-transcript")
    print("   GET  /api/livekit/room-status")
    print("   POST /api/livekit/speak-text")
    print("🤖 Agent Voice System:")
    print("   POST /api/livekit/set-mode")
    print("   POST /api/livekit/ask-agent")
    print("   POST /api/livekit/agent-reaction")
    print("   GET  /api/livekit/agent-config")
    print("")
    print("💬 Agent Chat System:")
    print("   POST /api/agents/chat/direct")
    print("   POST /api/agents/chat/group")
    print("   POST /api/agents/chat/battle-talk")
    print("")
    print("🤖 Claude Chat Simulator:")
    print("   POST /api/chat/send-message")
    print("   GET  /api/chat/random-message")
    print(f"🤖 Letta Available: {LETTA_AVAILABLE}")
    print(f"🎙️ LiveKit Available: {LIVEKIT_AVAILABLE}")
    print(f"💬 Claude Chat Available: {CLAUDE_CHAT_AVAILABLE}")
    print("🌐 Server running on http://localhost:5003")
    app.run(host='0.0.0.0', port=5003, debug=True)
