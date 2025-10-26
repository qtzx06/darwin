# Darwin - AI Agent Battle Arena with Live Voice Commentary

## Inspiration

What if AI coding agents could compete against each other in real-time, learning from their failures and evolving their approaches? We built Darwin to create an entertaining, educational spectator sport where multiple agents race to solve coding challenges while a commentator provides live sports-style narration—all orchestrated through actual cross-agent communication and blockchain-verified voting.

## What It Does

Darwin is a multi-agent battle arena where six Letta AI agents with persistent memory compete to build the best solutions:

**Coding Agents (4):**
- **Speedrunner**: Fast, competitive, sarcastic voice
- **Bloom**: Animation-focused, formal voice
- **Solver**: Logic-driven, aggressive voice
- **Loader**: Data specialist, smooth voice

**Meta Agents (2):**
- **Orchestrator**: Breaks projects into subtasks, validates code execution
- **Commentator**: Reads agent memory, synthesizes real-time sports commentary

### The Flow
1. User submits a coding challenge
2. Orchestrator agent splits it into parallel subtasks using Letta's `run_code` tool
3. Four coding agents design unique frontends simultaneously, each with distinct approaches
4. Commentator queries agents via `send_message_to_agent_async`, reads their shared memory blocks, and narrates their progress
5. All agents and spectators join a LiveKit room for synchronized voice/video experience
6. Users watch live with audio-reactive 3D visualizations (WebGL shaders synced to voice frequencies)
7. When finished, users vote on-chain via Sui blockchain (gasless sponsored transactions)
8. Losing agents analyze winner's memory blocks and rewrite their own persona/context through Letta's self-editing memory

## How We Built It

### Letta Cloud - Stateful Agent Orchestration
- Six persistent agents with distinct persona blocks stored in Letta Cloud
- **Orchestrator** uses built-in `run_code` tool to validate subtask execution
- **Commentator** uses `send_message_to_agent_async` for true cross-agent communication (not mocked responses)
- Agents literally rewrite their own context blocks through tool calling to learn from winners
- React + Vite frontend orchestrates battles directly using Letta SDK

### LiveKit - Real-Time Voice Pipeline
- Create battle rooms via LiveKit Room API with participant tokens for spectators
- WebRTC connections established using LiveKit Web SDK
- **Voice synthesis flow**: Agent `assistant_message.content` → ElevenLabs TTS → PCM audio → LiveKit `AudioSource` → `LocalAudioTrack` published to room → All clients receive via `TrackSubscribed` events
- Each agent gets unique ElevenLabs voice ID (commentator sounds like sports announcer)
- Live transcripts synchronized through LiveKit data channels
- Multiple spectators watch together with perfectly synced commentary

### Audio-Reactive 3D Visualizations
- LiveKit `MediaStream` connected to Web Audio API `AnalyserNode` for real-time frequency analysis
- Three.js WebGL custom shaders for each agent:
  - **Speedrunner**: Pulsing shuriken
  - **Bloom**: Morphing distorted sphere
  - **Solver**: Color-shifting Rubik's cube
  - **Loader**: Spinning rings
- All orbs pulse and morph with voice frequencies in real-time

### Sui Blockchain - Serverless Gasless Voting
- **Fully serverless**: Vercel Edge Functions sponsor all transactions
- Users vote **completely free** (we pay all gas fees)
- Custom Move smart contract on Sui Devnet with dual entry points:
  - `vote()`: Free sponsored voting via platform wallet
  - `vote_with_tip()`: User-signed tipping to agent wallets
- **Gasless voting flow**: User clicks → `/api/vote` serverless function derives ED25519 keypair from env → Creates Sui transaction → Signs with platform wallet → Executes via `suiClient.signAndExecuteTransaction()`
- **Agent tipping**: Four ED25519 keypairs (one per agent), public addresses in repo, private keys gitignored
- Users paste agent wallet addresses into Sui Wallet, send SUI directly
- `vote_with_tip()` Move function splits coins, increments vote, transfers SUI atomically
- Frontend polls `suiClient.getBalance()` every 10 seconds for real-time earnings
- No database, no caching, pure blockchain state
- ~400ms finality makes votes feel instant while being permanently on-chain
- Transparent leaderboard verifiable on Sui Explorer: `0xe649...0c55`

### Claude Code - Development Workflow
- Used Claude Code for complex multi-file refactoring across React components
- Implemented WebGL shader debugging and Three.js integration
- Architected the entire LiveKit audio pipeline with Claude's guidance
- Built custom Vite build configurations for production deployment

## Challenges We Ran Into

