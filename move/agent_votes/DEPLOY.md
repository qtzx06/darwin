# Deploying the Agent Votes Smart Contract

This guide walks through deploying the updated agent_votes Move contract with tipping functionality to Sui devnet.

## Prerequisites

1. **Sui CLI installed**: 
```bash
cargo install --locked --git https://github.com/MystenLabs/sui.git --branch devnet sui
```

2. **Sui wallet setup**:
```bash
sui client
```

3. **Get devnet SUI** from the faucet:
```bash
sui client faucet
```

## Deployment Steps

### 1. Navigate to the contract directory
```bash
cd move/agent_votes
```

### 2. Build the contract
```bash
sui move build
```

This will compile your Move code and check for errors.

### 3. Publish to Sui devnet
```bash
sui client publish --gas-budget 100000000
```

**Save the output!** You'll need:
- `packageId`: The deployed package address
- `registryId`: The shared object ID for VoteRegistry

Example output:
```
╭─────────────────────────────────────────────────────────────────────────────────────╮
│ Object Changes                                                                      │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ Created Objects:                                                                    │
│  ┌──                                                                               │
│  │ ObjectID: 0x28ab822cc91b6daf3c6e6f9ba087713ec956b9369d4222f13d196f6532f82a4b │
│  │ Type: 0xcf1f3::agent_votes::VoteRegistry                                       │
│  │ Owner: Shared                                                                   │
│  └──                                                                               │
│ Published Objects:                                                                  │
│  ┌──                                                                               │
│  │ PackageID: 0xcf1f3a68ade5af6ecd417e8f71cc3d11ca19cfa7d5d07244962161a83f21118e │
│  └──                                                                               │
╰─────────────────────────────────────────────────────────────────────────────────────╯
```

### 4. Initialize Agent Wallet Addresses

After deployment, set the agent wallet addresses in the registry:

```bash
sui client call \
  --package <PACKAGE_ID> \
  --module agent_votes \
  --function update_agent_wallets \
  --args <REGISTRY_ID> \
    0xb77755f36b8af6e50a601606713f7be643a4beb7c9da534d852a028edf1e3ea0 \
    0x0f49ec7048b42e6139d2d22b9acd078807426b94a26c31e3632366f34b84d513 \
    0xaba9b0ab7fbd9963adc13ddc5468f57f06f2b54fc46390a31a646ba12a88f401 \
    0x3efa42d7ae0c18f26fc6a91fca387ee64d4c542a523f5862d6cede24ed448bda \
  --gas-budget 10000000
```

Replace:
- `<PACKAGE_ID>` with your deployed package ID
- `<REGISTRY_ID>` with your VoteRegistry object ID

The addresses are in order: Speedrunner, Bloom, Solver, Loader

### 5. Update Frontend Configuration

Update the package and registry IDs in your frontend code:

**File: `src/utils/suiClient.js`**
```javascript
export const PACKAGE_ID = 'YOUR_NEW_PACKAGE_ID';
export const REGISTRY_ID = 'YOUR_NEW_REGISTRY_ID';
```

**File: `api/vote.js`** (if using Vercel)
```javascript
const PACKAGE_ID = 'YOUR_NEW_PACKAGE_ID';
const REGISTRY_ID = 'YOUR_NEW_REGISTRY_ID';
```

### 6. Test the Deployment

#### Test free voting:
```bash
sui client call \
  --package <PACKAGE_ID> \
  --module agent_votes \
  --function vote \
  --args <REGISTRY_ID> 0 \
  --gas-budget 10000000
```

#### Test voting with tip (0.1 SUI):
```bash
sui client call \
  --package <PACKAGE_ID> \
  --module agent_votes \
  --function vote_with_tip \
  --args <REGISTRY_ID> 0 \
  --gas-budget 10000000 \
  --split-coins gas [100000000]
```

#### Verify the registry:
```bash
sui client object <REGISTRY_ID>
```

You should see:
- Vote counts
- Agent wallet addresses
- Admin address (your deployer address)

## Troubleshooting

### Error: "Insufficient gas"
Increase the gas budget: `--gas-budget 200000000`

### Error: "Package not found"
Make sure you're using the correct network:
```bash
sui client active-env
```
Should show: `devnet`

### Error: "Object not found"
Double-check the REGISTRY_ID from the publish output.

### View Transaction on Explorer
After any transaction, you can view it on Sui Explorer:
```
https://devnet.suivision.xyz/txblock/<TX_DIGEST>
```

## Updating the Contract

If you need to update the contract logic:

1. Make changes to `sources/agent_votes.move`
2. Increment the version or make breaking changes carefully
3. Publish as a new package (Move packages are immutable)
4. Update the PACKAGE_ID in your frontend
5. The old REGISTRY_ID can be migrated or you can create a new one

## Security Notes

- **Admin Key**: The address that deploys the contract becomes the admin
- **Agent Wallets**: Can be updated only by the admin via `update_agent_wallets`
- **Private Keys**: Agent wallet private keys should be kept secure offline
- **Gas Sponsor**: Keep the sponsor mnemonic in environment variables only

## Next Steps

Once deployed:
1. Update the README with your new contract addresses
2. Test all functionality (free voting, tipping, balance display)
3. Monitor the contract on Sui Explorer
4. Consider setting up monitoring/alerts for agent earnings

## Resources

- [Sui Move Documentation](https://docs.sui.io/build/move)
- [Sui Explorer (Devnet)](https://devnet.suivision.xyz/)
- [Sui Discord](https://discord.gg/sui)

