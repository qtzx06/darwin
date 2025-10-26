# Escrow Deployment Scripts

Automated scripts for deploying, testing, and using the escrow contracts on Sui blockchain.

## 📜 Available Scripts

### 1. `deploy.sh` - Main Deployment Script

Builds, tests, and deploys the escrow contracts to Sui.

**Features:**
- ✅ Automatic network selection (devnet/testnet/mainnet)
- ✅ Pre-deployment test execution
- ✅ Gas balance verification
- ✅ Automatic faucet request (for devnet/testnet)
- ✅ Saves deployment info to JSON
- ✅ Creates environment configuration file

**Usage:**
```bash
./scripts/deploy.sh
```

**Output:**
- `deployment-{network}.json` - Deployment details
- `../.env.escrow` - Environment variables for frontend

---

### 2. `verify-deployment.sh` - Deployment Verification

Verifies the deployed package and checks all functions exist.

**Checks:**
- ✅ Package exists on blockchain
- ✅ Escrow module is present
- ✅ All functions are accessible
- ✅ Deployment transaction is valid
- ✅ Contract events (if any)

**Usage:**
```bash
./scripts/verify-deployment.sh
```

**Example Output:**
```
[1/5] Checking package existence...
✅ Package exists

[2/5] Checking escrow module...
✅ Escrow module found

[3/5] Verifying contract functions...
  ✓ create_shared
  ✓ accept
  ✓ cancel
  ✓ raise_dispute
  ✓ resolve_dispute
  ✓ create_swap
...
```

---

### 3. `demo-escrow.sh` - Create Demo Escrow

Creates a sample escrow with 0.1 SUI for testing.

**Features:**
- Creates escrow with customizable recipient
- Saves escrow details to JSON
- Shows accept/cancel commands
- Optional auto-accept in testing mode

**Usage:**
```bash
./scripts/demo-escrow.sh
```

**Interactive Prompts:**
- Enter recipient address (or press Enter for self-test)
- Option to auto-accept if you're both sender/recipient

**Output:**
- `demo-escrow.json` - Escrow details

---

### 4. `demo-swap.sh` - Create Demo Atomic Swap

Creates a sample atomic swap between two parties.

**Features:**
- Party A offers 0.05 SUI
- Party B offers 0.1 SUI
- 1-hour expiration
- Testing mode (same address for both parties)
- Optional auto-complete

**Usage:**
```bash
./scripts/demo-swap.sh
```

**Interactive Prompts:**
- Enter Party B address (or press Enter for self-test)
- Option to complete swap if testing mode

**Output:**
- `demo-swap.json` - Swap details

---

## 🚀 Quick Start

### First Time Setup

```bash
# 1. Deploy to devnet
./scripts/deploy.sh
# Select option 1 (devnet)

# 2. Verify deployment
./scripts/verify-deployment.sh

# 3. Try a demo escrow
./scripts/demo-escrow.sh

# 4. Try a demo swap
./scripts/demo-swap.sh
```

### Deploying to Different Networks

**Devnet (Testing):**
```bash
./scripts/deploy.sh
# Select: 1) devnet
```

**Testnet (Pre-production):**
```bash
./scripts/deploy.sh
# Select: 2) testnet
```

**Mainnet (Production):**
```bash
./scripts/deploy.sh
# Select: 3) mainnet
# Type 'YES' to confirm
```

---

## 📁 Generated Files

### `deployment-{network}.json`

Contains deployment metadata:
```json
{
  "network": "devnet",
  "packageId": "0x...",
  "txDigest": "...",
  "deployer": "0x...",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0"
}
```

### `../.env.escrow`

Environment variables for integration:
```bash
VITE_ESCROW_NETWORK=devnet
VITE_ESCROW_PACKAGE_ID=0x...
VITE_ESCROW_TX_DIGEST=...
VITE_ESCROW_DEPLOYER=0x...
```

### `demo-escrow.json`

