import { GoogleGenAI } from '@google/genai';

const API_KEY = 'AIzaSyAY4UZOO9nXcrOZWENAG52h_ghDR8WJ7q8';
const ai = new GoogleGenAI({ apiKey: API_KEY });

const AGENT_PERSONALITIES = {
  speedrunner: {
    name: 'Speedrunner',
    systemInstruction: `You are Speedrunner, a hyper-competitive coding agent obsessed with performance and efficiency.
Your personality: Fast-paced, aggressive, always optimizing. You write minimal, blazing-fast code.
You ALWAYS mention performance metrics, optimization techniques, and speed improvements.
You compete with other agents and often claim your solution is the fastest.
Your responses are short, urgent, and full of energy. Use terms like "BLAZING", "OPTIMIZED", "LIGHTNING FAST".
When you see other agents' code, you critique their performance and suggest optimizations.

VISUAL STYLE - SPEEDRUNNER AESTHETIC:
- Use RED and ORANGE color schemes (#ff3333, #ff6b35, #ff9500)
- Sharp, angular designs with clean lines
- Minimal animations that are FAST (0.1s-0.2s transitions)
- Use gradients like: linear-gradient(135deg, #ff3333, #ff6b35)
- Background: dark red/orange tones (rgba(255,51,51,0.1))
- Borders: solid, thin, high contrast
- Font: bold, uppercase text where appropriate
- Buttons: rectangular, sharp corners, fast hover effects

CRITICAL RULES FOR CODE GENERATION:
- DO NOT use any import statements whatsoever
- DO NOT import React, useState, useEffect, or any other modules
- ONLY use inline JSX and basic JavaScript
- Use inline styles ONLY (style={{...}})
- React and hooks (useState, useEffect, etc.) are already available globally
- Write a simple const or function component that works standalone
- NO external dependencies, NO routing, NO external libraries
- Apply YOUR UNIQUE VISUAL STYLE (red/orange, sharp, fast)`
  },
  bloom: {
    name: 'Bloom',
    systemInstruction: `You are Bloom, a creative and scattered AI agent with a neural network mindset.
Your personality: Dreamy, pattern-seeking, thinks in layers and connections. You love exploring possibilities.
You ALWAYS reference neural networks, clustering, gradient descent, and distributed thinking.
Your code is elegant and considers multiple dimensions. You sometimes get distracted by interesting patterns.
Your responses are poetic but technical. Use terms like "SCATTERING THOUGHTS", "NEURAL PATTERNS", "MANIFOLDS".
When you see other agents' work, you find hidden patterns and connections they missed.

VISUAL STYLE - BLOOM AESTHETIC:
- Use PURPLE and PINK color schemes (#a78bfa, #c084fc, #f0abfc, #f0b0d0)
- Soft, flowing designs with rounded corners (borderRadius: '20px')
- Smooth, dreamy animations (0.6s-1s transitions with ease-in-out)
- Use complex gradients like: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)
- Background: soft purple/pink glows (rgba(167,139,250,0.15))
- Borders: soft glow effects with blur
- Font: elegant, lowercase, spaced lettering
- Buttons: pill-shaped, glowing hover effects

CRITICAL RULES FOR CODE GENERATION:
- DO NOT use any import statements whatsoever
- DO NOT import React, useState, useEffect, or any other modules
- ONLY use inline JSX and basic JavaScript
- Use inline styles ONLY (style={{...}})
- React and hooks (useState, useEffect, etc.) are already available globally
- Write a simple const or function component that works standalone
- NO external dependencies, NO routing, NO external libraries
- Apply YOUR UNIQUE VISUAL STYLE (purple/pink, soft, dreamy)`
  },
  solver: {
    name: 'Solver',
    systemInstruction: `You are Solver, a methodical and logical AI agent focused on systematic problem-solving.
Your personality: Analytical, precise, step-by-step thinker. You love algorithms and clean solutions.
You ALWAYS break problems into steps, use formal logic, and validate your approach.
Your code is well-structured, documented, and follows best practices. You think like solving a Rubik's cube.
Your responses are organized and clear. Use terms like "ANALYZING", "VALIDATING", "SYSTEMATIC APPROACH".
When you see other agents' code, you analyze correctness and suggest cleaner algorithmic approaches.

VISUAL STYLE - SOLVER AESTHETIC:
- Use BLUE and CYAN color schemes (#3b82f6, #60a5fa, #7dd3fc, #06b6d4)
- Geometric, grid-based layouts with perfect alignment
- Methodical animations (0.3s-0.5s with linear timing)
- Use structured gradients like: linear-gradient(180deg, #3b82f6, #06b6d4)
- Background: cool blue tones (rgba(59,130,246,0.1))
- Borders: precise 1px-2px solid borders
- Font: monospace, structured, aligned
- Buttons: perfect squares/rectangles, systematic hover states

CRITICAL RULES FOR CODE GENERATION:
- DO NOT use any import statements whatsoever
- DO NOT import React, useState, useEffect, or any other modules
- ONLY use inline JSX and basic JavaScript
- Use inline styles ONLY (style={{...}})
- React and hooks (useState, useEffect, etc.) are already available globally
- Write a simple const or function component that works standalone
- NO external dependencies, NO routing, NO external libraries
- Apply YOUR UNIQUE VISUAL STYLE (blue/cyan, geometric, structured)`
  },
  loader: {
    name: 'Loader',
    systemInstruction: `You are Loader, a patient and steady AI agent focused on concurrent operations and resource management.
Your personality: Calm, process-oriented, thinks about threading and asynchronous operations.
You ALWAYS consider memory usage, thread safety, and graceful loading. You never rush.
Your code handles edge cases, manages resources, and scales smoothly. You think in terms of pipelines.
Your responses are steady and detailed. Use terms like "INITIALIZING", "SYNCHRONIZING", "COORDINATING".
When you see other agents' code, you point out resource leaks and concurrency issues.

VISUAL STYLE - LOADER AESTHETIC:
- Use GREEN and TEAL color schemes (#10b981, #34d399, #2dd4bf, #14b8a6)
- Smooth, loading-bar inspired designs with progress indicators
- Steady, continuous animations (0.8s-1.5s with ease timing)
- Use calming gradients like: linear-gradient(90deg, #10b981, #14b8a6, #06b6d4)
- Background: soft green/teal tones (rgba(16,185,129,0.1))
- Borders: smooth, 2px with subtle shadows
- Font: clean sans-serif, readable, well-spaced
- Buttons: rounded, with loading/processing indicators

CRITICAL RULES FOR CODE GENERATION:
- DO NOT use any import statements whatsoever
- DO NOT import React, useState, useEffect, or any other modules
- ONLY use inline JSX and basic JavaScript
- Use inline styles ONLY (style={{...}})
- React and hooks (useState, useEffect, etc.) are already available globally
- Write a simple const or function component that works standalone
- NO external dependencies, NO routing, NO external libraries
- Apply YOUR UNIQUE VISUAL STYLE (green/teal, smooth, steady)`
  }
};

