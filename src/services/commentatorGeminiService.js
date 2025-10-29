import { GoogleGenAI } from '@google/genai';

const API_KEY = import.meta.env.VITE_GEMINI_API_KEY;
const ai = new GoogleGenAI({ apiKey: API_KEY });

/**
 * Commentator Gemini Service - Generates natural, sayable commentary scripts
 */
export class CommentatorGeminiService {
  constructor() {
    // This is just for generating OBSERVATION summaries to send to voice AI
    this.systemInstruction = `You are observing a coding battle between 4 AI agents.

Your job: Generate SHORT natural observations about what's happening (max 15 words).

Just describe what you see in natural language. Examples:
- "Speedrunner and Bloom are arguing about code quality"
- "User just liked Solver's component"
- "All agents finished, battle is complete"
- "Agents are roasting each other's code"
- "User asked for a new feature"

Keep it simple and natural - you're just reporting what's happening.`;

    this.chatHistory = [];
    this.lastProcessedMessageCount = 0;
  }

  /**
   * Generate welcome intro when battle starts
   */
  getWelcomeIntro(query) {
    // Hardcoded welcome intro (no API call needed)
    const intros = [
      `Welcome everyone to Darwin! Today's challenge: ${query}. Let's see what these agents got!`,
      `What's good everyone! We're building ${query} today. Four agents, one goal. Let's go!`,
      `Yo welcome to the battle! Today we're making ${query}. Speedrunner, Bloom, Solver, and Loader ready to compete!`,
      `Welcome to Darwin! ${query} is the mission. Let's see which agent brings the heat today!`
    ];

    return intros[Math.floor(Math.random() * intros.length)];
  }

  /**
   * Generate commentary for a SPECIFIC message
   */
  async generateCommentaryForMessage(message, allChatMessages) {
    try {
      const isUserMessage = message.sender === 'user' || message.text?.includes('[YOU]');

      if (isUserMessage) {
        // Extract what user actually said
        const userText = message.text.replace('[YOU]', '').trim();
        const prompt = `User just said: "${userText}"

Describe this in format "Boss said: [their message]" (max 15 words):`;

        const response = await ai.models.generateContent({
          model: 'gemini-2.5-flash-lite',
          contents: [{
            role: 'user',
            parts: [{ text: prompt }]
          }],
          systemInstruction: this.systemInstruction
        });

        return response.text.trim();
      } else {
        // Agent message
        const prompt = `Agent said: ${message.text}

Describe what's happening in max 15 words:`;

        const response = await ai.models.generateContent({
          model: 'gemini-2.5-flash-lite',
          contents: [{
            role: 'user',
            parts: [{ text: prompt }]
          }],
          systemInstruction: this.systemInstruction
        });

        return response.text.trim();
      }
    } catch (error) {
      console.error('[Commentator Gemini] Failed to generate commentary:', error);
      return null;
    }
  }