Sample escrow details:
```json
{
  "escrowId": "0x...",
  "sender": "0x...",
  "recipient": "0x...",
  "amount": "100000000",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### `demo-swap.json`

Sample swap details:
```json
{
  "swapId": "0x...",
  "partyA": "0x...",
  "partyB": "0x...",
  "amountA": "50000000",
  "amountB": "100000000",
  "expiration": "1704067200000",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

---

## 🛠️ Prerequisites

All scripts require:

1. **Sui CLI** installed:
   ```bash
   cargo install --locked --git https://github.com/MystenLabs/sui.git --branch main sui
   ```

2. **jq** (JSON processor):
   ```bash
   # macOS
   brew install jq

   # Ubuntu/Debian
   sudo apt-get install jq
   ```

3. **Active Sui wallet**:
   ```bash
   sui client
   # Follow prompts to create/import wallet
   ```

---

## 🔧 Troubleshooting

### "sui: command not found"
→ Install Sui CLI (see Prerequisites)

### "jq: command not found"
→ Install jq: `brew install jq` (macOS) or `apt-get install jq` (Linux)

### "No deployment found"
→ Run `./scripts/deploy.sh` first

### "Insufficient gas"
→ Request test tokens:
```bash
sui client faucet
```

### "Module not found"
→ Verify package ID in `deployment-{network}.json` is correct

### Script permission denied
→ Make executable:
```bash
chmod +x scripts/*.sh
```

---

## 📝 Manual Commands

If you prefer manual deployment:

### Deploy
```bash
cd escrow-contracts
sui move build
sui move test
sui client publish --gas-budget 200000000
```

### Create Escrow
```bash
# Split coin
sui client split-coin --coin-id <COIN> --amounts 100000000

# Create escrow
sui client call \
  --package <PACKAGE_ID> \
  --module escrow \
  --function create_shared \
  --type-args 0x2::sui::SUI \
  --args <COIN_ID> <RECIPIENT> "[]" "[]" "0x5061796d656e74" \
  --gas-budget 100000000
```

### Accept Escrow
```bash
sui client call \
  --package <PACKAGE_ID> \
  --module escrow \
  --function accept \
  --type-args 0x2::sui::SUI \
  --args <ESCROW_ID> 0x6 \
  --gas-budget 100000000
```

---

## 🔗 Useful Links

- **Sui Explorer (Devnet)**: https://suiexplorer.com/?network=devnet
- **Sui Explorer (Testnet)**: https://suiexplorer.com/?network=testnet
- **Sui Explorer (Mainnet)**: https://suiexplorer.com/
- **Sui Documentation**: https://docs.sui.io/
- **Sui Faucet (Devnet)**: https://faucet.sui.io/

---

## 📊 Script Flow Diagram

```
┌──────────────┐
│  deploy.sh   │
└──────┬───────┘
       │
       ├─> Build
       ├─> Test
       ├─> Publish
       ├─> Save deployment info
       └─> Create .env
              │
              ▼
       ┌──────────────────┐
       │ verify-deploy.sh │
       └──────┬───────────┘
              │
              ├─> Check package
              ├─> Check module
              ├─> Check functions
              └─> Verify transaction
                     │
                     ▼
              ┌─────────────┐
              │ demo-*.sh   │
              └─────┬───────┘
                    │
                    ├─> Create escrow/swap
                    ├─> Show commands
                    └─> Optional auto-complete
```

---

## 🎯 Best Practices

1. **Always test on devnet first**
   ```bash
   ./scripts/deploy.sh  # Select devnet
   ```

2. **Verify after deployment**
   ```bash
   ./scripts/verify-deployment.sh
   ```

3. **Save deployment files**
   - Keep `deployment-*.json` files
   - Commit to version control (except mainnet with sensitive data)

4. **Use descriptive names**
   - Add meaningful descriptions to escrows
   - Document swap purposes

5. **Monitor gas costs**
   - Check transaction costs
   - Optimize for production

---

## 📜 License

MIT License - See ../LICENSE for details
