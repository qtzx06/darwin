"""
Agent Voice Configuration - Maps each agent to their unique voice and personality.
"""

AGENT_VOICE_CONFIG = {
    "One": {
        "voice_id": "tQbs4WJdeIOdank6mubQ",  # Using commentator voice for now, will find casual/witty voice
        "personality": "sarcastic",
        "speech_style": "casual, humorous, uses slang",
        "color": "#3B82F6"  # Blue
    },
    "Two": {
        "voice_id": "oHwIxN4uGlD1D3IKyWJZ",  # Using commentator voice for now, will find professional voice
        "personality": "perfectionist",
        "speech_style": "formal, precise, technical",
        "color": "#10B981"  # Green
    },
    "Three": {
        "voice_id": "FMgBdHe1YV2Xi0B9anXW",  # Using commentator voice for now, will find aggressive voice
        "personality": "competitive",
        "speech_style": "fast-paced, intense, competitive",
        "color": "#EF4444"  # Red
    },
    "Four": {
        "voice_id": "E95NigJoVU5BI8HjQeN3",  # Using commentator voice for now, will find creative voice
        "personality": "creative",
        "speech_style": "smooth, artistic, design-focused",
        "color": "#8B5CF6"  # Purple
    }
}

def get_agent_voice_config(agent_name):
    """Get voice configuration for a specific agent."""
    return AGENT_VOICE_CONFIG.get(agent_name, AGENT_VOICE_CONFIG["One"])

def get_all_agent_names():
    """Get list of all agent names."""
    return list(AGENT_VOICE_CONFIG.keys())

def calculate_emotion_level(agent_name, battle_state):
    """
    Calculate emotion level (0.0-1.0) based on agent's current state.
    
    Args:
        agent_name: Name of the agent (One, Two, Three, Four)
        battle_state: Dict with agent stats and recent events
    
    Returns:
        float: Emotion level for ElevenLabs style parameter
    """
    agent_stats = battle_state.get("agent_stats", {})
    agent_wins = agent_stats.get(agent_name, {}).get("wins", 0)
    total_rounds = battle_state.get("total_rounds", 1)
    
    # Calculate win rate
    win_rate = agent_wins / total_rounds if total_rounds > 0 else 0
    
    # Determine emotion based on win rate
    if win_rate >= 0.6:  # Winning
        return 0.2  # Confident, slower
    elif win_rate <= 0.3:  # Losing
        return 0.8  # Frustrated, faster
    else:  # Close/Tied
        return 0.6  # Excited, intense

def get_agent_prompt_template(agent_name, event_type):
    """
    Get personality-specific prompt template for agent reactions.
    
    Args:
        agent_name: Name of the agent
        event_type: Type of event (code_submitted, won_round, lost_round, etc.)
    
    Returns:
        str: Prompt template for the agent
    """
    config = get_agent_voice_config(agent_name)
    personality = config["personality"]
    
    templates = {
        "code_submitted": {
            "sarcastic": "You just submitted code. React in 1 sentence with your sarcastic, humorous personality. Use slang and be casual.",
            "perfectionist": "You just submitted code. React in 1 sentence with your methodical, technical personality. Be formal and precise.",
            "competitive": "You just submitted code. React in 1 sentence with your aggressive, competitive personality. Be intense and fast-paced.",
            "creative": "You just submitted code. React in 1 sentence with your artistic, design-focused personality. Be smooth and creative."
        },
        "won_round": {
            "sarcastic": "You just won a round! React in 1 sentence with your sarcastic personality. Be cocky but funny.",
            "perfectionist": "You just won a round! React in 1 sentence with your methodical personality. Be professional and precise.",
            "competitive": "You just won a round! React in 1 sentence with your aggressive personality. Be triumphant and intense.",
            "creative": "You just won a round! React in 1 sentence with your artistic personality. Be celebratory and smooth."
        },
        "lost_round": {
            "sarcastic": "You just lost a round. React in 1 sentence with your sarcastic personality. Be disappointed but still funny.",
            "perfectionist": "You just lost a round. React in 1 sentence with your methodical personality. Be analytical and determined.",
            "competitive": "You just lost a round. React in 1 sentence with your aggressive personality. Be frustrated but competitive.",
            "creative": "You just lost a round. React in 1 sentence with your artistic personality. Be disappointed but graceful."
        },
        "user_question": {
            "sarcastic": "A spectator asked you a question. Answer in 1 sentence with your sarcastic, humorous personality. Be casual and witty.",
            "perfectionist": "A spectator asked you a question. Answer in 1 sentence with your methodical personality. Be formal and technical.",
            "competitive": "A spectator asked you a question. Answer in 1 sentence with your aggressive personality. Be intense and competitive.",
            "creative": "A spectator asked you a question. Answer in 1 sentence with your artistic personality. Be smooth and creative."
        }
    }
    
    return templates.get(event_type, {}).get(personality, "React in 1 sentence with your personality.")
