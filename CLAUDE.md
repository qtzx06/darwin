# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Darwin is a React + Vite application featuring a multi-agent AI coding battle system. The landing page includes advanced visual effects with FBO particle animations, liquid glass morphism, and interactive elements. The main orchestration page showcases 4 AI agents (Speedrunner, Bloom, Solver, Loader) competing to build React components based on user prompts, with live voice commentary.

## Development Commands

- `npm run dev` - Start development server with HMR
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint

## Architecture

### Two-Page Application

1. **Landing Page** (`App.jsx`) - Search interface with visual effects
2. **Orchestration Page** (`Orchestration.jsx`) - AI agent battle interface with live coding

### Landing Page Components

**WebglNoise** (`src/components/WebglNoise.jsx`)
- Three.js particle orb animation for loading screen
- Uses NormalBlending with radial gradient texture (white → light pink → medium pink → red)
- IcosahedronGeometry with animated particles

**Wisp Animation** (`/public/wisp/`)
- Three.js-based FBO particle system background
- Implements zoom-in animation triggered by search submission
- Listens for `postMessage` events to trigger zoom effect

**GlassSearchBar** (`src/components/GlassSearchBar.jsx`)
- Liquid glass morphism effect using SVG filters (`#glass-distortion`)
- Three-layer rendering: glass-filter, glass-overlay, glass-specular
- Integrated with Framer Motion for smooth transitions
- Suggestions: "landing page for cal hacks", "cool 404 error page", "beautifully designed coming soon page"

**Dither** (`src/components/Dither.jsx`)
- WebGL shader-based dithered wave animation for side panels
- Left and right panels have opposite animation directions
- Post-processing with custom RetroEffect using Bayer matrix dithering

