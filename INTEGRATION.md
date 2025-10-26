# Sui Integration Guide

## What We Built

A simple on-chain voting system where users can vote for their favorite Darwin agents. Each vote is recorded on the Sui blockchain.

## Files Created

1. **Move Smart Contract** (`move/agent_votes/`)
   - `sources/agent_votes.move` - The voting logic
   - `Move.toml` - Package configuration

2. **Frontend Integration** (`src/utils/suiClient.js`)
   - Functions to vote and fetch vote counts

## Next Steps to Enable Voting

### Option 1: Simple (Without Wallet) - Display Only

Just display vote counts without letting users vote:

```javascript
// In Orchestration.jsx
import { getVoteCounts } from '../utils/suiClient';
import { useEffect, useState } from 'react';

const [voteCounts, setVoteCounts] = useState({});

useEffect(() => {
  // Fetch votes every 10 seconds
  const interval = setInterval(async () => {
    const counts = await getVoteCounts();
    setVoteCounts(counts);
  }, 10000);

  return () => clearInterval(interval);
}, []);

// Display in agent cards: "❤️ {voteCounts.speedrunner || 0} votes"
```

### Option 2: Full Integration (With Wallet)

To let users actually vote, you need to add a wallet connector:

1. Install wallet adapter:
```bash
npm install @mysten/dapp-kit @mysten/wallet-standard @tanstack/react-query
```

2. Wrap your app in providers (in `main.jsx` or `App.jsx`):
```javascript
import { SuiClientProvider, WalletProvider } from '@mysten/dapp-kit';
import { getFullnodeUrl } from '@mysten/sui/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import '@mysten/dapp-kit/dist/index.css';

const queryClient = new QueryClient();
const networks = {
  testnet: { url: getFullnodeUrl('testnet') }
};

<QueryClientProvider client={queryClient}>
  <SuiClientProvider networks={networks} defaultNetwork="testnet">
    <WalletProvider>
      <App />
    </WalletProvider>
  </SuiClientProvider>
</QueryClientProvider>
```

3. Add wallet connection button and voting:
```javascript
import { useCurrentAccount, useSignAndExecuteTransaction } from '@mysten/dapp-kit';
import { voteForAgent } from '../utils/suiClient';

function AgentCard({ agentId }) {
  const currentAccount = useCurrentAccount();
  const { mutate: signAndExecute } = useSignAndExecuteTransaction();

  const handleVote = async () => {
    if (!currentAccount) {
      alert('Please connect wallet first!');
      return;
    }

    try {
      await voteForAgent(agentId, { signAndExecuteTransactionBlock: signAndExecute });
      alert('Vote recorded on-chain!');
    } catch (error) {
      console.error('Vote failed:', error);
    }
  };

  return <button onClick={handleVote}>Vote</button>;
}
```

## Deployment Steps

1. **Deploy the smart contract** (see `move/agent_votes/README.md`)
   - Build with `sui move build`
   - Publish with `sui client publish --gas-budget 100000000`
   - Copy PackageID and RegistryID

2. **Update `src/utils/suiClient.js`** with your deployed IDs

3. **Choose integration option** (display-only or full wallet)

4. **Test on testnet** before going to mainnet

## Current State

✅ Smart contract written
✅ Frontend utilities created
⏸️ Not deployed yet (waiting for you to deploy)
⏸️ Not integrated with UI (waiting for wallet setup)

## Quick Start (No Deployment Needed Yet)

You can develop the UI without deploying by just showing placeholder vote counts. When you're ready to go live:

1. Install Sui CLI
2. Deploy the contract
3. Update the IDs
4. Add wallet integration
5. Users can vote!

The smart contract is super simple - just increments counters. No complex betting logic, just a like button that writes to blockchain 🔥
