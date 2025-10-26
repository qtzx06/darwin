/**
 * API Service for Darwin Competitive Agent System
 * Handles all communication with the Flask backend
 */

const API_BASE_URL = 'http://localhost:5003';

class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

// Helper function for making API requests
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    const data = await response.json();

    if (!response.ok) {
      throw new ApiError(
        data.error || `HTTP ${response.status}`,
        response.status,
        data
      );
    }

    return data;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(`Network error: ${error.message}`, 0, null);
  }
}

// Core competitive API endpoints
export const competitiveApi = {
  // Project management
  async submitProject(projectDescription) {
    return apiRequest('/api/submit-project', {
      method: 'POST',
      body: JSON.stringify({ project_description: projectDescription }),
    });
  },

  async createAgents(projectId) {
    return apiRequest('/api/create-agents', {
      method: 'POST',
      body: JSON.stringify({ project_id: projectId }),
    });
  },

  async orchestrateProject(projectDescription) {
    console.log('📤 Sending orchestration request:', { project_description: projectDescription });
    const response = await apiRequest('/api/orchestrate-project', {
      method: 'POST',
      body: JSON.stringify({ project_description: projectDescription }),
    });
    console.log('📥 Received orchestration response:', response);
    console.log('📥 Response type:', typeof response);
    console.log('📥 Response keys:', Object.keys(response));
    if (response.subtasks) {
      console.log('📥 Subtasks:', response.subtasks);
    } else {
      console.log('⚠️ No subtasks property in response');
    }
    return response;
  },

  // Round management
  async startWork(projectId, subtaskId) {
    return apiRequest('/api/start-work', {
      method: 'POST',
      body: JSON.stringify({ project_id: projectId, subtask_id: subtaskId }),
    });
  },

  async getResults(projectId, agentNames = ['One', 'Two', 'Three', 'Four']) {
    return apiRequest('/api/get-results', {
      method: 'POST',
      body: JSON.stringify({ project_id: projectId, agent_names: agentNames }),
    });
  },

  async selectWinner(projectId, winner, reason) {
    return apiRequest('/api/select-winner', {
      method: 'POST',
      body: JSON.stringify({ project_id: projectId, winner, reason }),
    });
  },

  async completeRound(projectId, winner, winnerCode, subtaskId) {
    return apiRequest('/api/complete-round', {
      method: 'POST',
      body: JSON.stringify({
        project_id: projectId,
        winner,
        winner_code: winnerCode,
        subtask_id: subtaskId
      }),
    });
  },

  // Status and info
  async getAgentStats(projectId) {
    return apiRequest(`/api/agent-stats?project_id=${encodeURIComponent(projectId)}`);
  },

  async getProjectStatus(projectId) {
    return apiRequest(`/api/project-status?project_id=${encodeURIComponent(projectId)}`);
  },

  async getProgressMessages(projectId) {
    return apiRequest(`/api/progress-messages?project_id=${encodeURIComponent(projectId)}`);
  },

  async retrieveCode(projectId, agentName) {
    return apiRequest('/api/retrieve-code', {
      method: 'POST',
      body: JSON.stringify({ project_id: projectId, agent_name: agentName }),
    });
  },

  async getMessages(projectId, agentName) {
    return apiRequest('/api/get-messages', {
      method: 'POST',
      body: JSON.stringify({ project_id: projectId, agent_name: agentName }),
    });
  },

  async getCommentary(projectId, subtaskId) {
    return apiRequest('/api/get-commentary', {
      method: 'POST',
      body: JSON.stringify({ project_id: projectId, subtask_id: subtaskId }),
    });
  },

  async getChatSummary(projectId, subtaskId) {
    return apiRequest('/api/get-chat-summary', {
      method: 'POST',
      body: JSON.stringify({ project_id: projectId, subtask_id: subtaskId }),
    });
  },

  // Health check
  async getHealth() {
    return apiRequest('/api/health');
  },

  async getAgents() {
    return apiRequest('/api/agents');
  },
};