**DevpostCard** (`src/components/DevpostCard.jsx`)
- Footer with links to GitHub (https://github.com/qtzx06/darwin) and Devpost (https://devpost.com/software/darwin-w6fez0)
- Easter egg: clicking logo shows "*quack!*" text

### Orchestration Page Components

**Agent System** (`src/components/AgentCard.jsx`)
- 4 AI agents: Speedrunner, Bloom, Solver, Loader
- Each generates React code using Gemini 2.5 Flash
- Agents have distinct personalities and coding approaches
- Code displays with typing animation
- Live transcript showing agent thoughts
- Glass card styling with transparent backgrounds (0.4 opacity for cards, 0.5 for transcripts)

**Commentator** (`src/components/Commentator.jsx`)
- Voice AI using Gemini Native Audio (gemini-2.5-flash-native-audio-preview-09-2025)
- Charon voice for deep male commentary
- React to agent banter and user input
- Two-stage system: Text observation → Natural voice reaction
- Mute/unmute voice output

**Voice Transcription** (`src/services/geminiAudioService.js`)
- Uses Gemini API for audio transcription (not Live API)
- MediaRecorder collects audio chunks → batch transcription
- Converts casual speech to actionable instructions
- Shows in chat as "[MANAGER] Boss said: {instruction}"

**Manager Feedback System**
- Auto-generates feedback every 4 agent banter messages
- Hardcoded messages like "make it blue", "speedrunner optimize this", etc.
- Appears as [MANAGER] in chat (blue color #9dc4ff)
- Triggers agent code iterations

**Chat System** (`src/components/ChatInput.jsx`)
- Message types: user, agent, manager, voice
- Color coding: [MANAGER] (blue), Boss said (from voice), agent messages (purple)
- All user/manager messages trigger agent iterations via `handleUserMessage`

**Preview System** (`src/components/CodeRenderer.jsx`)
- Live preview of agent-generated code
- ErrorBoundary catches runtime errors
- Renders in iframe for isolation

**Transcript Panel** (`src/components/TranscriptPanel.jsx`)
- Shows voice transcriptions: [YOU] for user, [MANAGER] for commentator
- Mic button to toggle recording
- Scrollable with hidden scrollbar

### Gemini Integration

**geminiService.js**
- Agent code generation using Gemini 2.5 Flash
- System prompts define agent personalities
- Agents know about window.* globals (Motion, Lucide, ReactSpring, THREE, gsap, Chart)
- `analyzeFeedback` - keyword-based analysis of user feedback
- `iterateOnCode` - agents improve code based on feedback

**geminiAudioService.js**
- Gemini Native Audio Live API for voice output
- Audio chunk queue for sequential playback
- PCM audio processing (24kHz output)
- Batch audio transcription using generateContent API

**commentatorGeminiService.js**
- Generates short observations (max 15 words) of chat events
- Understands agent names and Boss
- Converts events into natural commentary for voice AI

### State Management

**Orchestration.jsx** manages:
- `agentCode` - Generated code for each agent
- `agentStatus` - Status messages (working, done, etc.)
- `chatMessages` - All chat messages with types
- `transcripts` - Voice transcription history
- `isBattleRunning` - Whether agents are generating
- `expandedAgent` - Which agent card is expanded
- `processedManagerMessages` - Tracks processed messages to prevent duplicates

### Message Flow

1. **User types in chat** → Shows as [MANAGER] → Triggers iteration
2. **User speaks via mic** → Gemini transcribes → Shows as "[MANAGER] Boss said: {instruction}" → Triggers iteration
3. **Manager auto-feedback** (every 4 banter) → Shows as [MANAGER] → Triggers iteration
4. **Agent iteration** → `analyzeFeedback` analyzes → Targets specific agents → `iterateOnCode` improves code

### Styling Approach

- **Fonts**: BBH Sans Bartle for headers, Geist Mono for all UI text
- **Color Scheme**:
  - Pink/coral accents (#f0b0d0, #FF69B4)
  - Manager messages: blue (#9dc4ff)
  - Agent messages: purple (#a78bfa)
  - User messages: pink (#f0b0d0)
- **Glass Effects**:
  - Transparent black backgrounds (0.4-0.5 opacity)
  - backdrop-filter: blur()
  - Three-layer rendering (filter, overlay, specular)
- **Animations**: Framer Motion for transitions, GSAP for 3D effects

### Navigation

1. Landing page → User enters query → Battle starts
2. Orchestration page → Click "DARWIN //" header to return to landing page
3. URL format: `#orchestration?query={user_query}`

### Agent Banter System

- Autonomous banter between agents every 6-9 seconds after battle complete
- Agents roast each other's code
- Personality-based banter (e.g., Speedrunner brags about speed, Bloom focuses on aesthetics)

### Important Implementation Details

**useCallback Dependencies**
- `handleUserMessage` must include `agentCode`, `setChatMessages`, `setAgentStatus`, `setAgentCode` in dependencies to see latest state

**Message Processing**
- Use `processedManagerMessages` ref to track which messages have been processed
- Prevents infinite loops and duplicate iterations
- Each manager/voice message has unique `messageId` or `timestamp`

**Audio Blending**
- Use `NormalBlending` for particles (not AdditiveBlending which washes to white)
- Radial gradients in particle textures for multi-color effects

**Error Handling**
- ErrorBoundary in CodeRenderer catches CSS rules access errors
- Graceful fallbacks for Gemini API failures

**Agent Iteration**
- Only iterates if agent has code: `if (agentCode[targetAgentId])`
- Sequential processing with 2s delays to avoid rate limits
- Shows working messages during iteration

**DARWIN Logo**
- Outline text with transparent fill
- Subtle glow: `text-shadow: 0 0 15px rgba(255, 255, 255, 0.15), 0 0 30px rgba(240, 176, 208, 0.1)`
- Drop shadow for depth

### Mobile Responsiveness

- Title font reduces from 3rem to 2rem
- Side dither panels hidden on mobile
- Glass cards adapt layout
- Touch-friendly button sizes

## Common Tasks

### Adding New Manager Messages
Update the `managerMessages` array in the banter effect (Orchestration.jsx ~lines 185-206)

### Changing Voice
Modify `voiceName` in `geminiAudioService.js` createSession config (currently "Charon")

### Adjusting Glass Transparency
Modify `--bg-color` variables in component CSS files:
- AgentCard.css: 0.4 for cards, 0.5 for transcripts
- ChatInput.css: 0.5
- TranscriptPanel.css: 0.5
- PreviewCard.css: 0.5

### Agent Personalities
Defined in geminiService.js system prompts:
- Speedrunner: Fast, competitive, efficiency-obsessed
- Bloom: Creative, scattered, loves animations/visuals
- Solver: Logical, methodical, algorithm-focused
- Loader: Patient, steady, handles async/data

### Debugging Voice Issues
- Check console for `[GeminiAudio]` logs
- Verify `onUserTranscript` callback is set
- Ensure AudioContext is resumed (requires user gesture)
- Check if session is active: `this.isSessionActive`
