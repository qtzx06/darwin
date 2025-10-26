# 🚀 Install Sui CLI and Deploy Escrow Contracts

Your escrow contracts are ready to deploy! Follow these steps to install the necessary tools and deploy.

## Current Status

✅ **Escrow contracts written** (660+ lines)
✅ **Comprehensive tests** (15 test cases)
✅ **Deployment scripts** (4 automated scripts)
✅ **Documentation** (complete)
❌ **Sui CLI** (needs installation)

## Quick Install & Deploy (15 minutes)

### Step 1: Install Rust (if not installed)

**macOS:**
```bash
# Option 1: Using Homebrew (recommended)
brew install rust

# Option 2: Using rustup
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

**Linux:**
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

**Verify:**
```bash
cargo --version
rustc --version
```

### Step 2: Install Sui CLI (~5-10 minutes)

```bash
cargo install --locked --git https://github.com/MystenLabs/sui.git --branch main sui
```

This will compile Sui from source. It takes a few minutes.

**Verify:**
```bash
sui --version
```

### Step 3: Install jq (JSON processor)

**macOS:**
```bash
brew install jq
```

**Linux:**
```bash
sudo apt-get install jq
```

### Step 4: Deploy! 🚀

```bash
cd escrow-contracts
./scripts/deploy.sh
```

The script will:
1. Set up your Sui wallet (if first time)
2. Select network (choose devnet for testing)
3. Get test tokens automatically
4. Run all tests
5. Deploy the contracts
6. Save configuration files
7. Show you the Package ID

### Step 5: Verify & Test

```bash
# Verify deployment
./scripts/verify-deployment.sh

# Try a demo escrow
./scripts/demo-escrow.sh

# Try a demo swap
./scripts/demo-swap.sh
```

---

## Alternative: Manual Deployment (without scripts)

If you prefer manual steps:

### 1. Set up Sui Client

```bash
sui client
# Follow prompts to create wallet
```

### 2. Switch to Devnet

```bash
sui client switch --env devnet
```

### 3. Get Test Tokens

```bash
sui client faucet
```

### 4. Build & Test

```bash
cd escrow-contracts
sui move build
sui move test
```

### 5. Deploy

```bash
sui client publish --gas-budget 200000000
```

**Save the Package ID from the output!**

### 6. Test Manually

```bash
# Get a coin
sui client gas

# Split coin for escrow (0.1 SUI)
sui client split-coin --coin-id <COIN_ID> --amounts 100000000

# Create escrow
sui client call \
  --package <PACKAGE_ID> \
  --module escrow \
  --function create_shared \
  --type-args 0x2::sui::SUI \
  --args <NEW_COIN_ID> <YOUR_ADDRESS> "[]" "[]" "0x5465737420457363726f77" \
  --gas-budget 100000000
```

---

## What Happens During Deployment

### Automated Script Flow

```
1. Check Prerequisites
   ├─ Sui CLI installed? ✓
   ├─ jq installed? ✓
   └─ Wallet configured? ✓

2. Network Selection
   └─ Choose: devnet/testnet/mainnet

3. Gas Check
   ├─ Check balance
   └─ Auto-request faucet (devnet)

4. Pre-deployment
   ├─ Run tests (15 tests)
   └─ Build package

5. Deployment
   ├─ Publish to Sui
   ├─ Extract Package ID
   └─ Save transaction digest

6. Post-deployment
   ├─ Create deployment-{network}.json
   ├─ Create .env.escrow
   └─ Show explorer links

7. Optional Demo
   └─ Run demo escrow
```

---

## Expected Output

### During Deploy

```
╔═══════════════════════════════════════════╗
║   Escrow Contracts Deployment Script     ║
║            Sui Blockchain                 ║
╚═══════════════════════════════════════════╝

✅ Sui CLI found: sui 1.15.0

📡 Current Configuration:
   Network: devnet
   Address: 0x...

Select deployment network:
1) devnet (recommended for testing)
2) testnet
3) mainnet (production)
4) Use current network (devnet)

Enter choice [1-4]: 1

✅ Target network: devnet

💰 Checking gas balance...
✅ Gas balance OK