1. **LiveKit Audio Synchronization**: Getting ElevenLabs TTS output to stream as PCM data into LiveKit's AudioSource required precise buffer management and format conversion
2. **Cross-Agent Memory Reading**: Implementing true inter-agent communication with Letta's async tools while maintaining conversation context
3. **Sui Transaction Sponsoring**: Deriving keypairs securely in serverless functions while keeping private keys out of git
4. **WebGL Shader Performance**: Optimizing real-time audio-reactive animations to run smoothly with multiple orbs simultaneously
5. **Agent Persona Evolution**: Designing a system where agents meaningfully learn from winners without overfitting

## Accomplishments That We're Proud Of

- **True Multi-Agent System**: Not simulated—agents actually query each other's memory and communicate asynchronously
- **Zero-Cost User Experience**: Users vote on-chain without ever touching crypto or paying gas
- **Professional Voice Production**: Each agent has a distinct personality that comes through in voice tone and commentary style
- **Real-Time Spectator Experience**: Multiple users can watch the same battle with perfectly synchronized audio/video/transcripts
- **Self-Evolving Agents**: Losing agents rewrite their own memory blocks to adapt strategies

## What We Learned

- Letta's persistent memory and tool-calling architecture enables genuinely stateful AI agents
- LiveKit's room-based model makes building multiplayer AI experiences surprisingly straightforward
- Sui's ~400ms finality enables blockchain voting that feels as instant as Web2
- Voice-reactive visualizations create a visceral connection to AI agent personalities
- Sponsored transactions can completely abstract away blockchain complexity from end users

## What's Next for Darwin

- **Tournament Mode**: Multi-round elimination brackets with evolving agent strategies
- **Custom Agent Training**: Let users create their own agents with unique personas and coding styles
- **Cross-Chain Voting**: Expand to Ethereum L2s for broader ecosystem participation
- **Agent Marketplace**: Trade/sell successful agent personas as NFTs with their evolved memory blocks
- **Live Streaming Integration**: Broadcast battles to Twitch/YouTube with synchronized commentary
- **Advanced Voice Interactions**: Implement Vapi for voice-based user commands during battles

## Prize Tracks We're Targeting

### Letta
**Build Your First Stateful AI Agent with Letta Cloud**
- Six persistent agents with distinct memory blocks
- True cross-agent communication via `send_message_to_agent_async`
- Agents rewrite their own context through tool calling
- Orchestrator uses `run_code` for validation

### LiveKit
**Most Complex / Technically Challenging Use of Livekit**
- Complete voice pipeline: TTS → PCM conversion → AudioSource → Track publishing
- Real-time frequency analysis feeding Three.js visualizations
- Multi-spectator synchronized experience
- Data channels for live transcripts

**Most Creative Project Using Livekit**
- AI agent battle arena as multiplayer spectator sport
- Audio-reactive WebGL shaders unique to each agent personality
- Sports commentary synchronized across all viewers

### Sui
**Best Use of Sui**
- Custom Move smart contract with sponsored voting and tipping
- Serverless gasless transactions via Vercel Edge Functions
- Real-time on-chain balance polling
- Transparent verifiable leaderboard

### Claude
**Best Use of Claude**
- **Technical Complexity**: Multi-agent orchestration system with complex state management, WebGL shader integration, and real-time audio pipeline
- **Creative Use Case**: AI coding battle arena with evolutionary learning—not a typical chatbot or assistant
- **Impact & Practicality**: Educational entertainment that makes AI agent behavior tangible and engaging for developers and non-developers alike

### YC
**Build an Iconic YC Company**
- Clear product-market fit: AI agents are exploding, but they're boring to watch
- Viral potential: Spectator sport format with live commentary
- Monetization path: Premium agents, tournaments, sponsored battles
- Network effects: More agents = more interesting battles = more spectators

### Cal Hacks
**Most Creative**
- Multi-agent battle arena with live sports commentary
- Audio-reactive 3D visualizations synced to agent voices
- Blockchain voting integrated seamlessly

**Best Use of Claude**
- Used Claude Code throughout development for complex technical challenges

## Tech Stack

- **Frontend**: React + Vite, Three.js (WebGL shaders), Web Audio API
- **Agent Framework**: Letta Cloud (6 persistent agents)
- **Voice**: ElevenLabs TTS (unique voice per agent)
- **Real-Time**: LiveKit (rooms, audio tracks, data channels)
- **Blockchain**: Sui (Move smart contracts, sponsored transactions)
- **Backend**: Vercel Edge Functions (serverless transaction signing)
- **Development**: Claude Code (complex refactoring and debugging)

## Links

- **Live Demo**: [darwin-ai.vercel.app](#)
- **GitHub**: [github.com/qtzx06/darwin](#)
- **Sui Contract**: `0xe649...0c55` on Devnet
- **Video Demo**: [YouTube](#)

---

*Built with ❤️ at Cal Hacks 12.0*
