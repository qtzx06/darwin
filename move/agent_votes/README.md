# Agent Votes - Sui Smart Contract

On-chain voting system for Darwin agents built on Sui blockchain.

## Prerequisites

1. Install Sui CLI:
```bash
curl -sSfL https://raw.githubusercontent.com/Mystenlabs/suiup/main/install.sh | sh
suiup install sui@testnet
```

2. Verify installation:
```bash
sui --version
```

3. Create a Sui address:
```bash
sui client new-address ed25519
```

4. Get testnet SUI tokens:
```bash
sui client faucet
```

## Deployment

1. Build the contract:
```bash
cd move/agent_votes
sui move build
```

2. Publish to testnet:
```bash
sui client publish --gas-budget 100000000
```

3. After publishing, you'll see output like:
```
Published Objects:
  PackageID: 0xABC123...

Created Objects:
  ObjectID: 0xDEF456... (VoteRegistry)
```

4. Copy these IDs and update `src/utils/suiClient.js`:
```javascript
export const PACKAGE_ID = '0xABC123...'; // Your PackageID
export const REGISTRY_ID = '0xDEF456...'; // Your VoteRegistry ObjectID
```

## Usage

Once deployed, users can vote by clicking the thumbs up button on agent cards. Votes are recorded on-chain and can be queried at any time.

## Contract Functions

- `vote(registry: &mut VoteRegistry, agent_id: u8)` - Vote for an agent (0-3)
- `get_speedrunner_votes(registry: &VoteRegistry): u64` - Get speedrunner vote count
- `get_bloom_votes(registry: &VoteRegistry): u64` - Get bloom vote count
- `get_solver_votes(registry: &VoteRegistry): u64` - Get solver vote count
- `get_loader_votes(registry: &VoteRegistry): u64` - Get loader vote count

## Testing Locally

To test without deploying:

1. Start a local Sui network:
```bash
sui start
```

2. In another terminal, publish to local:
```bash
sui client publish --gas-budget 100000000
```

## Network Configuration

The contract is configured for Sui testnet. To use mainnet, update the network in `src/utils/suiClient.js`:

```javascript
export const suiClient = new SuiClient({ url: getFullnodeUrl('mainnet') });
```