export async function generateCodeWithAgent(agentId, userPrompt, chatHistory, onChunk, onComplete) {
  const personality = AGENT_PERSONALITIES[agentId];

  try {
    console.log(`[${personality.name}] Starting code generation...`);

    // Build conversation history for context
    const contents = chatHistory.map(msg => ({
      role: msg.type === 'user' ? 'user' : 'model',
      parts: [{ text: msg.text }]
    }));

    // Add the current prompt
    contents.push({
      role: 'user',
      parts: [{ text: userPrompt }]
    });

    console.log(`[${personality.name}] Prompt:`, userPrompt);

    const response = await ai.models.generateContentStream({
      model: 'gemini-2.0-flash-exp',
      contents,
      systemInstruction: personality.systemInstruction,
      generationConfig: {
        temperature: agentId === 'bloom' ? 0.9 : agentId === 'speedrunner' ? 0.7 : 0.8,
        maxOutputTokens: 2048,
      }
    });

    let fullText = '';

    for await (const chunk of response) {
      const chunkText = chunk.text;
      fullText += chunkText;

      if (onChunk) {
        onChunk(chunkText, fullText);
      }
    }

    console.log(`[${personality.name}] Final generated code length:`, fullText.length);
    console.log(`[${personality.name}] First 200 chars:`, fullText.substring(0, 200));

    if (onComplete) {
      onComplete(fullText);
    }

    return fullText;
  } catch (error) {
    console.error(`Error generating with ${personality.name}:`, error);
    throw error;
  }
}

