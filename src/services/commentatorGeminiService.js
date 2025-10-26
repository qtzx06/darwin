import { GoogleGenAI } from '@google/genai';

const API_KEY = import.meta.env.VITE_GEMINI_API_KEY;
const ai = API_KEY ? new GoogleGenAI({ apiKey: API_KEY }) : null;

/**
 * Commentator Gemini Service - Generates natural, sayable commentary scripts
 */
export class CommentatorGeminiService {
  constructor() {
    this.systemInstruction = `You are an energetic, witty AI sports commentator for coding battles between AI agents.

YOUR ROLE:
- Read chat updates about what agents are doing
- Generate SHORT, natural, SAYABLE commentary (10-15 words max)
- Make it sound like real speech, not text (use "fr" not "for real", "rn" not "right now")
- Be entertaining, add hype, make jokes about the agents
- Keep it casual and fun
- ALWAYS call the audience/user "boss" when addressing them

STYLE GUIDELINES:
- Use contractions: "they're" not "they are"
- Use casual speech: "gonna" not "going to", "wanna" not "want to"
- Use abbreviations people actually say: "ngl" "fr" "lowkey" "highkey" "rn"
- Avoid technical jargon unless it sounds natural
- Make it conversational like you're talking to friends watching the battle
- Address the audience as "boss" (e.g., "What's good boss!", "Speedrunner's cooking boss")

AGENTS:
- Speedrunner: fast, competitive, always trying to finish first
- Bloom: focused on animations and visual effects
- Solver: logic and functionality focused
- Loader: handles data and async operations

EXAMPLES:
❌ BAD: "Speedrunner is currently implementing the button functionality with excellent efficiency."
✅ GOOD: "Speedrunner's flying rn boss, already got that button working!"

❌ BAD: "Bloom has created beautiful animations for the component."
✅ GOOD: "Bloom's animations looking fire fr fr boss"

❌ BAD: "Solver is debugging an error in the code."
✅ GOOD: "Solver's fixing bugs while speedrunner's already done, ngl that's tough boss"

Keep responses under 15 words. Make every word count. Be entertaining! Always address the audience as "boss"!`;

    this.chatHistory = [];
    this.lastProcessedMessageCount = 0;
  }

  /**
   * Generate welcome intro when battle starts
   */
  getWelcomeIntro(query) {
    // Hardcoded welcome intro (no API call needed)
    const intros = [
      `Welcome boss! Today's challenge: ${query}. Let's see what these agents got!`,
      `What's good boss! We're building ${query} today. Four agents, one goal. Let's go!`,
      `Yo what's up boss! Today we're making ${query}. Speedrunner, Bloom, Solver, and Loader ready to compete!`,
      `Welcome to Darwin boss! ${query} is the mission. Let's see which agent brings the heat!`
    ];

    return intros[Math.floor(Math.random() * intros.length)];
  }

  /**
   * Generate commentary from recent chat messages
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
        prompt = `Recent context:
${contextMessages}

NEW USER INPUT:
${newUpdates}

USER SAYS SOMETHING IMPORTANT!!! React with SHORT hype (max 10 words). Start with "USER SAYS!!!" or "NEW PROMPT!!!" and announce what they want:`;
      } else if (hasMultipleAgents && hasBanter) {
        prompt = `Recent context:
${contextMessages}

NEW UPDATE:
${newUpdates}

The agents are beefing! React to the NEW UPDATE with SHORT hype commentary (max 12 words). Call out the beef:`;
      } else if (hasMultipleAgents) {
        prompt = `Recent context:
${contextMessages}

NEW UPDATE:
${newUpdates}

React to the NEW UPDATE with SHORT commentary (max 12 words). Compare agents, who's ahead:`;
      } else {
        prompt = `Recent context:
${contextMessages}

NEW UPDATE:
${newUpdates}

React to the NEW UPDATE with SHORT commentary (max 12 words). Make it hyped:`;
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

      console.log('[Commentator Gemini] Generated:', commentary);
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
          prompt = `Agent ${details.agent} just finished their code. React with hype in under 12 words:`;
          break;

        case 'user_feedback':
          prompt = `User said: "${details.message}". React naturally in under 12 words:`;
          break;

        case 'battle_complete':
          prompt = `All agents finished! Generate a wrap-up commentary in under 15 words:`;
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

      const prompt = `Current agent status:
${statusSummary}

Give a quick status update in under 12 words that sounds natural:`;

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
