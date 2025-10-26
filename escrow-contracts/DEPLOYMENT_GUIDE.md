# 🚀 Escrow Contracts - Complete Deployment Guide

Step-by-step guide to deploy and use the escrow contracts on Sui blockchain.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Deploy (5 minutes)](#quick-deploy)
3. [Detailed Deployment](#detailed-deployment)
4. [Verification](#verification)
5. [Testing](#testing)
6. [Production Deployment](#production-deployment)
7. [Integration](#integration)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### 1. Install Sui CLI

```bash
cargo install --locked --git https://github.com/MystenLabs/sui.git --branch main sui
```

Verify installation:
```bash
sui --version
```

### 2. Install jq (JSON processor)

**macOS:**
```bash
brew install jq
```

**Linux:**
```bash
sudo apt-get install jq
```

### 3. Set Up Sui Wallet

```bash
sui client
```

Follow prompts to:
- Create new wallet, or
- Import existing wallet

### 4. Get Test Tokens (for devnet/testnet)

```bash
sui client switch --env devnet
sui client faucet
```

---

## Quick Deploy

**Fastest path from zero to deployed:**

```bash
# 1. Navigate to project
cd escrow-contracts

# 2. Run deployment script
./scripts/deploy.sh

# 3. Select network (choose 1 for devnet)
# Follow prompts...

# 4. Verify deployment
./scripts/verify-deployment.sh

# 5. Try a demo
./scripts/demo-escrow.sh
```

**Done!** Your escrow contracts are live on Sui.

---

## Detailed Deployment

### Step 1: Build the Contracts

```bash
cd escrow-contracts
sui move build
```

**Expected output:**
```
BUILDING escrow_contracts
UPDATING GIT DEPENDENCY https://github.com/MystenLabs/sui.git
INCLUDING DEPENDENCY Sui
BUILDING escrow_contracts
```

### Step 2: Run Tests

```bash
sui move test
```

**Expected output:**
```
Running Move unit tests
[ PASS    ] escrow::escrow_tests::test_create_escrow
[ PASS    ] escrow::escrow_tests::test_accept_escrow
...
Test result: OK. Total tests: 15; passed: 15; failed: 0
```

### Step 3: Choose Network

**For testing:**
```bash
sui client switch --env devnet
```

**For pre-production:**
```bash
sui client switch --env testnet
```

**For production:**
```bash
sui client switch --env mainnet
```

### Step 4: Check Gas Balance

```bash
sui client gas
```

If empty on devnet/testnet:
```bash
sui client faucet
```

### Step 5: Publish

```bash
sui client publish --gas-budget 200000000
```

**Save the output!** You need:
- **Package ID**: `0x...`
- **Transaction Digest**: For verification

**Example output:**
```
╭─────────────────────────────────────────────────────────╮
│ Object Changes                                          │
├─────────────────────────────────────────────────────────┤
│ Created Objects:                                        │
│  ┌──                                                    │
│  │ ObjectID: 0xabc123...                               │
│  │ Sender: 0xdef456...                                 │
│  │ ObjectType: 0x2::package::UpgradeCap                │
│  └──                                                    │
│ Published Objects:                                      │
│  ┌──                                                    │
│  │ PackageID: 0x789xyz...   ← SAVE THIS!              │
│  └──                                                    │
╰─────────────────────────────────────────────────────────╯
```

---

## Verification

### Using the Script

```bash
./scripts/verify-deployment.sh
```

### Manual Verification

**Check package exists:**
```bash
sui client object <PACKAGE_ID>
```

**View on explorer:**
- Devnet: `https://suiexplorer.com/object/<PACKAGE_ID>?network=devnet`
- Testnet: `https://suiexplorer.com/object/<PACKAGE_ID>?network=testnet`
- Mainnet: `https://suiexplorer.com/object/<PACKAGE_ID>`

---

## Testing

### Create Test Escrow

**Using script:**
```bash
./scripts/demo-escrow.sh
```

**Manual:**
```bash
# 1. Split coin (0.1 SUI = 100000000 MIST)
sui client split-coin --coin-id <COIN_ID> --amounts 100000000

# 2. Create escrow
sui client call \
  --package <PACKAGE_ID> \
  --module escrow \
  --function create_shared \
  --type-args 0x2::sui::SUI \
  --args <NEW_COIN_ID> <RECIPIENT_ADDR> "[]" "[]" "0x5061796d656e74" \
  --gas-budget 100000000

# 3. Accept escrow (as recipient)
sui client call \
  --package <PACKAGE_ID> \
  --module escrow \
  --function accept \
  --type-args 0x2::sui::SUI \
  --args <ESCROW_ID> 0x6 \
  --gas-budget 100000000
```

### Test Atomic Swap

**Using script:**
```bash
./scripts/demo-swap.sh
```

**Manual:** See [QUICKSTART.md](QUICKSTART.md) for detailed swap commands.

---

## Production Deployment

### Checklist Before Mainnet

- [ ] All tests passing on devnet
- [ ] Manual testing completed
- [ ] Integration testing with frontend
- [ ] Security review completed
- [ ] Gas costs analyzed
- [ ] Backup of deployment keys
- [ ] Monitoring setup ready
- [ ] Emergency procedures documented

### Deploy to Mainnet

```bash
# 1. Switch to mainnet
sui client switch --env mainnet

# 2. DOUBLE-CHECK you're on mainnet
sui client active-env
# Should output: mainnet

# 3. Check you have sufficient SUI
sui client gas

# 4. Deploy
sui client publish --gas-budget 200000000

# 5. IMMEDIATELY save Package ID
echo "PACKAGE_ID=0x..." >> .env.production

# 6. Verify
./scripts/verify-deployment.sh
```

### Post-Deployment

1. **Update frontend config**
   ```javascript
   const ESCROW_PACKAGE_ID = '0x...'; // Mainnet
   ```

2. **Monitor events**
   ```bash
   sui client events --module escrow
   ```

3. **Set up alerts** for unusual activity

4. **Document the deployment**
   - Save `deployment-mainnet.json`
   - Record in changelog
   - Update team documentation

---

## Integration

### JavaScript/TypeScript

```typescript
import { Transaction } from '@mysten/sui/transactions';

const PACKAGE_ID = '0x...'; // From deployment

// Create escrow
const tx = new Transaction();
const [coin] = tx.splitCoins(tx.gas, [100_000_000]); // 0.1 SUI

tx.moveCall({
  target: `${PACKAGE_ID}::escrow::create_shared`,
  typeArguments: ['0x2::sui::SUI'],
  arguments: [
    coin,
    tx.pure.address(recipientAddr),
    tx.pure.option('address', null), // no arbiter
    tx.pure.option('u64', null),     // no time-lock
    tx.pure(new TextEncoder().encode('Payment for services')),
  ],
});

await signAndExecuteTransaction({ transaction: tx });
```

### Environment Variables

Create `.env.production`:
```bash
VITE_ESCROW_NETWORK=mainnet
VITE_ESCROW_PACKAGE_ID=0x...
```

Load in your app:
```javascript
const config = {
  network: import.meta.env.VITE_ESCROW_NETWORK,
  packageId: import.meta.env.VITE_ESCROW_PACKAGE_ID,
};
```

---

## Troubleshooting

### Build Errors

**"dependency not found"**
```bash
# Update dependencies
sui move build --fetch-deps-only
```

**"compilation error"**
- Check syntax in `sources/escrow.move`
- Ensure Move.toml is correct

### Deployment Errors

**"Insufficient gas"**
```bash
# Check balance
sui client gas

# Get more (devnet/testnet)
sui client faucet

# Or use different gas coin
sui client publish --gas <COIN_ID> --gas-budget 200000000
```

**"Module already exists"**
- You're trying to publish same package twice
- Use a different address or wait for first tx

**"Transaction timeout"**
- Network congestion
- Retry with higher gas budget
- Try again later

### Runtime Errors

**"Function not found"**
- Check PACKAGE_ID is correct
- Verify module name is "escrow"
- Ensure function exists: `sui client call --package <PKG> --module escrow --function <NAME> --help`

**"Object not found"**
- Escrow may have been accepted/cancelled
- Check escrow ID is correct
- View on explorer

**"Access denied" (ENotSender, ENotRecipient)**
- Using wrong wallet
- Check sender/recipient addresses match

**"Time-lock not expired" (EEscrowLocked)**
- Escrow has unlock time in future
- Wait until unlock time
- Check with: `sui client object <ESCROW_ID>`

---

## Network Information

### Devnet
- **Purpose**: Development and testing
- **Resets**: Periodically (data loss expected)
- **Faucet**: https://faucet.sui.io/
- **Explorer**: https://suiexplorer.com/?network=devnet

### Testnet
- **Purpose**: Pre-production staging
- **Resets**: Rarely
- **Faucet**: Available
- **Explorer**: https://suiexplorer.com/?network=testnet

### Mainnet
- **Purpose**: Production
- **Resets**: Never
- **Faucet**: No (use real SUI)
- **Explorer**: https://suiexplorer.com/

---

## Gas Costs

Typical gas costs (approximate):

| Operation | MIST | SUI |
|-----------|------|-----|
| Deploy package | ~50M | ~0.05 |
| Create escrow | ~2M | ~0.002 |
| Accept escrow | ~2M | ~0.002 |
| Cancel escrow | ~2M | ~0.002 |
| Create swap | ~3M | ~0.003 |
| Execute swap | ~3M | ~0.003 |

**1 SUI = 1,000,000,000 MIST**

---

## Support

- **Documentation**: [README.md](README.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **Scripts Guide**: [scripts/README.md](scripts/README.md)
- **Sui Docs**: https://docs.sui.io/
- **Sui Discord**: https://discord.gg/sui

---

## Security Reminders

1. **Never commit private keys** to version control
2. **Test on devnet** before mainnet
3. **Audit contracts** for production use
4. **Monitor events** for suspicious activity
5. **Have emergency procedures** ready
6. **Keep backups** of deployment info
7. **Document everything** for team

---

Built with ❤️ on Sui blockchain