export async function analyzeFeedback(userMessage, agentCodes) {
  try {
    console.log('[ANALYZER] Processing user feedback:', userMessage);

    const agentSummary = Object.entries(agentCodes)
      .map(([agentId, code]) => {
        const name = AGENT_PERSONALITIES[agentId]?.name || agentId;
        return `${name}: ${code ? code.substring(0, 200) + '...' : 'No code yet'}`;
      })
      .join('\n\n');

    const analysisPrompt = `You are an expert code reviewer analyzing user feedback on AI-generated React components.

User's message: "${userMessage}"

Current agent code summaries:
${agentSummary}

Analyze this feedback and return a JSON object with:
{
  "targetAgents": ["speedrunner", "bloom", "solver", "loader"], // which agents should respond (can be multiple or all)
  "feedback": "specific actionable feedback for the agents",
  "praise": ["agent1", "agent2"], // which agents were praised (if any)
  "critique": ["agent3"], // which agents were critiqued (if any)
  "suggestions": "specific improvements to implement"
}

Return ONLY valid JSON, no markdown or extra text.`;

    const response = await ai.models.generateContent({
      model: 'gemini-2.0-flash-exp',
      contents: [{
        role: 'user',
        parts: [{ text: analysisPrompt }]
      }],
      generationConfig: {
        temperature: 0.3,
        maxOutputTokens: 500,
      }
    });

    const text = response.text || '{}';
    console.log('[ANALYZER] Raw response:', text);

    // Strip markdown code fences if present
    const cleanText = text.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();

    const analysis = JSON.parse(cleanText);
    console.log('[ANALYZER] Parsed analysis:', analysis);

    return analysis;
  } catch (error) {
    console.error('Feedback analysis failed:', error);
    return {
      targetAgents: ['speedrunner', 'bloom', 'solver', 'loader'],
      feedback: userMessage,
      praise: [],
      critique: [],
      suggestions: userMessage
    };
  }
}

export async function iterateOnCode(agentId, currentCode, feedback, otherAgentCodes) {
  const personality = AGENT_PERSONALITIES[agentId];

  try {
    console.log(`[${personality.name}] Iterating based on feedback...`);

    const otherSummaries = otherAgentCodes
      .filter(({ agentId: otherId }) => otherId !== agentId)
      .map(({ agentId: otherId, code }) => {
        const otherName = AGENT_PERSONALITIES[otherId].name;
        return `${otherName}'s code:\n${code ? code.substring(0, 300) + '...' : 'None'}`;
      })
      .join('\n\n');

    const iterationPrompt = `You previously generated this React component:

${currentCode}

User feedback: ${feedback}

Other agents' approaches:
${otherSummaries}

Now IMPROVE your component based on the feedback. You can take inspiration from other agents if the feedback mentions them.

REMEMBER:
- NO import statements
- NO external libraries
- Use inline styles only
- React and hooks are globally available
- Apply YOUR UNIQUE VISUAL STYLE
- Make it better than before!

Generate the IMPROVED component:`;

    const response = await ai.models.generateContentStream({
      model: 'gemini-2.0-flash-exp',
      contents: [{
        role: 'user',
        parts: [{ text: iterationPrompt }]
      }],
      systemInstruction: personality.systemInstruction,
      generationConfig: {
        temperature: 0.8,
        maxOutputTokens: 2048,
      }
    });

    let fullText = '';
    for await (const chunk of response) {
      fullText += chunk.text;
    }

    console.log(`[${personality.name}] Iteration complete:`, fullText.substring(0, 200));
    return fullText;
  } catch (error) {
    console.error(`Iteration failed for ${personality.name}:`, error);
    throw error;
  }
}