// LiveKit voice system API endpoints
export const livekitApi = {
  // Room management
  async createBattleRoom(projectId) {
    return apiRequest('/api/livekit/create-battle-room', {
      method: 'POST',
      body: JSON.stringify({ project_id: projectId }),
    });
  },

  async joinRoom(roomName, userName = 'Spectator') {
    return apiRequest('/api/livekit/join-room', {
      method: 'POST',
      body: JSON.stringify({ room_name: roomName, user_name: userName }),
    });
  },

  async getRoomStatus(roomName) {
    return apiRequest(`/api/livekit/room-status?room_name=${encodeURIComponent(roomName)}`);
  },

  async getTranscript(roomName) {
    return apiRequest(`/api/livekit/get-transcript?room_name=${encodeURIComponent(roomName)}`);
  },

  // Voice interaction
  async setMode(roomName, mode) {
    return apiRequest('/api/livekit/set-mode', {
      method: 'POST',
      body: JSON.stringify({ room_name: roomName, mode }),
    });
  },

  async askCommentator(roomName, question) {
    return apiRequest('/api/livekit/ask-commentator', {
      method: 'POST',
      body: JSON.stringify({ room_name: roomName, question }),
    });
  },

  async askAgent(roomName, agentName, question) {
    return apiRequest('/api/livekit/ask-agent', {
      method: 'POST',
      body: JSON.stringify({ room_name: roomName, agent_name: agentName, question }),
    });
  },

  async getAgentReaction(roomName, eventType, context = {}) {
    return apiRequest('/api/livekit/agent-reaction', {
      method: 'POST',
      body: JSON.stringify({ room_name: roomName, event_type: eventType, context }),
    });
  },

  async getAgentConfig() {
    return apiRequest('/api/livekit/agent-config');
  },

  // Text-to-speech
  async speakText(text, voiceId) {
    const response = await fetch(`${API_BASE_URL}/api/livekit/speak-text`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text, voice_id: voiceId }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new ApiError(
        errorData.error || `HTTP ${response.status}`,
        response.status,
        errorData
      );
    }

    return response.blob(); // Return audio blob
  },
};

// Agent chat system API endpoints
export const agentChatApi = {
  async directChat(fromAgent, toAgent, message, projectId) {
    return apiRequest('/api/agents/chat/direct', {
      method: 'POST',
      body: JSON.stringify({
        from_agent: fromAgent,
        to_agent: toAgent,
        message,
        project_id: projectId
      }),
    });
  },

  async groupChat(agentNames, topic, projectId) {
    return apiRequest('/api/agents/chat/group', {
      method: 'POST',
      body: JSON.stringify({
        agent_names: agentNames,
        topic,
        project_id: projectId
      }),
    });
  },

  async battleTalk(projectId, battleContext = {}, triggerEvent = 'battle_start') {
    return apiRequest('/api/agents/chat/battle-talk', {
      method: 'POST',
      body: JSON.stringify({
        project_id: projectId,
        battle_context: battleContext,
        trigger_event: triggerEvent
      }),
    });
  },
};

// Utility functions
export const apiUtils = {
  // Map backend agent names to frontend agent IDs
  mapAgentNameToId(backendName) {
    const mapping = {
      'One': 'speedrunner',
      'Two': 'bloom',
      'Three': 'solver',
      'Four': 'loader'
    };
    return mapping[backendName] || backendName.toLowerCase();
  },

  // Map frontend agent IDs to backend agent names
  mapAgentIdToName(frontendId) {
    const mapping = {
      'speedrunner': 'One',
      'bloom': 'Two',
      'solver': 'Three',
      'loader': 'Four'
    };
    return mapping[frontendId] || frontendId;
  },

  // Generate project ID
  generateProjectId() {
    return `project_${Date.now()}`;
  },

  // Format battle context for API calls
  formatBattleContext(currentLeader, roundNumber, taskDifficulty) {
    return {
      current_leader: currentLeader,
      round_number: roundNumber,
      task_difficulty: taskDifficulty,
    };
  },

  // Error handling helper
  handleApiError(error, fallbackMessage = 'An error occurred') {
    console.error('API Error:', error);

    if (error instanceof ApiError) {
      return {
        message: error.message,
        status: error.status,
        data: error.data,
      };
    }

    return {
      message: fallbackMessage,
      status: 0,
      data: null,
    };
  },
};

// Claude Chat Simulator API
export const claudeChatApi = {
  async sendMessage(message) {
    return apiRequest('/api/chat/send-message', {
      method: 'POST',
      body: JSON.stringify({ message }),
    });
  },
  
  async getRandomMessage() {
    return apiRequest('/api/chat/random-message', {
      method: 'GET',
    });
  },
};

// Export everything
export { ApiError };
export default {
  competitive: competitiveApi,
  livekit: livekitApi,
  agentChat: agentChatApi,
  claudeChat: claudeChatApi,
  utils: apiUtils,
};