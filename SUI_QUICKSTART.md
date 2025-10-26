# 🚀 Sui Betting Quick Start

Get your Darwin betting app running in 5 minutes!

## Prerequisites

- Node.js installed
- Sui CLI installed ([guide](https://docs.sui.io/guides/developer/getting-started/sui-install))
- Sui wallet browser extension ([download](https://chrome.google.com/webstore/detail/sui-wallet))

## Step 1: Install Dependencies

```bash
npm install
```

## Step 2: Deploy Smart Contract

**Easiest: Use the script**
```bash
./scripts/deploy-sui.sh
```

**Or manually:**
```bash
# Build
cd colosseum && sui move build

# Publish to devnet
sui client publish --gas-budget 200000000
```

Copy the **Package ID** and **House Object ID** from the output.

## Step 3: Configure App

```bash
# Create .env file
cp .env.example .env

# Edit .env with your values
nano .env
```

Add your IDs:
```env
VITE_SUI_NETWORK=devnet
VITE_SUI_PACKAGE_ID=0xYOUR_PACKAGE_ID_HERE
VITE_SUI_HOUSE_ID=0xYOUR_HOUSE_ID_HERE
```

## Step 4: Seed the House

The house needs SUI to pay winners:

```bash
# Get test SUI
sui client faucet

# Check your coins
sui client gas

# Deposit 10 SUI to house
sui client split-coin --coin-id <COIN_ID> --amounts 10000000000
sui client call \
  --package <PACKAGE_ID> \
  --module colosseum_bets \
  --function deposit \
  --args <HOUSE_ID> <NEW_COIN_ID> \
  --gas-budget 100000000
```

## Step 5: Run the App

```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

## Step 6: Place Your First Bet

1. Click **"Connect Wallet"** (top-right)
2. Connect your Sui wallet
3. Select bet amount (0.1 SUI to start)
4. Click **0** or **1**
5. Approve transaction in wallet popup
6. See your result!

## 🎉 You're Done!

The app is now running with real on-chain betting.

## Need Help?

- **Full guide**: See [DEPLOYMENT.md](./DEPLOYMENT.md)
- **Integration details**: See [SUI_INTEGRATION.md](./SUI_INTEGRATION.md)
- **Contract docs**: See [colosseum/README.md](./colosseum/README.md)

## Common Issues

**"Wallet won't connect"**
→ Install [Sui Wallet extension](https://chrome.google.com/webstore/detail/sui-wallet)

**"Transaction failed"**
→ Make sure house has enough SUI (Step 4)

**"Out of gas"**
→ Get more test SUI: `sui client faucet`

**Build errors**
→ Make sure you ran `npm install` after cloning

## Next Steps

- Add more game modes
- Customize UI styling
- Deploy to mainnet (see DEPLOYMENT.md)
- Add house rake/fees
- Implement leaderboards

---

**Pro tip**: Test everything on devnet before going to mainnet!