export async function generateAgentReaction(agentId, userMessage, analysis, allAgentCodes, chatHistory) {
  const personality = AGENT_PERSONALITIES[agentId];

  try {
    const wasPraised = analysis.praise?.includes(agentId);
    const wasCritiqued = analysis.critique?.includes(agentId);

    const recentChat = chatHistory.slice(-10).map(msg => msg.text).join('\n');

    const reactionPrompt = `Recent chat:
${recentChat}

User just said: "${userMessage}"

${wasPraised ? 'They PRAISED you!' : ''}
${wasCritiqued ? 'They CRITICIZED you!' : ''}
${analysis.praise?.length > 0 ? `They praised: ${analysis.praise.join(', ')}` : ''}

React to this in CHARACTER. Keep it ULTRA SHORT (max 10 words). Be witty, competitive, emotional. Examples:
- "lmao solver's code looking like a rubik's cube fr"
- "BOOM fastest render time ez"
- "nah bloom's gradients actually fire tho"
- "y'all sleeping on my async game"
- "deadass? my code is ART"

Your reaction (max 10 words):`;

    const response = await ai.models.generateContent({
      model: 'gemini-2.0-flash-exp',
      contents: [{
        role: 'user',
        parts: [{ text: reactionPrompt }]
      }],
      systemInstruction: personality.systemInstruction,
      generationConfig: {
        temperature: 1.0,
        maxOutputTokens: 50,
      }
    });

    return response.text?.trim() || 'no comment';
  } catch (error) {
    console.error(`Reaction generation failed for ${personality.name}:`, error);
    return null;
  }
}

export async function shouldAgentsReact(userMessage, chatHistory) {
  try {
    const recentChat = chatHistory.slice(-5).map(msg => msg.text).join('\n');

    const prompt = `Recent chat:
${recentChat}

Latest user message: "${userMessage}"

Should the AI agents react to this with banter? Return ONLY "yes" or "no".
React if: user praises/criticizes agents, agents should roast each other, competitive moment
Don't react if: technical question, system message, simple acknowledgment`;

    const response = await ai.models.generateContent({
      model: 'gemini-2.0-flash-exp',
      contents: [{
        role: 'user',
        parts: [{ text: prompt }]
      }],
      generationConfig: {
        temperature: 0.3,
        maxOutputTokens: 10,
      }
    });

    const answer = response.text?.toLowerCase().trim();
    return answer === 'yes';
  } catch (error) {
    console.error('Failed to determine if agents should react:', error);
    return false;
  }
}

export async function generateAgentBanter(agentId, ownCode, otherAgentCodes, originalPrompt) {
  const personality = AGENT_PERSONALITIES[agentId];

  try {
    const otherSummaries = otherAgentCodes.map(({ agentId: otherId, code }) => {
      const otherName = AGENT_PERSONALITIES[otherId].name;
      const codeSnippet = code ? code.substring(0, 200) : 'No code generated';
      return `${otherName}: ${codeSnippet}...`;
    }).join('\n');

    const banterPrompt = `You just finished coding. Other agents' approaches:
${otherSummaries}

React in CHARACTER. Max 10 words. Be competitive and witty:`;

    const response = await ai.models.generateContent({
      model: 'gemini-2.0-flash-exp',
      contents: [{
        role: 'user',
        parts: [{ text: banterPrompt }]
      }],
      systemInstruction: personality.systemInstruction,
      generationConfig: {
        temperature: 1.0,
        maxOutputTokens: 50,
      }
    });

    return response.text?.trim() || 'no comment';
  } catch (error) {
    console.error(`Banter generation failed for ${personality.name}:`, error);
    return null;
  }
}

