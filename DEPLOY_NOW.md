# 🚀 Deploy Escrow Contracts NOW

You have Sui configuration already set up! Here's how to deploy the escrow contracts.

## Current Status

✅ Sui config exists (`~/.sui/sui_config/`)
✅ Connected to testnet
✅ Escrow contracts ready
❓ Need to verify Sui CLI is in PATH

## Quick Deploy Steps

### Option 1: If Sui CLI is Installed Elsewhere

If you installed Sui via a different method (homebrew, pre-built binary, etc.), find where it is:

```bash
# Find sui binary
find / -name "sui" -type f 2>/dev/null | grep -v "Permission denied"

# Or check common locations
ls /usr/local/bin/sui
ls ~/bin/sui
ls ~/.local/bin/sui
```

Once found, you can either:
- Add it to PATH, or
- Use full path in commands

### Option 2: Install Sui CLI via Cargo

```bash
# Install Rust/Cargo first
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# Install Sui CLI
cargo install --locked --git https://github.com/MystenLabs/sui.git --branch main sui

# Verify
sui --version
```

### Option 3: Use Pre-built Sui Binary

Download from Sui releases:
```bash
# macOS (example)
wget https://github.com/MystenLabs/sui/releases/latest/download/sui-macos-x86_64
chmod +x sui-macos-x86_64
sudo mv sui-macos-x86_64 /usr/local/bin/sui

# Verify
sui --version
```

## Once Sui CLI Works

### 1. Test the connection
```bash
sui client active-env
# Should show: testnet

sui client active-address
# Should show your address
```

### 2. Get test tokens (if on testnet/devnet)
```bash
sui client faucet
```

### 3. Deploy the contracts
```bash
cd escrow-contracts

# Option A: Automated script (recommended)
./scripts/deploy.sh

# Option B: Manual deployment
sui move build
sui move test
sui client publish --gas-budget 200000000
```

## Manual Deployment Commands

If you prefer step-by-step manual deployment:

```bash
# 1. Navigate to project
cd escrow-contracts

# 2. Build the Move package
sui move build

# 3. Run tests
sui move test

# 4. Check your network
sui client active-env

# 5. Check gas balance
sui client gas

# 6. Get test tokens if needed
sui client faucet

# 7. Publish the package
sui client publish --gas-budget 200000000
```

### What to Save from Deployment

After `sui client publish`, you'll see output like:

```
╭─────────────────────────────────────────────────────╮
│ Published Objects                                   │
├─────────────────────────────────────────────────────┤
│  ┌──                                                │
│  │ PackageID: 0xabc123...  ← SAVE THIS!           │
│  │ Version: 1                                      │
│  └──                                                │
╰─────────────────────────────────────────────────────╯
```

**Save the PackageID** - you'll need it to interact with the contracts!

## Verify Deployment

```bash
# View package on explorer
# Testnet: https://suiexplorer.com/object/<PACKAGE_ID>?network=testnet

# View package details
sui client object <PACKAGE_ID>

# Test create an escrow
./scripts/demo-escrow.sh
```

## Quick Test Escrow (Manual)

```bash
# 1. Get a coin
sui client gas

# 2. Split coin for escrow (0.1 SUI = 100000000 MIST)
sui client split-coin --coin-id <COIN_ID> --amounts 100000000

# 3. Create escrow (replace <PACKAGE_ID>, <NEW_COIN_ID>, <YOUR_ADDRESS>)
sui client call \
  --package <PACKAGE_ID> \
  --module escrow \
  --function create_shared \
  --type-args 0x2::sui::SUI \
  --args <NEW_COIN_ID> <YOUR_ADDRESS> "[]" "[]" "0x54657374" \
  --gas-budget 100000000
```

## Troubleshooting

**"sui: command not found"**
- Sui CLI not in PATH
- Install via one of the options above
- Or use full path to sui binary

**"Insufficient gas"**
```bash
sui client faucet
```

**"Module not found"**
- Check PACKAGE_ID is correct
- Make sure you're on the right network

**Need help with Sui config?**
```bash
# Reset/recreate config
sui client

# Switch network
sui client switch --env devnet
sui client switch --env testnet

# View current config
cat ~/.sui/sui_config/client.yaml
```

## Your Config Info

Based on what I found:
- **Config location**: `~/.sui/sui_config/`
- **Keystore**: `/Users/melodyyang/.sui/sui_config/sui.keystore`
- **Active network**: testnet
- **Status**: ✅ Configured, just need CLI access

## Next Steps

1. **Locate or install** Sui CLI (see options above)
2. **Test**: `sui client active-env`
3. **Get tokens**: `sui client faucet`
4. **Deploy**: `cd escrow-contracts && ./scripts/deploy.sh`
5. **Verify**: `./scripts/verify-deployment.sh`

---

Everything is ready to go - you just need the `sui` command accessible! 🚀

Choose whichever installation method works best for you, then run:

```bash
cd escrow-contracts
./scripts/deploy.sh
```

The automated script will handle the rest!