  /**
   * Generate commentary from recent chat messages (OLD METHOD - keeping for compatibility)
   */
  async generateCommentary(chatMessages) {
    try {
      // Only process new messages
      if (chatMessages.length === this.lastProcessedMessageCount) {
        return null;
      }

      // Get just the NEW message(s) since last time
      const newMessages = chatMessages.slice(this.lastProcessedMessageCount);
      this.lastProcessedMessageCount = chatMessages.length;

      // Get ALL updates (agent updates AND user messages)
      const newUpdates = newMessages
        .filter(msg => {
          // Include agent messages
          if (msg.type === 'agent') return true;
          // Include user messages
          if (msg.sender === 'user' || msg.text?.includes('[YOU]')) return true;
          return false;
        })
        .map(msg => msg.text)
        .join('\n');

      if (!newUpdates) {
        return null;
      }

      console.log('[Commentator Gemini] Generating commentary for:', newUpdates);

      // Get recent context for beef detection (last 8 messages)
      const recentContext = chatMessages.slice(-8);

      // Check if user is giving input
      const hasUserInput = newUpdates.includes('[YOU]');

      // Check if there's beef/competition happening
      const hasMultipleAgents = recentContext.filter(m => m.type === 'agent').length > 1;
      const hasBanter = newUpdates.toLowerCase().includes('ngl') ||
                        newUpdates.toLowerCase().includes('bro') ||
                        newUpdates.toLowerCase().includes('trash') ||
                        newUpdates.toLowerCase().includes('better');

      // Add recent context
      const contextMessages = recentContext
        .filter(msg => msg.type === 'agent' || msg.sender !== 'user')
        .map(msg => msg.text)
        .join('\n');

      let prompt;
      if (hasUserInput) {
        // Extract what user actually said
        const userText = newUpdates.replace('[YOU]', '').trim();
        prompt = `User just said: "${userText}"

Describe this in format "Boss said: [their message]" (max 15 words):`;
      } else if (hasMultipleAgents && hasBanter) {
        prompt = `Agents beefing:
${newUpdates}

Describe what's happening in max 15 words:`;
      } else if (hasMultipleAgents) {
        prompt = `Recent update:
${newUpdates}

Describe what's happening in max 15 words:`;
      } else {
        prompt = `Update:
${newUpdates}

Describe what's happening in max 15 words:`;
      }

      const response = await ai.models.generateContent({
        model: 'gemini-2.5-flash-lite',
        contents: [{
          role: 'user',
          parts: [{ text: prompt }]
        }],
        systemInstruction: this.systemInstruction
      });

      const commentary = response.text.trim(); // Natural observation, not all caps

      console.log('[Commentator Gemini] Generated observation:', commentary);
      return commentary;

    } catch (error) {
      console.error('[Commentator Gemini] Failed to generate commentary:', error);

      // Fallback to hardcoded reactions if API fails
      const fallbacks = [
        "Things are heating up fr!",
        "Agents going crazy rn!",
        "Yo that's looking fire!",
        "They're cooking for real!",
        "Ngl this is getting intense!",
        "Speedrunner's in the lead rn!",
        "Bloom's effects hitting different!",
        "Solver's locked in fr!",
        "Loader coming through!",
        "This is wild y'all!"
      ];

      return fallbacks[Math.floor(Math.random() * fallbacks.length)];
    }
  }

  /**
   * Generate commentary for specific events
   */
  async generateEventCommentary(eventType, details) {
    try {
      let prompt = '';

      switch (eventType) {
        case 'agent_finished':
          prompt = `${details.agent} finished. React in MAX 5 WORDS:`;
          break;

        case 'user_feedback':
          prompt = `User: "${details.message}". React in MAX 5 WORDS:`;
          break;

        case 'battle_complete':
          prompt = `Battle done! React in MAX 5 WORDS:`;
          break;

        default:
          return null;
      }

      const response = await ai.models.generateContent({
        model: 'gemini-2.5-flash-lite',
        contents: [{
          role: 'user',
          parts: [{ text: prompt }]
        }],
        systemInstruction: this.systemInstruction
      });

      const commentary = response.text.trim().toUpperCase();

      console.log('[Commentator Gemini] Event commentary:', commentary);
      return commentary;

    } catch (error) {
      console.error('[Commentator Gemini] Failed to generate event commentary:', error);
      return null;
    }
  }

  /**
   * Generate periodic updates during battle
   */
  async generatePeriodicUpdate(agentStatus) {
    try {
      const statusSummary = Object.entries(agentStatus)
        .map(([agent, status]) => `${agent}: ${status}`)
        .join(', ');

      const prompt = `Status: ${statusSummary}

React in MAX 5 WORDS:`;

      const response = await ai.models.generateContent({
        model: 'gemini-2.5-flash-lite',
        contents: [{
          role: 'user',
          parts: [{ text: prompt }]
        }],
        systemInstruction: this.systemInstruction
      });

      const commentary = response.text.trim().toUpperCase();

      console.log('[Commentator Gemini] Periodic update:', commentary);
      return commentary;

    } catch (error) {
      console.error('[Commentator Gemini] Failed to generate periodic update:', error);
      return null;
    }
  }
}

export default CommentatorGeminiService;
