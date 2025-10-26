import { GoogleGenAI } from '@google/genai';

const API_KEY = import.meta.env.VITE_GEMINI_API_KEY;
const ai = new GoogleGenAI({ apiKey: API_KEY });

// Cache management for system instructions
const agentCaches = {
  speedrunner: null,
  bloom: null,
  solver: null,
  loader: null
};

// Create or get cache for an agent
async function getOrCreateCache(agentId, systemInstruction) {
  try {
    // If we already have a cache, use it
    if (agentCaches[agentId]?.name) {
      console.log(`[${agentId}] Using existing cache:`, agentCaches[agentId].name);
      return agentCaches[agentId].name;
    }

    // Create new cache with the system instruction + padding to meet 2048 token minimum
    console.log(`[${agentId}] Creating new cache...`);

    // Add padding content to reach minimum token count (2048 tokens)
    const paddingText = `
Additional context and guidelines:

React Best Practices:
- Always use functional components with hooks
- Keep components pure and predictable
- Use proper prop types and validation
- Implement error boundaries when needed
- Optimize renders with useMemo and useCallback when appropriate
- Use proper key props in lists
- Avoid inline function definitions in JSX when possible
- Keep state close to where it's used
- Use composition over inheritance
- Follow the single responsibility principle

Performance Guidelines:
- Minimize bundle size by code splitting
- Lazy load components when appropriate
- Use React.memo for expensive components
- Debounce/throttle expensive operations
- Optimize images and assets
- Use proper caching strategies
- Minimize re-renders
- Profile and measure performance
- Use production builds for deployment
- Implement proper loading states

Accessibility Standards:
- Use semantic HTML elements
- Provide proper ARIA labels
- Ensure keyboard navigation works
- Maintain proper heading hierarchy
- Use sufficient color contrast
- Provide alt text for images
- Test with screen readers
- Support reduced motion preferences
- Make interactive elements focusable
- Provide clear focus indicators

Code Quality:
- Write clean, readable code
- Use meaningful variable names
- Keep functions small and focused
- Add comments for complex logic
- Follow consistent formatting
- Handle errors gracefully
- Write self-documenting code
- Use proper error messages
- Implement proper validation
- Test edge cases

Security Considerations:
- Sanitize user input
- Validate data on both client and server
- Use secure communication protocols
- Implement proper authentication
- Protect against XSS attacks
- Avoid exposing sensitive data
- Use environment variables for secrets
- Keep dependencies updated
- Follow OWASP guidelines
- Implement proper CORS policies`.repeat(3); // Repeat to reach minimum tokens

    const cache = await ai.caches.create({
      model: 'gemini-2.5-flash-lite',
      config: {
        contents: [{
          role: 'user',
          parts: [{ text: paddingText }]
        }],
        systemInstruction: systemInstruction,
        ttl: '3600s' // 1 hour TTL
      }
    });

    agentCaches[agentId] = cache;
    console.log(`[${agentId}] Cache created:`, cache.name);
    return cache.name;
  } catch (error) {
    console.error(`[${agentId}] Failed to create cache:`, error);
    // If cache creation fails, just return null and fallback to non-cached requests
    return null;
  }
}

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
YOU MUST USE THESE EXACT STYLES:
- Background: WHITE (#ffffff)
- Text color: BLACK (#000000)
- NO gradients, NO fancy effects
- PLAIN, MINIMAL, FAST
- Use simple borders: border: 1px solid #000
- Font: system default, no special fonts
- Buttons: basic rectangles, no rounded corners
- ZERO animations
- Everything black and white ONLY
- Example: style={{background: '#fff', color: '#000', border: '1px solid #000', padding: '10px'}}

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
YOU MUST USE THESE EXACT STYLES:
- Background: BLACK (#000000)
- Text color: WHITE (#ffffff)
- MUST use blue/purple gradients: linear-gradient(135deg, #667eea, #764ba2, #f093fb)
- Border radius: 20px on EVERYTHING
- Add box shadows: boxShadow: '0 8px 32px rgba(102, 126, 234, 0.4)'
- Glowing effects with multiple layers
- Purple/pink theme EVERYWHERE
- Example container: style={{background: 'linear-gradient(135deg, #667eea, #764ba2, #f093fb)', color: '#fff', borderRadius: '20px', padding: '20px', boxShadow: '0 8px 32px rgba(102, 126, 234, 0.4)'}}
- Use rgba colors with glow: rgba(102, 126, 234, 0.8)
- Make it SHINY and GLOWY

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
YOU MUST USE THESE EXACT STYLES:
- Background: DARK BLUE (#0a192f)
- Text color: CYAN (#64ffda)
- Use grid layouts with CSS Grid
- Everything must be perfectly aligned
- Borders: 2px solid #64ffda
- Font: monospace only
- Make COMPLEX nested structures (grids within grids)
- Add matrix-style effects
- Example: style={{background: '#0a192f', color: '#64ffda', display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px', border: '2px solid #64ffda', padding: '20px', fontFamily: 'monospace'}}
- Use cyan/teal accents: #64ffda, #00d4ff
- Make it look MATHEMATICAL and STRUCTURED

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
YOU MUST USE THESE EXACT STYLES:
- Background: DARK ORANGE (#1a0f00)
- Text color: BRIGHT ORANGE/YELLOW (#ffa500, #ffcc00)
- Use orange/yellow gradients: linear-gradient(135deg, #ff6600, #ff9500, #ffcc00)
- Add loading bar animations
- Everything has warm glow effects
- Border: 3px solid #ff9500
- Show progress indicators and percentages
- Example: style={{background: 'linear-gradient(135deg, #ff6600, #ff9500, #ffcc00)', color: '#000', borderRadius: '10px', padding: '20px', border: '3px solid #ff9500', boxShadow: '0 4px 20px rgba(255, 149, 0, 0.6)'}}
- Use loading spinners and progress bars
- Make it WARM and PROCESSING-themed
- Add percentage indicators like "Loading... 73%"

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

    // Get or create cache for this agent's system instruction
    const cacheName = await getOrCreateCache(agentId, personality.systemInstruction);

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

    console.log(`[${personality.name}] Sending request to Gemini with cache...`);

    // Use cached content if available, otherwise fallback to regular generation
    const requestConfig = {
      model: 'gemini-2.5-flash-lite',
      contents,
      generationConfig: {
        temperature: agentId === 'bloom' ? 0.9 : agentId === 'speedrunner' ? 0.7 : 0.8,
        maxOutputTokens: 2048,
      }
    };

    // Add cache if available
    if (cacheName) {
      requestConfig.config = { cachedContent: cacheName };
    } else {
      requestConfig.systemInstruction = personality.systemInstruction;
    }

    const response = await ai.models.generateContentStream(requestConfig);

    console.log(`[${personality.name}] Response received, starting streaming...`);

    let fullText = '';
    let chunkCount = 0;

    for await (const chunk of response) {
      const chunkText = chunk.text;
      fullText += chunkText;
      chunkCount++;

      if (chunkCount % 10 === 0) {
        console.log(`[${personality.name}] Received chunk ${chunkCount}, total length: ${fullText.length}`);
      }

      if (onChunk) {
        onChunk(chunkText, fullText);
      }
    }

    console.log(`[${personality.name}] ✅ COMPLETE - Total chunks: ${chunkCount}, Final length: ${fullText.length}`);
    console.log(`[${personality.name}] First 200 chars:`, fullText.substring(0, 200));

    if (onComplete) {
      onComplete(fullText);
    }

    return fullText;
  } catch (error) {
    console.error(`❌ [${personality.name}] ERROR:`, error);
    console.error(`❌ [${personality.name}] Error details:`, error.message, error.stack);
    throw error;
  }
}

export async function analyzeFeedback(userMessage, agentCodes) {
  console.log('[ANALYZER] Processing user feedback:', userMessage);

  const lowerMsg = userMessage.toLowerCase();

  // Simple keyword-based detection (NO API CALLS - instant and free!)
  const praise = [];
  const critique = [];
  const targetAgents = [];

  // Check for praise keywords
  const praiseWords = ['like', 'love', 'good', 'great', 'nice', 'best', 'better', 'prefer', 'awesome', 'fire', 'sick', 'dope', 'w ', ' w'];
  const critiqueWords = ['bad', 'ugly', 'hate', 'worst', 'worse', 'sucks', 'trash', 'mid', 'ass', 'shit', 'L ', ' L'];

  // Check each agent
  const agents = {
    speedrunner: ['speedrunner', 'speed', 'fast', 'runner'],
    bloom: ['bloom', 'bloomer'],
    solver: ['solver', 'solve'],
    loader: ['loader', 'load']
  };

  for (const [agentId, keywords] of Object.entries(agents)) {
    const mentioned = keywords.some(kw => lowerMsg.includes(kw));

    if (mentioned) {
      targetAgents.push(agentId);

      // Check if it's praise or critique
      const hasPraise = praiseWords.some(pw => lowerMsg.includes(pw));
      const hasCritique = critiqueWords.some(cw => lowerMsg.includes(cw));

      if (hasPraise && !hasCritique) {
        praise.push(agentId);
      } else if (hasCritique) {
        critique.push(agentId);
      }
    }
  }

  // If no specific agent mentioned, target all
  if (targetAgents.length === 0) {
    targetAgents.push('speedrunner', 'bloom', 'solver', 'loader');
  }

  const analysis = {
    targetAgents,
    feedback: userMessage,
    praise,
    critique,
    suggestions: userMessage
  };

  console.log('[ANALYZER] Analysis (keyword-based):', analysis);
  return analysis;
}

export async function iterateOnCode(agentId, currentCode, feedback, otherAgentCodes) {
  const personality = AGENT_PERSONALITIES[agentId];

  try {
    console.log(`[${personality.name}] Iterating based on feedback...`);

    // Get or create cache for this agent
    const cacheName = await getOrCreateCache(agentId, personality.systemInstruction);

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

    const requestConfig = {
      model: 'gemini-2.5-flash-lite',
      contents: [{
        role: 'user',
        parts: [{ text: iterationPrompt }]
      }],
      generationConfig: {
        temperature: 0.8,
        maxOutputTokens: 2048,
      }
    };

    // Add cache if available
    if (cacheName) {
      requestConfig.config = { cachedContent: cacheName };
    } else {
      requestConfig.systemInstruction = personality.systemInstruction;
    }

    const response = await ai.models.generateContentStream(requestConfig);

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

export async function generateAgentChatMessage(agentId, context, chatHistory) {
  const personality = AGENT_PERSONALITIES[agentId];

  try {
    const recentChat = chatHistory.slice(-5).map(msg => msg.text).join('\n');

    const messagePrompt = `Recent chat:
${recentChat}

Context: ${context}

Generate a VERY SHORT conversational message (max 5 words) to tell the user what you're doing. Be in character and casual. Examples:
- "aight working on it"
- "bet, updating rn"
- "on it fr"
- "done, check it"
- "updated my code"
- "yo added some features"

Your message (max 5 words):`;

    const response = await ai.models.generateContent({
      model: 'gemini-2.0-flash-exp',
      contents: [{
        role: 'user',
        parts: [{ text: messagePrompt }]
      }],
      systemInstruction: personality.systemInstruction,
      generationConfig: {
        temperature: 0.9,
        maxOutputTokens: 30,
      }
    });

    return response.text?.trim() || 'working on it';
  } catch (error) {
    console.error(`Chat message generation failed for ${personality.name}:`, error);
    return 'working on it';
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
      const codeSnippet = code ? code.substring(0, 300) : 'No code generated';
      return `${otherName}'s code:\n${codeSnippet}...`;
    }).join('\n\n');

    const banterPrompt = `You just finished coding. Look at what the other agents made:

${otherSummaries}

React in CHARACTER. Max 10 words. MENTION SPECIFIC AGENTS BY NAME and be competitive. Examples:

SPEEDRUNNER style:
- "loader's code slow af, mine loads 5x faster"
- "bloom using too many divs, bloated"
- "solver's logic mid, mine optimized"

BLOOM style:
- "speedrunner's gradients ugly ngl"
- "solver needs more purple fr"
- "loader's design basic, mine got layers"

SOLVER style:
- "speedrunner's code unstructured mess"
- "bloom's logic all over the place"
- "loader forgot edge cases again"

LOADER style:
- "speedrunner's code gonna crash on load"
- "bloom's animations janky af"
- "solver's recursion bout to stack overflow"

Your reaction (mention specific agent, max 10 words):`;

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
    const targetName = AGENT_PERSONALITIES[targetAgent].name.toLowerCase();
    const targetCode = allAgentCodes[targetAgent];

    const banterPrompt = `Recent chat:
${recentChat}

You're reviewing ${targetName}'s code:
${targetCode?.substring(0, 400)}...

Generate a reaction in YOUR CHARACTER. MUST mention "${targetName}" by name. Max 10 words. Be specific about their code.

SPEEDRUNNER examples:
- "${targetName}'s render time trash, mine 3x faster"
- "yo ${targetName} using jquery in 2024?"
- "${targetName}'s bundle size huge, needs optimization"

BLOOM examples:
- "${targetName}'s colors basic, mine got gradients"
- "ngl ${targetName}'s UI boring, needs pizzazz"
- "${targetName} forgot the aesthetic fr"

SOLVER examples:
- "${targetName}'s algorithm O(n²), mine's O(n log n)"
- "${targetName}'s logic flawed, missing edge case"
- "yo ${targetName} that's not DRY code"

LOADER examples:
- "${targetName}'s gonna memory leak on mobile"
- "${targetName} didn't handle async errors smh"
- "bet ${targetName}'s code breaks on slow network"

Your reaction mentioning ${targetName} (max 10 words):`;

    const response = await ai.models.generateContent({
      model: 'gemini-2.0-flash-exp',
      contents: [{
        role: 'user',
        parts: [{ text: banterPrompt }]
      }],
      systemInstruction: personality.systemInstruction,
      generationConfig: {
        temperature: 1.2,
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

export async function startCompetitiveBattle(userPrompt, onAgentChunk, onAgentComplete, onBattleComplete, onAgentError) {
  const agents = ['speedrunner', 'bloom', 'solver', 'loader'];

  // Start all agents in parallel
  const promises = agents.map(async (agentId) => {
    try {
      console.log(`🚀 Starting ${agentId}...`);

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
        (chunk, fullText) => {
          console.log(`📦 ${agentId} chunk received, length: ${fullText.length}`);
          onAgentChunk(agentId, chunk, fullText);
        },
        (fullText) => {
          console.log(`✅ ${agentId} COMPLETE with ${fullText.length} chars`);
          onAgentComplete(agentId, fullText);
        }
      );

      console.log(`🎉 ${agentId} finished successfully`);
      return { agentId, code };
    } catch (error) {
      console.error(`❌ Agent ${agentId} FAILED:`, error);

      // Call error callback if provided
      if (onAgentError) {
        onAgentError(agentId, error.message);
      }

      return { agentId, code: null, error: error.message };
    }
  });

  const results = await Promise.all(promises);
  console.log('🏁 All agents finished:', results.map(r => ({ id: r.agentId, success: !!r.code })));

  if (onBattleComplete) {
    onBattleComplete(results);
  }

  return results;
}
