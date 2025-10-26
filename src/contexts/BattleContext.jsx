import React, { createContext, useContext, useReducer, useEffect } from 'react';
import api, { apiUtils } from '../services/api';

// Initial state
const initialState = {
  // Project state
  projectId: null,
  projectDescription: '',
  subtasks: [],
  currentSubtaskIndex: 0,
  currentSubtask: null,
  projectStatus: 'idle', // idle, initializing, active, completed

  // Agent state
  agents: {
    speedrunner: { name: 'Speedrunner', status: 'idle', code: '', result: null, messages: [] },
    bloom: { name: 'Bloom', status: 'idle', code: '', result: null, messages: [] },
    solver: { name: 'Solver', status: 'idle', code: '', result: null, messages: [] },
    loader: { name: 'Loader', status: 'idle', code: '', result: null, messages: [] },
  },
  agentStats: null,
  currentWinner: null,
  roundInProgress: false,

  // LiveKit voice state
  roomName: null,
  roomToken: null,
  voiceMode: 'commentary', // commentary, agent
  transcript: [],
  roomStatus: null,
  agentConfig: null,

  // UI state
  expandedAgent: null,
  loading: false,
  error: null,

  // Chat state
  agentChats: [],
  battleTalk: [],
};

// Action types
const ActionTypes = {
  // Project actions
  SET_PROJECT: 'SET_PROJECT',
  SET_PROJECT_STATUS: 'SET_PROJECT_STATUS',
  SET_SUBTASKS: 'SET_SUBTASKS',
  SET_CURRENT_SUBTASK: 'SET_CURRENT_SUBTASK',

  // Agent actions
  SET_AGENT_STATUS: 'SET_AGENT_STATUS',
  SET_AGENT_RESULT: 'SET_AGENT_RESULT',
  SET_AGENT_CODE: 'SET_AGENT_CODE',
  SET_AGENT_MESSAGES: 'SET_AGENT_MESSAGES',
  SET_ALL_AGENTS_RESULTS: 'SET_ALL_AGENTS_RESULTS',
  SET_AGENT_STATS: 'SET_AGENT_STATS',
  SET_WINNER: 'SET_WINNER',
  SET_ROUND_IN_PROGRESS: 'SET_ROUND_IN_PROGRESS',

  // LiveKit actions
  SET_ROOM_INFO: 'SET_ROOM_INFO',
  SET_VOICE_MODE: 'SET_VOICE_MODE',
  ADD_TRANSCRIPT_MESSAGE: 'ADD_TRANSCRIPT_MESSAGE',
  SET_TRANSCRIPT: 'SET_TRANSCRIPT',
  SET_ROOM_STATUS: 'SET_ROOM_STATUS',
  SET_AGENT_CONFIG: 'SET_AGENT_CONFIG',

  // UI actions
  SET_EXPANDED_AGENT: 'SET_EXPANDED_AGENT',
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  CLEAR_ERROR: 'CLEAR_ERROR',

  // Chat actions
  ADD_AGENT_CHAT: 'ADD_AGENT_CHAT',
  ADD_BATTLE_TALK: 'ADD_BATTLE_TALK',
};

