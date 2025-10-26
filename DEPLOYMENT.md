# Sui Blockchain Betting Deployment Guide

This guide walks you through deploying the Colosseum betting smart contract to Sui blockchain and integrating it with your Darwin application.

## Prerequisites

1. **Install Sui CLI**
   ```bash
   cargo install --locked --git https://github.com/MystenLabs/sui.git --branch main sui
   ```

2. **Create/Configure Sui Wallet**
   ```bash
   sui client
   # Follow prompts to create a new wallet or import existing one
   ```

3. **Get Testnet SUI Tokens**
   ```bash
   # Switch to devnet
   sui client switch --env devnet

   # Request test tokens from faucet
   sui client faucet

   # Check your balance
   sui client gas
   ```

## Step 1: Build the Move Package

```bash
cd colosseum
sui move build
```

This will compile your Move contract and check for any errors.

## Step 2: Publish the Package

```bash
sui client publish --gas-budget 200000000
```

**Important:** Save the output! You'll need:
- **Package ID** (looks like `0x...`)
- **Transaction Digest**

The output will look something like:
```
╭──────────────────────────────────────────────────────────────────────╮
│ Published Objects                                                    │
├──────────────────────────────────────────────────────────────────────┤
│  ┌──                                                                │
│  │ PackageID: 0xabcd1234...                                         │
│  └──                                                                │
╰──────────────────────────────────────────────────────────────────────╯
```

Copy the `PackageID` value.

## Step 3: Initialize the House

The `init` function runs automatically on publish and creates a shared `House` object. Find the House object ID:

```bash
# View objects owned/created in the publish transaction
sui client object <TRANSACTION_DIGEST>
```

Or query for shared objects:
```bash
sui client objects --json | grep -A 5 "House"
```

Look for an object with type `<PACKAGE_ID>::colosseum_bets::House`. Copy its Object ID.

## Step 4: Seed the House Pot (Optional but Recommended)

To allow payouts, you need to fund the house:

```bash
# First, get a coin to split
sui client gas

# Split some SUI (e.g., 10 SUI = 10000000000 MIST)
sui client split-coin --coin-id <YOUR_COIN_ID> --amounts 10000000000 --gas-budget 100000000

# Note the new coin ID from the output, then deposit it
sui client call \
  --package <PACKAGE_ID> \
  --module colosseum_bets \
  --function deposit \
  --args <HOUSE_ID> <SPLIT_COIN_ID> \
  --gas-budget 100000000
```

## Step 5: Configure Your App

1. **Create `.env` file:**
   ```bash
   cp .env.example .env
   ```

2. **Update the values in `.env`:**
   ```env
   VITE_SUI_NETWORK=devnet
   VITE_SUI_PACKAGE_ID=0xYOUR_PACKAGE_ID_HERE
   VITE_SUI_HOUSE_ID=0xYOUR_HOUSE_OBJECT_ID_HERE
   ```

3. **Restart your dev server:**
   ```bash
   npm run dev
   ```

## Step 6: Test the Integration

1. Open your app in the browser
2. Click "Connect Wallet" in the top-right
3. Connect your Sui wallet (install Sui Wallet extension if needed)
4. Try placing a bet by:
   - Selecting an amount
   - Clicking 0 or 1
   - Approving the transaction in your wallet

## Testing Commands (CLI)

You can also test the contract directly via CLI:

### Place a Bet
```bash
sui client call \
  --package <PACKAGE_ID> \
  --module colosseum_bets \
  --function place_bet \
  --args <HOUSE_ID> <YOUR_SUI_COIN_ID> 100000000 1 \
  --gas-budget 100000000
```

### Settle a Bet
```bash
sui client call \
  --package <PACKAGE_ID> \
  --module colosseum_bets \
  --function settle_bet \
  --args <HOUSE_ID> 0x8 <YOUR_ADDRESS> 100000000 1 \
  --gas-budget 100000000
```

Note: `0x8` is the well-known Random object address on Sui.

## Troubleshooting

### "Insufficient gas"
- Request more test tokens: `sui client faucet`
- Increase gas budget in commands

### "Object not found"
- Verify Package ID and House ID are correct
- Make sure you're on the right network (devnet/testnet/mainnet)

### "Module not found"
- Ensure the package was published successfully
- Check that the module name is `colosseum_bets`

### "Wallet not connecting"
- Install [Sui Wallet browser extension](https://chrome.google.com/webstore/detail/sui-wallet)
- Make sure wallet is on the same network as your app (devnet)

## Moving to Production (Mainnet)

1. **Switch to mainnet:**
   ```bash
   sui client switch --env mainnet
   ```

2. **Get real SUI tokens** (from exchange or bridge)

3. **Republish contract:**
   ```bash
   cd colosseum
   sui client publish --gas-budget 200000000
   ```

4. **Update `.env`:**
   ```env
   VITE_SUI_NETWORK=mainnet
   VITE_SUI_PACKAGE_ID=<NEW_MAINNET_PACKAGE_ID>
   VITE_SUI_HOUSE_ID=<NEW_MAINNET_HOUSE_ID>
   ```

5. **Seed mainnet house** with real SUI

## Admin Functions

### Withdraw from House (Admin Only)
```bash
sui client call \
  --package <PACKAGE_ID> \
  --module colosseum_bets \
  --function admin_withdraw \
  --args <HOUSE_ID> <RECIPIENT_ADDRESS> <AMOUNT_IN_MIST> \
  --gas-budget 100000000
```

Only the admin (deployer) can call this function.

## Monitoring

### Check House Balance
```bash
sui client object <HOUSE_ID> --json
```

Look for the `pot` field to see current balance.

### View Transaction Events
```bash
sui client events --module colosseum_bets
```

This shows all `BetPlaced` and `BetSettled` events.

## Resources

- [Sui Documentation](https://docs.sui.io/)
- [Sui Move by Example](https://examples.sui.io/)
- [Sui TypeScript SDK](https://sdk.mystenlabs.com/typescript)
- [Sui dApp Kit](https://sdk.mystenlabs.com/dapp-kit)
