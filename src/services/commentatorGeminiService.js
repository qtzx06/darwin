import { GoogleGenAI } from '@google/genai';

const API_KEY = import.meta.env.VITE_GEMINI_API_KEY;
const ai = new GoogleGenAI({ apiKey: API_KEY });

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

STYLE GUIDELINES:
- Use contractions: "they're" not "they are"
- Use casual speech: "gonna" not "going to", "wanna" not "want to"
- Use abbreviations people actually say: "ngl" "fr" "lowkey" "highkey" "rn"
- Avoid technical jargon unless it sounds natural
- Make it conversational like you're talking to friends watching the battle

AGENTS:
- Speedrunner: fast, competitive, always trying to finish first
- Bloom: focused on animations and visual effects
- Solver: logic and functionality focused
- Loader: handles data and async operations

EXAMPLES:
❌ BAD: "Speedrunner is currently implementing the button functionality with excellent efficiency."
✅ GOOD: "Speedrunner's flying rn, already got that button working!"

❌ BAD: "Bloom has created beautiful animations for the component."
✅ GOOD: "Bloom's animations looking fire fr fr"

❌ BAD: "Solver is debugging an error in the code."
✅ GOOD: "Solver's fixing bugs while speedrunner's already done, ngl that's tough"

Keep responses under 15 words. Make every word count. Be entertaining!`;

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
   * Generate commentary from recent chat messages
   */
  async generateCommentary(chatMessages) {
    try {
      // Only process new messages
      if (chatMessages.length === this.lastProcessedMessageCount) {
        return null;
      }

      // Get the last few messages for context
      const recentMessages = chatMessages.slice(-8);
      this.lastProcessedMessageCount = chatMessages.length;

      // Filter out system messages, only get agent updates
      const agentUpdates = recentMessages
        .filter(msg => msg.type === 'agent' || msg.sender !== 'user')
        .map(msg => msg.text)
        .join('\n');

      if (!agentUpdates) {
        return null;
      }

      console.log('[Commentator Gemini] Generating commentary for:', agentUpdates);

      // Check if there's beef/competition happening
      const hasMultipleAgents = recentMessages.filter(m => m.type === 'agent').length > 1;
      const hasBanter = agentUpdates.toLowerCase().includes('ngl') ||
                        agentUpdates.toLowerCase().includes('bro') ||
                        agentUpdates.toLowerCase().includes('trash') ||
                        agentUpdates.toLowerCase().includes('better');

      let prompt;
      if (hasMultipleAgents && hasBanter) {
        prompt = `The agents are beefing! React to this drama with SHORT hype commentary (max 12 words):

${agentUpdates}

Call out the beef, who's winning, make it exciting:`;
      } else if (hasMultipleAgents) {
        prompt = `Multiple agents working! React to their progress with SHORT commentary (max 12 words):

${agentUpdates}

Compare their approaches, who's ahead:`;
      } else {
        prompt = `React to this agent update with SHORT commentary (max 12 words):

${agentUpdates}

Make it hyped and natural:`;
      }

      const response = await ai.models.generateContent({
        model: 'gemini-2.5-flash-lite',
        contents: [{
          role: 'user',
          parts: [{ text: prompt }]
        }],
        systemInstruction: this.systemInstruction
      });

      const commentary = response.text.trim();

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

      const commentary = response.text.trim();

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

      const commentary = response.text.trim();

      console.log('[Commentator Gemini] Periodic update:', commentary);
      return commentary;

    } catch (error) {
      console.error('[Commentator Gemini] Failed to generate periodic update:', error);
      return null;
    }
  }
}

export default CommentatorGeminiService;