// Reducer
function battleReducer(state, action) {
  switch (action.type) {
    case ActionTypes.SET_PROJECT:
      return {
        ...state,
        projectId: action.payload.projectId,
        projectDescription: action.payload.description,
      };

    case ActionTypes.SET_PROJECT_STATUS:
      return {
        ...state,
        projectStatus: action.payload,
      };

    case ActionTypes.SET_SUBTASKS:
      return {
        ...state,
        subtasks: action.payload,
        currentSubtask: action.payload[0] || null,
      };

    case ActionTypes.SET_CURRENT_SUBTASK:
      return {
        ...state,
        currentSubtaskIndex: action.payload,
        currentSubtask: state.subtasks[action.payload] || null,
      };

    case ActionTypes.SET_AGENT_STATUS:
      return {
        ...state,
        agents: {
          ...state.agents,
          [action.payload.agentId]: {
            ...state.agents[action.payload.agentId],
            status: action.payload.status,
          },
        },
      };

    case ActionTypes.SET_AGENT_RESULT:
      return {
        ...state,
        agents: {
          ...state.agents,
          [action.payload.agentId]: {
            ...state.agents[action.payload.agentId],
            result: action.payload.result,
          },
        },
      };

    case ActionTypes.SET_AGENT_CODE:
      return {
        ...state,
        agents: {
          ...state.agents,
          [action.payload.agentId]: {
            ...state.agents[action.payload.agentId],
            code: action.payload.code,
          },
        },
      };

    case ActionTypes.SET_AGENT_MESSAGES:
      return {
        ...state,
        agents: {
          ...state.agents,
          [action.payload.agentId]: {
            ...state.agents[action.payload.agentId],
            messages: action.payload.messages,
          },
        },
      };

    case ActionTypes.SET_ALL_AGENTS_RESULTS:
      const updatedAgents = { ...state.agents };
      action.payload.forEach(result => {
        const agentId = apiUtils.mapAgentNameToId(result.agent_name);
        if (updatedAgents[agentId]) {
          updatedAgents[agentId] = {
            ...updatedAgents[agentId],
            result,
            code: result.code || '',
            status: 'completed',
          };
        }
      });
      return {
        ...state,
        agents: updatedAgents,
      };

    case ActionTypes.SET_AGENT_STATS:
      return {
        ...state,
        agentStats: action.payload,
      };

    case ActionTypes.SET_WINNER:
      return {
        ...state,
        currentWinner: action.payload,
      };

    case ActionTypes.SET_ROUND_IN_PROGRESS:
      return {
        ...state,
        roundInProgress: action.payload,
      };

    case ActionTypes.SET_ROOM_INFO:
      return {
        ...state,
        roomName: action.payload.roomName,
        roomToken: action.payload.token,
      };

    case ActionTypes.SET_VOICE_MODE:
      return {
        ...state,
        voiceMode: action.payload,
      };

    case ActionTypes.ADD_TRANSCRIPT_MESSAGE:
      return {
        ...state,
        transcript: [...state.transcript, action.payload],
      };

    case ActionTypes.SET_TRANSCRIPT:
      return {
        ...state,
        transcript: action.payload,
      };

    case ActionTypes.SET_ROOM_STATUS:
      return {
        ...state,
        roomStatus: action.payload,
      };

    case ActionTypes.SET_AGENT_CONFIG:
      return {
        ...state,
        agentConfig: action.payload,
      };

    case ActionTypes.SET_EXPANDED_AGENT:
      return {
        ...state,
        expandedAgent: action.payload,
      };

    case ActionTypes.SET_LOADING:
      return {
        ...state,
        loading: action.payload,
      };

    case ActionTypes.SET_ERROR:
      return {
        ...state,
        error: action.payload,
      };

    case ActionTypes.CLEAR_ERROR:
      return {
        ...state,
        error: null,
      };

    case ActionTypes.ADD_AGENT_CHAT:
      return {
        ...state,
        agentChats: [...state.agentChats, action.payload],
      };

    case ActionTypes.ADD_BATTLE_TALK:
      return {
        ...state,
        battleTalk: [...state.battleTalk, ...action.payload],
      };

    default:
      return state;
  }
}

// Create context
const BattleContext = createContext();

