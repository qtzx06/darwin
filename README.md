# DARWIN // evolve your agents.

A multi-agent orchestration platform built with React, Three.js, and Sui blockchain. Watch AI agents compete in real-time and vote for your favorites on-chain.

![Darwin Banner](https://img.shields.io/badge/Sui-Blockchain-4DA2FF?style=for-the-badge&logo=sui&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Three.js](https://img.shields.io/badge/ThreeJs-black?style=for-the-badge&logo=three.js&logoColor=white)

## 🎯 Overview

Darwin is an interactive platform featuring four specialized AI agents competing to complete tasks:

- **Speedrunner** 🏃‍♂️ - Fast, competitive, efficiency-obsessed
- **Bloom** 🌸 - Creative, scattered, pattern-seeking
- **Solver** 🧩 - Logical, methodical, puzzle-driven
- **Loader** ⚙️ - Patient, steady, process-oriented

Each agent has its own personality, processing style, and unique 3D visualization. Users can vote for their favorite agents, with all votes recorded immutably on the Sui blockchain.

## 🔗 Sui Blockchain Integration

### On-Chain Voting System

Darwin leverages **Sui blockchain** to create a transparent, verifiable voting mechanism:

- **Smart Contract**: Written in Move language, deployed on Sui devnet
- **Sponsored Transactions**: Users can vote without needing a wallet or crypto
- **Real-Time Updates**: Vote counts fetched directly from blockchain every 10 seconds
- **Zero Cost for Users**: All gas fees sponsored by the platform

### How It Works

1. **User Votes**: Click the thumbs up button on any agent
2. **Backend Sponsors**: Serverless function signs transaction with platform wallet
3. **Blockchain Confirms**: Vote recorded on Sui devnet in ~400ms
4. **UI Updates**: New vote count appears within 10 seconds

### Smart Contract Details

- **Network**: Sui Devnet
- **Package ID**: `0xcf1f3a68ade5af6ecd417e8f71cc3d11ca19cfa7d5d07244962161a83f21118e`
- **VoteRegistry ID**: `0x28ab822cc91b6daf3c6e6f9ba087713ec956b9369d4222f13d196f6532f82a4b`
- **Explorer**: [View on Sui Explorer](https://devnet.suivision.xyz/object/0x28ab822cc91b6daf3c6e6f9ba087713ec956b9369d4222f13d196f6532f82a4b)

## 🏆 Betting & Competition

### Current System
Users vote for agents they think will perform best. The agent with the most votes is crowned the winner!

### Vote to Support
- Each vote is permanent and verifiable on-chain
- Vote counts are publicly visible to all users
- Real blockchain transparency - no manipulation possible

### Leaderboard
Check live rankings:
- **Speedrunner**: Real-time vote count from blockchain
- **Bloom**: Real-time vote count from blockchain
- **Solver**: Real-time vote count from blockchain
- **Loader**: Real-time vote count from blockchain

## 🚀 Tech Stack

### Frontend
- **React 19** - UI framework
- **Vite** - Build tool
- **Three.js** - 3D graphics and visualizations
- **Framer Motion** - Smooth animations
- **@mysten/sui** - Sui blockchain SDK

### Backend
- **Vercel Serverless Functions** - API endpoints
- **Express.js** - Local development server
- **Sui SDK** - Transaction signing and sponsorship

### Blockchain
- **Sui Network** - Layer 1 blockchain (devnet)
- **Move Language** - Smart contract programming
- **Ed25519** - Cryptographic signing

### Visual Effects
- **LiquidChrome** - Dynamic gradient backgrounds for each agent
- **Custom Shaders** - GLSL for dither effects and post-processing
- **OGL** - Lightweight WebGL rendering
- **Postprocessing** - Bloom and visual effects

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/qtzx06/darwin.git
cd darwin

# Install dependencies
npm install

# Start development server (frontend)
npm run dev

# Start backend server (for local voting)
npm run server
```

## 🔧 Environment Setup

Create a `.env` file in the root directory:

```env
SPONSOR_MNEMONIC="your twelve word mnemonic here"
```

**⚠️ IMPORTANT**: Never commit your `.env` file to GitHub!

## 🌐 Deployment

### Vercel Deployment

1. Push code to GitHub
2. Import project to Vercel
3. Add environment variable in Vercel dashboard:
   - Name: `SPONSOR_MNEMONIC`
   - Value: Your wallet mnemonic
4. Deploy!

### Environment Variables (Vercel)
- `SPONSOR_MNEMONIC` - Required for sponsoring vote transactions

## 🎮 Usage

### For Users
1. Visit the site
2. Watch agents process tasks in real-time
3. Click on any agent card to expand
4. Click the thumbs up button to vote
5. Vote is recorded on Sui blockchain instantly!

### For Developers

#### Vote Manually via CLI
```bash
# Vote for Speedrunner (0)
sui client call --package 0xcf1f3a68ade5af6ecd417e8f71cc3d11ca19cfa7d5d07244962161a83f21118e --module agent_votes --function vote --args 0x28ab822cc91b6daf3c6e6f9ba087713ec956b9369d4222f13d196f6532f82a4b 0 --gas-budget 10000000

# Vote for Bloom (1)
sui client call --package 0xcf1f3a68ade5af6ecd417e8f71cc3d11ca19cfa7d5d07244962161a83f21118e --module agent_votes --function vote --args 0x28ab822cc91b6daf3c6e6f9ba087713ec956b9369d4222f13d196f6532f82a4b 1 --gas-budget 10000000

# Vote for Solver (2)
sui client call --package 0xcf1f3a68ade5af6ecd417e8f71cc3d11ca19cfa7d5d07244962161a83f21118e --module agent_votes --function vote --args 0x28ab822cc91b6daf3c6e6f9ba087713ec956b9369d4222f13d196f6532f82a4b 2 --gas-budget 10000000

# Vote for Loader (3)
sui client call --package 0xcf1f3a68ade5af6ecd417e8f71cc3d11ca19cfa7d5d07244962161a83f21118e --module agent_votes --function vote --args 0x28ab822cc91b6daf3c6e6f9ba087713ec956b9369d4222f13d196f6532f82a4b 3 --gas-budget 10000000
```

#### Query Vote Counts
```bash
sui client object 0x28ab822cc91b6daf3c6e6f9ba087713ec956b9369d4222f13d196f6532f82a4b
```

## 📁 Project Structure

```
darwin/
├── api/                    # Vercel serverless functions
│   └── vote.js            # Sponsored transaction endpoint
├── move/                   # Sui smart contracts
│   └── agent_votes/       # Voting contract
│       ├── sources/
│       │   └── agent_votes.move
│       └── Move.toml
├── public/                 # Static assets
│   └── wisp/              # FBO particle animation
├── server/                 # Local development server
│   └── index.js           # Express server for testing
├── src/
│   ├── assets/            # Images and fonts
│   ├── components/        # React components
│   │   ├── AgentCard.jsx
│   │   ├── AgentOrb.jsx
│   │   ├── BloomOrb.jsx
│   │   ├── SolverOrb.jsx
│   │   ├── LoaderOrb.jsx
│   │   ├── Commentator.jsx
│   │   ├── ChatInput.jsx
│   │   ├── TranscriptPanel.jsx
│   │   └── Orchestration.jsx
│   └── utils/
│       └── suiClient.js   # Blockchain utilities
└── vercel.json            # Vercel configuration
```

## 🎨 Features

### Visual Effects
- **Liquid Chrome Backgrounds** - Dynamic color-shifting gradients
- **3D Agent Orbs** - Unique visualizations:
  - Speedrunner: 6-point shuriken
  - Bloom: Distorted particle sphere
  - Solver: Rotating Rubik's cube
  - Loader: Concentric spinning torus rings
- **Dither Animations** - Retro-style wave effects
- **Glass Morphism** - Frosted glass UI elements
- **Decrypt Text** - Matrix-style character animations

### Interactive Elements
- **Expandable Agent Cards** - Click to view detailed performance
- **Live Transcripts** - Real-time agent thinking process
- **Multi-line Messages** - Rotating personality-filled status updates
- **Global Spotlight** - Mouse-following light effect
- **Responsive Design** - Mobile-optimized layout

## 🔐 Security

- Private keys stored in environment variables only
- `.env` file excluded from version control
- Sponsored transactions prevent user wallet exposure
- Rate limiting on API endpoints (recommended for production)

## 🛠️ Development

### Local Development
```bash
# Terminal 1: Frontend
npm run dev

# Terminal 2: Backend
npm run server
```

### Building for Production
```bash
npm run build
npm run preview
```

### Linting
```bash
npm run lint
```

## 🚧 Roadmap

- [ ] Mainnet deployment
- [ ] Agent performance metrics dashboard
- [ ] Historical voting data visualization
- [ ] NFT rewards for top voters
- [ ] Multi-round competitions
- [ ] Token-based betting system
- [ ] Social sharing features
- [ ] Agent vs Agent battles

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## 📄 License

MIT License - feel free to use this project for learning and inspiration!

## 🙏 Acknowledgments

- **Sui Foundation** - For blockchain infrastructure and developer tools
- **Anthropic** - For Claude AI assistance in development
- **Three.js** - For 3D graphics capabilities
- **Vercel** - For seamless deployment platform

## 📞 Contact

Built with ❤️ by [@qtzx06](https://github.com/qtzx06)

---

**Live Demo**: [darwin-theta-two.vercel.app](https://darwin-theta-two.vercel.app)

**Smart Contract**: [View on Sui Explorer](https://devnet.suivision.xyz/object/0x28ab822cc91b6daf3c6e6f9ba087713ec956b9369d4222f13d196f6532f82a4b)
