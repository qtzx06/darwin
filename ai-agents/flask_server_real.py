#!/usr/bin/env python3
"""
Real Flask server that makes actual Letta API calls
"""

import sys
import os
import json
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add current directory to path
sys.path.append('.')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from api_wrapper import CompetitiveAPI
    from src.core.agent_factory import AgentFactory
    from letta_client import Letta
    LETTA_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Warning: letta_client not available: {e}")
    print("   Using simulated mode instead")
    LETTA_AVAILABLE = False
    # Mock classes for simulated mode
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
    return jsonify(result), 200

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
    print(f"🤖 Letta Available: {LETTA_AVAILABLE}")
    print("🌐 Server running on http://localhost:5003")
    app.run(host='0.0.0.0', port=5003, debug=True)
