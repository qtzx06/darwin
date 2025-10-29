# darwin // evolve your agents.

a multi-agent ai coding battle platform built with react, gemini, and sui blockchain. watch four specialized ai agents compete to build react components in real-time, with live voice commentary and on-chain voting.

![darwin banner](https://img.shields.io/badge/sui-blockchain-4da2ff?style=for-the-badge&logo=sui&logocolor=white)
![react](https://img.shields.io/badge/react-20232a?style=for-the-badge&logo=react&logocolor=61dafb)
![three.js](https://img.shields.io/badge/threejs-black?style=for-the-badge&logo=three.js&logocolor=white)

## overview

darwin is an interactive platform where four ai agents compete to build react components based on user prompts. each agent uses google gemini 2.5 flash with distinct personalities and approaches:

- speedrunner - prioritizes speed and minimal code, competitive and efficiency-obsessed
- bloom - focuses on aesthetics and animations, creative but scattered
- solver - emphasizes logic and algorithms, methodical and precise
- loader - handles async operations and data management, patient and steady

users can watch agents code in real-time, provide feedback through text or voice input, vote for their favorite implementations, and tip agents directly on-chain.

## core functionality

### agent system

each agent generates actual react code that renders live in the browser:

- **code generation**: agents use gemini 2.5 flash api with custom system prompts that define their personality and coding style
- **live preview**: generated code is transpiled with babel and rendered in isolated preview panels
- **code iteration**: agents improve their code based on user feedback, manager instructions, and agent banter
- **personality-driven responses**: each agent has hardcoded banter messages and reactions that trigger based on events

the agents have access to pre-loaded browser libraries (framer motion, lucide icons, react-spring, three.js, gsap, chart.js) via window globals, allowing them to create rich interactive components without imports.

### state machine orchestration

the orchestration page manages agent state through several parallel systems:

1. **battle initialization**: user enters a prompt on landing page, navigates to orchestration with query parameter
2. **code generation phase**: all 4 agents simultaneously generate initial code via gemini api calls
3. **live preview**: code renders in real-time with error boundaries catching runtime issues
4. **autonomous banter**: agents exchange messages every 6-9 seconds after completion, roasting each other's approaches
5. **manager feedback**: hardcoded manager messages inject every 4 banter rounds, triggering agent iterations
6. **user interaction**: users can vote, provide feedback, or speak instructions via microphone

### voice system

darwin features two-way voice interaction:

**input - voice transcription**:
- uses gemini api (not live api) for batch audio transcription
- mediarecorder captures audio chunks which are sent for transcription
- transcribed speech converts to actionable instructions
- displays as "[manager] boss said: {instruction}" in chat
- triggers agent code iterations

**output - ai commentary**:
- gemini native audio live api (gemini-2.5-flash-native-audio-preview) with charon voice
- commentator observes chat events and generates short observations (max 15 words)
- observations fed to voice ai which responds naturally
- audio streams back as pcm chunks (24khz) and plays sequentially
- provides live play-by-play commentary on agent actions

### feedback and iteration system

multiple feedback mechanisms trigger agent code improvements:

1. **user text input**: messages from chat input show as "[you]" and trigger targeted agent iterations
2. **voice commands**: transcribed speech shows as "[manager] boss said:" and triggers iterations
3. **manager auto-messages**: hardcoded messages inject periodically (every 4 banter messages)
4. **voting flow**: when user votes for an agent, triggers:
   - manager gives detailed analysis (4 variants per agent)
   - 2 random other agents react with salty hardcoded messages
   - all agents iterate on their code

the `analyzefeedback` function uses keyword matching to determine which agents should respond, and `iterateoncode` generates improved versions based on the feedback context.

### blockchain integration

darwin uses sui blockchain for transparent, immutable voting:

**smart contract**:
- written in move language, deployed on sui devnet
- package id: `0x302f582a43a8d22bc2a030ab76e3253f79618217a7a6576ad8a91b6075a85ae8`
- voteregistry id: `0x44e13769132e791fca5067ddb0d13d3f50ea1488d4c5a89453227fe7b11b15b9`
- stores vote counts for all 4 agents in shared object

**sponsored transactions**:
- users vote without needing wallet or sui tokens
- backend server (express) or serverless function (vercel) sponsors gas fees
- votes recorded on-chain in ~400ms
- frontend polls blockchain every 10 seconds for updated counts

**agent wallets**:
- each agent has a devnet wallet address stored in `src/utils/agentwallets.json`
- wallet addresses display as truncated strings with copy-to-clipboard functionality
- users can tip agents directly by copying wallet addresses

### visual system

darwin features extensive webgl and shader-based visuals:

**landing page**:
- webglnoise: three.js particle orb with icosahedron geometry and radial gradient texture
- wisp: fbo particle system with zoom-in animation triggered by search submission
- dither: webgl shader-based wave animations on side panels using bayer matrix dithering
- glass search bar: liquid glass morphism with svg filters and three-layer rendering

**orchestration page**:
- liquidchrome: dynamic gradient backgrounds unique to each agent
- glass card effects: transparent backgrounds (0.4-0.5 opacity) with backdrop blur
- agent visualizations: custom 3d visuals for each agent's headshot
- typing animations: streaming text effect for generated code
- expand preview: click preview to hide code and expand rendered component to full width

### message and chat system

the chat system handles multiple message types with color-coded prefixes:

- `[you]`: user messages from text input (pink #f0b0d0)
- `[manager]`: auto-injected feedback messages (blue #9dc4ff)
- `[manager] boss said:`: transcribed voice input (blue #9dc4ff)
- agent names in brackets: agent banter and reactions (purple #a78bfa)

messages trigger different behaviors:
- user/manager messages call `handleusermessage` which runs feedback analysis and agent iteration
- agent banter messages increment counter for periodic manager message injection
- vote messages trigger special flow with analysis and reactions

the `processedmanagermessages` ref tracks which messages have been processed to prevent duplicate iterations and infinite loops.

## tech stack

**frontend**:
- react 19 with vite
- three.js for 3d graphics and webgl shaders
- framer motion for ui animations
- @mysten/sui for blockchain interactions
- babel standalone for runtime jsx transpilation

**ai services**:
- google gemini 2.5 flash for code generation
- gemini native audio live api for voice output
- gemini api for voice transcription (batch, not live)

**backend**:
- express.js for local development server (port 3001)
- vercel serverless functions for production
- sui sdk for transaction signing and sponsorship

**blockchain**:
- sui network devnet
- move smart contracts
- ed25519 keypair for transaction signing

## installation

```bash
git clone https://github.com/qtzx06/darwin.git
cd darwin
npm install

# terminal 1: frontend
npm run dev

# terminal 2: backend (for local testing)
npm run server
```

## environment setup

create a `.env` file:

```env
SPONSOR_MNEMONIC="your twelve word mnemonic phrase"
VITE_GEMINI_API_KEY="your gemini api key"
VITE_LIVEKIT_API_KEY="livekit key (optional)"
VITE_LIVEKIT_API_SECRET="livekit secret (optional)"
```

never commit `.env` to version control.

## deployment

### vercel deployment

1. push to github
2. import to vercel
3. add environment variables in vercel dashboard:
   - `SPONSOR_MNEMONIC`: wallet mnemonic for sponsoring transactions
   - `VITE_GEMINI_API_KEY`: gemini api key
4. deploy

the app works with or without blockchain functionality. if sponsor wallet is unfunded or mnemonic missing, votes fail silently in background without breaking ux.

## project structure

```
darwin/
├── api/
│   └── vote.js              # vercel serverless function for sponsored voting
├── move/
│   └── agent_votes/         # sui smart contract
│       └── sources/
│           └── agent_votes.move
├── server/
│   └── index.js             # express server for local development
├── src/
│   ├── components/
│   │   ├── AgentCard.jsx    # agent card with code, preview, actions
│   │   ├── CodeRenderer.jsx # babel transpiler and react renderer
│   │   ├── Commentator.jsx  # voice ai commentary system
│   │   ├── ChatInput.jsx    # text input for user messages
│   │   ├── TranscriptPanel.jsx # voice transcription display
│   │   ├── Orchestration.jsx   # main orchestration state machine
│   │   ├── GlassSearchBar.jsx  # landing page search
│   │   ├── WebglNoise.jsx      # loading screen particles
│   │   └── Dither.jsx          # shader-based side panels
│   ├── services/
│   │   ├── geminiService.js       # agent code generation
│   │   ├── geminiAudioService.js  # voice input/output
│   │   └── commentatorGeminiService.js # commentary generation
│   └── utils/
│       ├── suiClient.js      # blockchain voting functions
│       └── agentWallets.json # agent wallet addresses
└── public/
    └── wisp/                 # fbo particle background
```

## functionality details

### code generation flow

1. user enters prompt on landing page
2. orchestration page loads with query parameter
3. `startbattle` function initiates simultaneous gemini api calls for all 4 agents
4. each agent receives prompt + personality-specific system prompt
5. agents return jsx code strings
6. `coderenderer` component:
   - strips markdown fences and import statements
   - transforms jsx to js using babel
   - extracts component name from transformed code
   - executes code with react hooks in scope
   - renders component in error boundary
7. code displays with typing animation in left panel
8. preview renders in right panel (expandable to full width)

### agent iteration flow

1. trigger event: user message, voice input, manager message, or vote
2. `analyzefeedback` examines feedback text for keywords
3. determines which agents should iterate (all, or specific agents)
4. for each target agent:
   - calls `iterateoncode` with current code + feedback
   - agent generates improved version via gemini
   - updates `agentcode` state
   - shows "working..." status during generation
   - displays "done!" when complete

### voting flow

1. user clicks thumbs up button on agent card
2. frontend immediately increments local vote count state
3. displays "[you] voted for {agent}" in chat
4. blockchain vote submitted in background (fails silently if error)
5. after 800ms delay, manager provides detailed analysis (rotates through 4 variants per agent)
6. after 1500ms, 2 random other agents post salty reactions
7. after 3500ms, triggers agent iteration with vote-specific prompt
8. every 10 seconds, frontend polls blockchain for actual vote counts

### voice interaction flow

**speaking to darwin**:
1. user clicks microphone button in transcript panel
2. mediarecorder starts capturing audio
3. audio chunks accumulate in array
4. on stop, chunks convert to blob
5. blob sent to gemini api for transcription
6. transcription converted to instruction format
7. displays as "[manager] boss said: {instruction}"
8. triggers `handleusermessage` for agent iteration

**commentator responses**:
1. chat event occurs (agent message, user vote, etc)
2. `observechat` generates short text observation via gemini
3. observation sent to live audio api session
4. audio chunks stream back as pcm data
5. chunks queued and played sequentially
6. commentary plays through browser audio
7. mute button toggles audio output

### manager auto-feedback system

hardcoded manager messages inject automatically:

```javascript
const managerMessages = [
  "make it blue",
  "add more animations",
  "speedrunner optimize this",
  // ... more messages
];
```

system watches `agentmessagecount` and injects manager message every 4 agent banter messages. this creates dynamic feedback loop without requiring constant user input.

### preview expansion

clicking on preview panel:
- hides code panel (left side)
- expands preview to 100% width with `preview-fullwidth` class
- preview still contained within agent card (not true fullscreen)
- clicking again restores split view

## smart contract details

### voting contract

```move
module agent_votes::agent_votes {
    struct VoteRegistry has key {
        id: UID,
        speedrunner_votes: u64,
        bloom_votes: u64,
        solver_votes: u64,
        loader_votes: u64
    }

    public entry fun vote(
        registry: &mut VoteRegistry,
        agent_id: u8,
        _ctx: &mut TxContext
    ) {
        // increments vote count for specified agent
    }
}
```

### manual voting via cli

```bash
# vote for speedrunner (0)
sui client call --package 0x302f582a43a8d22bc2a030ab76e3253f79618217a7a6576ad8a91b6075a85ae8 --module agent_votes --function vote --args 0x44e13769132e791fca5067ddb0d13d3f50ea1488d4c5a89453227fe7b11b15b9 0 --gas-budget 10000000

# vote for bloom (1)
sui client call --package 0x302f582a43a8d22bc2a030ab76e3253f79618217a7a6576ad8a91b6075a85ae8 --module agent_votes --function vote --args 0x44e13769132e791fca5067ddb0d13d3f50ea1488d4c5a89453227fe7b11b15b9 1 --gas-budget 10000000

# query current vote counts
sui client object 0x44e13769132e791fca5067ddb0d13d3f50ea1488d4c5a89453227fe7b11b15b9
```

## development

### local development

```bash
# terminal 1: vite dev server (port 5173)
npm run dev

# terminal 2: express backend (port 3001)
npm run server
```

vite proxy forwards `/api/*` requests to `localhost:3001` for local testing.

### building

```bash
npm run build
npm run preview
```

### debugging

common issues:

1. **vote fails**: ensure sponsor wallet has sui balance (get from https://faucet.sui.io/)
2. **code won't render**: check browser console for babel errors, error boundary catches most issues
3. **voice not working**: requires user gesture to initialize audiocontext
4. **agents not iterating**: check `processedmanagermessages` ref for duplicate prevention

## security considerations

- private keys only in environment variables
- `.env` excluded from git via `.gitignore`
- sponsored transactions hide wallet details from users
- error boundaries prevent code injection attacks
- babel runs in browser sandbox
- no eval() of untrusted code (uses function constructor with controlled scope)

## acknowledgments

built by [@qtzx06](https://github.com/qtzx06)

live demo: [darwin-theta-two.vercel.app](https://darwin-theta-two.vercel.app)

smart contract: [view on sui explorer](https://devnet.suivision.xyz/object/0x44e13769132e791fca5067ddb0d13d3f50ea1488d4c5a89453227fe7b11b15b9)