// Provider component
export function BattleProvider({ children }) {
  const [state, dispatch] = useReducer(battleReducer, initialState);

  // Helper function to handle API errors
  const handleError = (error, fallbackMessage) => {
    const errorInfo = apiUtils.handleApiError(error, fallbackMessage);
    dispatch({ type: ActionTypes.SET_ERROR, payload: errorInfo.message });
    console.error('Battle Context Error:', errorInfo);
  };

  // Project actions
  const actions = {
    async submitProject(projectDescription) {
      dispatch({ type: ActionTypes.SET_LOADING, payload: true });
      dispatch({ type: ActionTypes.CLEAR_ERROR });

      try {
        dispatch({ type: ActionTypes.SET_PROJECT_STATUS, payload: 'initializing' });

        // Submit project
        const projectResult = await api.competitive.submitProject(projectDescription);
        const projectId = projectResult.project_id;

        dispatch({
          type: ActionTypes.SET_PROJECT,
          payload: { projectId, description: projectDescription }
        });

        // Run these operations in parallel to speed up initialization
        const [agentCreation, orchestrationResult, roomResult, agentConfig] = await Promise.all([
          api.competitive.createAgents(projectId),
          api.competitive.orchestrateProject(projectDescription),
          api.livekit.createBattleRoom(projectId),
          api.livekit.getAgentConfig()
        ]);

        // Update state with all results
        dispatch({ type: ActionTypes.SET_SUBTASKS, payload: orchestrationResult.subtasks || [] });
        dispatch({
          type: ActionTypes.SET_ROOM_INFO,
          payload: { roomName: roomResult.room_name, token: roomResult.commentator_token }
        });
        dispatch({ type: ActionTypes.SET_AGENT_CONFIG, payload: agentConfig.agent_config });

        dispatch({ type: ActionTypes.SET_PROJECT_STATUS, payload: 'active' });

        return { projectId, roomName: roomResult.room_name };
      } catch (error) {
        handleError(error, 'Failed to submit project');
        dispatch({ type: ActionTypes.SET_PROJECT_STATUS, payload: 'idle' });
        throw error;
      } finally {
        dispatch({ type: ActionTypes.SET_LOADING, payload: false });
      }
    },

    async startRound(subtaskIndex = null) {
      if (!state.projectId) throw new Error('No active project');

      const subtaskIdx = subtaskIndex ?? state.currentSubtaskIndex;
      const subtask = state.subtasks[subtaskIdx];

      if (!subtask) throw new Error('No subtask available');

      dispatch({ type: ActionTypes.SET_LOADING, payload: true });
      dispatch({ type: ActionTypes.SET_ROUND_IN_PROGRESS, payload: true });

      try {
        // Set all agents to working status
        Object.keys(state.agents).forEach(agentId => {
          dispatch({
            type: ActionTypes.SET_AGENT_STATUS,
            payload: { agentId, status: 'working' }
          });
        });

        // Start work
        await api.competitive.startWork(state.projectId, subtaskIdx + 1);

        // Generate battle talk for round start
        const battleContext = apiUtils.formatBattleContext(
          state.currentWinner,
          subtaskIdx + 1,
          'medium'
        );

        const battleTalk = await api.agentChat.battleTalk(
          state.projectId,
          battleContext,
          'battle_start'
        );

        if (battleTalk.success) {
          dispatch({ type: ActionTypes.ADD_BATTLE_TALK, payload: battleTalk.trash_talk });
        }

        dispatch({ type: ActionTypes.SET_CURRENT_SUBTASK, payload: subtaskIdx });

      } catch (error) {
        handleError(error, 'Failed to start round');
        dispatch({ type: ActionTypes.SET_ROUND_IN_PROGRESS, payload: false });
        throw error;
      } finally {
        dispatch({ type: ActionTypes.SET_LOADING, payload: false });
      }
    },

    async pollResults() {
      if (!state.projectId || !state.roundInProgress) return;

      try {
        const results = await api.competitive.getResults(state.projectId);
        if (results.success && results.results) {
          dispatch({ type: ActionTypes.SET_ALL_AGENTS_RESULTS, payload: results.results });

          // Check if all agents are done
          const allCompleted = results.results.every(result => result.agent_name && result.code);
          if (allCompleted) {
            dispatch({ type: ActionTypes.SET_ROUND_IN_PROGRESS, payload: false });
          }
        }
      } catch (error) {
        console.warn('Failed to poll results:', error);
      }
    },

    async selectWinner(agentId, reason) {
      if (!state.projectId) throw new Error('No active project');

      const agentName = apiUtils.mapAgentIdToName(agentId);

      try {
        await api.competitive.selectWinner(state.projectId, agentName, reason);
        dispatch({ type: ActionTypes.SET_WINNER, payload: agentId });

        // Get updated stats
        const stats = await api.competitive.getAgentStats(state.projectId);
        dispatch({ type: ActionTypes.SET_AGENT_STATS, payload: stats.agent_stats });

        return true;
      } catch (error) {
        handleError(error, 'Failed to select winner');
        throw error;
      }
    },

    async completeRound() {
      if (!state.projectId || !state.currentWinner) {
        throw new Error('Cannot complete round without project and winner');
      }

      const winnerAgent = state.agents[state.currentWinner];
      const agentName = apiUtils.mapAgentIdToName(state.currentWinner);

      try {
        const result = await api.competitive.completeRound(
          state.projectId,
          agentName,
          winnerAgent.code,
          state.currentSubtaskIndex + 1
        );

        if (result.has_more_subtasks) {
          dispatch({ type: ActionTypes.SET_CURRENT_SUBTASK, payload: state.currentSubtaskIndex + 1 });
        } else {
          dispatch({ type: ActionTypes.SET_PROJECT_STATUS, payload: 'completed' });
        }

        return result;
      } catch (error) {
        handleError(error, 'Failed to complete round');
        throw error;
      }
    },

    // Voice actions
    async setVoiceMode(mode) {
      if (!state.roomName) return;

      try {
        await api.livekit.setMode(state.roomName, mode);
        dispatch({ type: ActionTypes.SET_VOICE_MODE, payload: mode });
      } catch (error) {
        handleError(error, 'Failed to set voice mode');
      }
    },

    async askCommentator(question) {
      if (!state.roomName) throw new Error('No active room');

      try {
        const response = await api.livekit.askCommentator(state.roomName, question);

        // Add to transcript
        dispatch({
          type: ActionTypes.ADD_TRANSCRIPT_MESSAGE,
          payload: {
            speaker: 'User',
            message: question,
            timestamp: Date.now(),
          }
        });

        dispatch({
          type: ActionTypes.ADD_TRANSCRIPT_MESSAGE,
          payload: {
            speaker: 'Commentator',
            message: response.response_text,
            timestamp: Date.now(),
          }
        });

        return response;
      } catch (error) {
        handleError(error, 'Failed to ask commentator');
        throw error;
      }
    },

    async askAgent(agentId, question) {
      if (!state.roomName) throw new Error('No active room');

      const agentName = apiUtils.mapAgentIdToName(agentId);

      try {
        const response = await api.livekit.askAgent(state.roomName, agentName, question);

        // Add to transcript
        dispatch({
          type: ActionTypes.ADD_TRANSCRIPT_MESSAGE,
          payload: {
            speaker: 'User',
            message: `@${agentName}: ${question}`,
            timestamp: Date.now(),
          }
        });

        dispatch({
          type: ActionTypes.ADD_TRANSCRIPT_MESSAGE,
          payload: {
            speaker: agentName,
            message: response.response_text,
            timestamp: Date.now(),
          }
        });

        return response;
      } catch (error) {
        handleError(error, `Failed to ask ${agentName}`);
        throw error;
      }
    },

    // Chat actions
    async sendDirectMessage(fromAgentId, toAgentId, message) {
      if (!state.projectId) throw new Error('No active project');

      const fromAgent = apiUtils.mapAgentIdToName(fromAgentId);
      const toAgent = apiUtils.mapAgentIdToName(toAgentId);

      try {
        const response = await api.agentChat.directChat(fromAgent, toAgent, message, state.projectId);

        if (response.success) {
          dispatch({ type: ActionTypes.ADD_AGENT_CHAT, payload: response });
        }

        return response;
      } catch (error) {
        handleError(error, 'Failed to send direct message');
        throw error;
      }
    },

    async startGroupDiscussion(agentIds, topic) {
      if (!state.projectId) throw new Error('No active project');

      const agentNames = agentIds.map(id => apiUtils.mapAgentIdToName(id));

      try {
        const response = await api.agentChat.groupChat(agentNames, topic, state.projectId);

        if (response.success) {
          dispatch({ type: ActionTypes.ADD_AGENT_CHAT, payload: response });
        }

        return response;
      } catch (error) {
        handleError(error, 'Failed to start group discussion');
        throw error;
      }
    },

    // UI actions
    setExpandedAgent(agentId) {
      dispatch({ type: ActionTypes.SET_EXPANDED_AGENT, payload: agentId });
    },

    clearError() {
      dispatch({ type: ActionTypes.CLEAR_ERROR });
    },
  };

  // Auto-polling for results during active rounds
  useEffect(() => {
    if (!state.roundInProgress) return;

    const interval = setInterval(() => {
      actions.pollResults();
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(interval);
  }, [state.roundInProgress, state.projectId]);

  return (
    <BattleContext.Provider value={{ state, actions }}>
      {children}
    </BattleContext.Provider>
  );
}

// Hook to use the context
export function useBattle() {
  const context = useContext(BattleContext);
  if (!context) {
    throw new Error('useBattle must be used within a BattleProvider');
  }
  return context;
}

export default BattleContext;