🧪 Running tests...
Running Move unit tests
[ PASS    ] escrow::escrow_tests::test_create_escrow
[ PASS    ] escrow::escrow_tests::test_accept_escrow
...
Test result: OK. Total tests: 15; passed: 15; failed: 0

✅ All tests passed!

🔨 Building Move package...
✅ Build successful

📦 Publishing package to devnet...

✅ Package published successfully!

╔═══════════════════════════════════════════╗
║         Deployment Successful! 🎉         ║
╚═══════════════════════════════════════════╝

Network:     devnet
Package ID:  0x1234567890abcdef...
Tx Digest:   ABC123XYZ...
```

### Files Created

**deployment-devnet.json:**
```json
{
  "network": "devnet",
  "packageId": "0x1234567890abcdef...",
  "txDigest": "ABC123XYZ...",
  "deployer": "0x...",
  "timestamp": "2024-10-26T...",
  "version": "1.0.0"
}
```

**../.env.escrow:**
```bash
VITE_ESCROW_NETWORK=devnet
VITE_ESCROW_PACKAGE_ID=0x1234567890abcdef...
VITE_ESCROW_TX_DIGEST=ABC123XYZ...
VITE_ESCROW_DEPLOYER=0x...
```

---

## Troubleshooting

### Rust Installation Issues

**"command not found: cargo"**
```bash
# Source cargo environment
source $HOME/.cargo/env

# Or add to shell profile
echo 'source $HOME/.cargo/env' >> ~/.zshrc  # or ~/.bashrc
```

### Sui Installation Issues

**"failed to compile sui"**
- Make sure you have latest Rust: `rustup update`
- Check you have enough disk space (2-3 GB)
- Try again with: `cargo install --locked --git https://github.com/MystenLabs/sui.git --branch framework/testnet sui`

**"takes too long"**
- First install takes 5-10 minutes (compiling from source)
- Get coffee ☕ and wait

### Deployment Issues

**"Insufficient gas"**
```bash
# Request more test tokens
sui client faucet
```

**"Module compilation failed"**
- Check you're in the right directory: `cd escrow-contracts`
- Try rebuilding: `sui move build`

**"Transaction failed"**
- Check network status
- Try increasing gas: `--gas-budget 300000000`

---

## After Deployment

### 1. Update Your Frontend

Copy the Package ID to your app:

```typescript
// src/config/escrow.ts
export const ESCROW_CONFIG = {
  network: 'devnet',
  packageId: '0x...', // From deployment
};
```

### 2. Test the Contracts

```bash
# Create a test escrow
./scripts/demo-escrow.sh

# Create a test swap
./scripts/demo-swap.sh
```

### 3. View on Explorer

Devnet: `https://suiexplorer.com/object/<PACKAGE_ID>?network=devnet`

### 4. Monitor Events

```bash
sui client events --module escrow
```

---

## Need Help?

**Installation Help:**
- Rust: https://www.rust-lang.org/tools/install
- Sui: https://docs.sui.io/guides/developer/getting-started/sui-install

**Deployment Help:**
- See: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- See: [scripts/README.md](scripts/README.md)
- See: [QUICKSTART.md](QUICKSTART.md)

**Testing Help:**
- Run: `sui move test -v` for verbose output
- Check: [tests/escrow_tests.move](tests/escrow_tests.move)

---

## Quick Commands Reference

```bash
# Install Rust (macOS)
brew install rust

# Install Sui CLI
cargo install --locked --git https://github.com/MystenLabs/sui.git --branch main sui

# Install jq
brew install jq  # macOS
sudo apt-get install jq  # Linux

# Deploy (automated)
cd escrow-contracts
./scripts/deploy.sh

# Verify
./scripts/verify-deployment.sh

# Test
./scripts/demo-escrow.sh
```

---

## Timeline Estimate

| Task | Time |
|------|------|
| Install Rust | 2-5 min |
| Install Sui CLI | 5-10 min |
| Set up wallet | 1 min |
| Deploy contracts | 2 min |
| Verify & test | 2 min |
| **Total** | **12-20 min** |

---

## Ready to Deploy!

Once you've installed the prerequisites:

```bash
cd escrow-contracts
./scripts/deploy.sh
```

The automated script handles everything else! 🚀

---

**Questions?** Check the documentation or run commands with `--help`