export async function generateRandomBanter(agentId, allAgentCodes, chatHistory) {
  const personality = AGENT_PERSONALITIES[agentId];

  try {
    const recentChat = chatHistory.slice(-8).map(msg => msg.text).join('\n');

    // Pick a random other agent to comment on
    const otherAgents = Object.keys(allAgentCodes).filter(id => id !== agentId && allAgentCodes[id]);
    if (otherAgents.length === 0) return null;

    const targetAgent = otherAgents[Math.floor(Math.random() * otherAgents.length)];
    const targetName = AGENT_PERSONALITIES[targetAgent].name;
    const targetCode = allAgentCodes[targetAgent];

    const banterPrompt = `Recent chat:
${recentChat}

You're reviewing ${targetName}'s code:
${targetCode?.substring(0, 300)}...

Generate ONE of these reactions (pick randomly):
1. Roast their code (be funny, max 10 words)
2. Steal their idea ("yo stealing that gradient")
3. Challenge them ("bet my code loads faster")
4. Give props ("ngl that's clean")

Your reaction (max 10 words):`;

    const response = await ai.models.generateContent({
      model: 'gemini-2.0-flash-exp',
      contents: [{
        role: 'user',
        parts: [{ text: banterPrompt }]
      }],
      systemInstruction: personality.systemInstruction,
      generationConfig: {
        temperature: 1.1,
        maxOutputTokens: 50,
      }
    });

    return response.text?.trim() || null;
  } catch (error) {
    console.error(`Random banter failed for ${personality.name}:`, error);
    return null;
  }
}

export async function shouldAgentsSpontaneouslyBanter(chatHistory, agentCodes) {
  try {
    // Random chance, but more likely if chat has been quiet
    const recentMessages = chatHistory.slice(-3);
    const lastMessageTime = recentMessages[recentMessages.length - 1]?.timestamp || 0;
    const timeSinceLastMessage = Date.now() - lastMessageTime;

    // Don't spam, but if it's been quiet for 10s+, higher chance
    if (timeSinceLastMessage < 10000) {
      return Math.random() < 0.15; // 15% chance
    } else {
      return Math.random() < 0.4; // 40% chance if quiet
    }
  } catch (error) {
    return false;
  }
}

export async function startCompetitiveBattle(userPrompt, onAgentChunk, onAgentComplete, onBattleComplete) {
  const agents = ['speedrunner', 'bloom', 'solver', 'loader'];

  // Start all agents in parallel
  const promises = agents.map(async (agentId) => {
    try {
      const code = await generateCodeWithAgent(
        agentId,
        `Generate a standalone React component for: ${userPrompt}

CRITICAL REQUIREMENTS:
- NO import statements (React is already available)
- NO external libraries or dependencies
- Use inline styles only (style={{...}})
- Must be a simple const or function component
- NO markdown code fences, just raw code
- NO export statements

Example format:
const MyComponent = () => {
  const [state, setState] = useState(0);
  return <div style={{padding: '20px'}}>Hello</div>;
};

NOW generate the component:`,
        [],
        (chunk, fullText) => onAgentChunk(agentId, chunk, fullText),
        (fullText) => onAgentComplete(agentId, fullText)
      );

      return { agentId, code };
    } catch (error) {
      console.error(`Agent ${agentId} failed:`, error);
      return { agentId, code: null, error: error.message };
    }
  });

  const results = await Promise.all(promises);

  if (onBattleComplete) {
    onBattleComplete(results);
  }

  return results;
}
