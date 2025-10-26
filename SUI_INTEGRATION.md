# Sui Blockchain Integration

Darwin now features **on-chain betting** powered by Sui blockchain! Users can place bets with real SUI cryptocurrency using a simple 0-or-1 game with 50/50 odds and 2x payouts.

## 🎯 What's New

### Smart Contract (`colosseum/`)
- **Move package** with betting logic and shared house pot
- **On-chain randomness** using Sui's native Random object
- **Instant settlement** via Programmable Transaction Blocks (PTBs)
- **Admin controls** for house management

### Frontend Components
- **WalletButton** - Connect Sui wallets (top-right corner)
- **BettingPanel** - Place bets with choice selection and amount input
- **Transaction handling** - Real-time bet results and payout display

### Features
- 🎲 **Provably Fair** - On-chain randomness, no backend manipulation
- ⚡ **Instant Results** - Place and settle in single transaction
- 💰 **2x Payouts** - Win double your bet on correct guess
- 🔒 **Decentralized** - No central authority controlling funds
- 📱 **Mobile Friendly** - Responsive betting interface

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ WalletButton │  │ BettingPanel │  │   App.jsx    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
│                    @mysten/dapp-kit                          │
│                            │                                 │
└────────────────────────────┼─────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  Sui Blockchain │
                    │   (devnet/      │
                    │   mainnet)      │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
       ┌──────▼──────┐ ┌────▼────┐ ┌──────▼──────┐
       │   House     │ │ Random  │ │   Events    │
       │  (shared)   │ │ (0x8)   │ │ BetPlaced   │
       │             │ │         │ │ BetSettled  │
       └─────────────┘ └─────────┘ └─────────────┘
```

## 📁 File Structure

```
darwin/
├── colosseum/                      # Sui Move package
│   ├── Move.toml                   # Package manifest
│   ├── sources/
│   │   └── colosseum_bets.move     # Main betting contract
│   └── README.md                   # Contract documentation
│
├── src/
│   ├── sui/
│   │   ├── config.js               # Network & contract config
│   │   └── transactions.js         # Transaction builders
│   │
│   ├── components/
│   │   ├── WalletButton.jsx        # Wallet connection UI
│   │   ├── WalletButton.css
│   │   ├── BettingPanel.jsx        # Betting interface
│   │   └── BettingPanel.css
│   │
│   ├── main.jsx                    # Sui providers setup
│   └── App.jsx                     # Main app with betting integration
│
├── scripts/
│   └── deploy-sui.sh               # Automated deployment script
│
├── .env.example                    # Environment template
├── DEPLOYMENT.md                   # Step-by-step deployment guide
└── SUI_INTEGRATION.md             # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
npm install
```

This includes:
- `@mysten/sui.js` - Sui TypeScript SDK
- `@mysten/dapp-kit` - React hooks for Sui wallets
- `@tanstack/react-query` - Required by dapp-kit

### 2. Deploy Smart Contract

**Option A: Automated Script**
```bash
./scripts/deploy-sui.sh
```

**Option B: Manual Deployment**
```bash
cd colosseum
sui move build
sui client publish --gas-budget 200000000
```

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions.

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your deployed contract details:
```env
VITE_SUI_NETWORK=devnet
VITE_SUI_PACKAGE_ID=0xYOUR_PACKAGE_ID
VITE_SUI_HOUSE_ID=0xYOUR_HOUSE_ID
```

### 4. Seed the House (Important!)

The house needs SUI to pay winners:

```bash
# Get a coin ID
sui client gas

# Split 10 SUI for the house
sui client split-coin --coin-id <COIN_ID> --amounts 10000000000 --gas-budget 100000000

# Deposit to house
sui client call \
  --package <PACKAGE_ID> \
  --module colosseum_bets \
  --function deposit \
  --args <HOUSE_ID> <SPLIT_COIN_ID> \
  --gas-budget 100000000
```

### 5. Run the App

```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) and:
1. Click **Connect Wallet** (top-right)
2. Install [Sui Wallet](https://chrome.google.com/webstore/detail/sui-wallet) if needed
3. Connect your wallet
4. Place a bet!

## 🎮 How to Play

1. **Connect your Sui wallet** - Click the wallet button in top-right
2. **Choose bet amount** - Select preset (0.1, 0.5, 1.0, 5.0 SUI) or enter custom amount
3. **Pick 0 or 1** - Click your choice to submit bet
4. **Approve transaction** - Confirm in your wallet popup
5. **See result** - Win or lose animation with payout details

### Game Rules

- **Odds**: 50/50 (fair coin flip)
- **Payout**: 2x your bet if you win
- **Minimum**: 0.1 SUI
- **Speed**: Instant settlement (one transaction)

## 🔧 Development

### Testing Locally

You can test the contract without the UI:

```bash
# Place a bet
sui client call \
  --package <PACKAGE_ID> \
  --module colosseum_bets \
  --function place_bet \
  --args <HOUSE_ID> <COIN_ID> 100000000 1 \
  --gas-budget 100000000

# Settle the bet
sui client call \
  --package <PACKAGE_ID> \
  --module colosseum_bets \
  --function settle_bet \
  --args <HOUSE_ID> 0x8 <YOUR_ADDRESS> 100000000 1 \
  --gas-budget 100000000
```

### Monitoring

**Check house balance:**
```bash
sui client object <HOUSE_ID> --json | jq '.data.content.fields.pot'
```

**View bet events:**
```bash
sui client events --module colosseum_bets
```

**View transaction history:**
```bash
sui client txns --to-address <YOUR_ADDRESS>
```

## 🔐 Security

### Smart Contract
- ✅ Uses Sui's native `Random` object (cryptographically secure)
- ✅ Shared object for atomic state updates
- ✅ Admin-only withdrawal function
- ⚠️ No rate limiting (add in production)
- ⚠️ No max bet cap (consider adding)

### Frontend
- ✅ Read-only contract calls don't need wallet approval
- ✅ All state-changing calls require explicit user approval
- ✅ Transaction amounts displayed before signing
- ⚠️ Always verify wallet popup matches expected transaction

### Best Practices
1. **Test on devnet first** - Never deploy untested code to mainnet
2. **Audit smart contracts** - Get professional audit before mainnet launch
3. **Limit house pot** - Don't put more SUI than you can afford to lose
4. **Monitor activity** - Watch for unusual betting patterns
5. **Secure admin keys** - House admin controls all funds

## 📊 Economics

### House Pot Management

**Initial Seeding:**
- Minimum: 10 SUI (covers ~5 max bets @ 1 SUI each)
- Recommended: 50-100 SUI for smooth operations

**House Edge:**
- Current: 0% (fair game, no house fee)
- Future: Add configurable rake (e.g., 2-5%)

**Sustainability:**
- With 0% edge, house breaks even long-term
- Add house fee to ensure profitability
- Monitor pot balance and refill as needed

### Example Fee Implementation

To add a 5% house fee, modify `settle_bet`:

```move
if (outcome == choice) {
    let gross_payout = amount * 2;
    let fee = gross_payout * 5 / 100;  // 5% fee
    payout_amt = gross_payout - fee;
    // ... transfer payout_amt to player
}
```

## 🌐 Going to Production

### Mainnet Checklist

- [ ] Full contract audit by security firm
- [ ] Add house rake/fee system
- [ ] Implement rate limiting
- [ ] Add max bet caps
- [ ] Set up monitoring/alerts
- [ ] Legal compliance review
- [ ] Obtain sufficient SUI for house pot
- [ ] Test all edge cases on testnet
- [ ] Deploy to mainnet
- [ ] Update frontend config
- [ ] Announce launch!

### Mainnet Deployment

```bash
# Switch network
sui client switch --env mainnet

# Publish
cd colosseum
sui client publish --gas-budget 200000000

# Update .env
VITE_SUI_NETWORK=mainnet
VITE_SUI_PACKAGE_ID=<NEW_PACKAGE_ID>
VITE_SUI_HOUSE_ID=<NEW_HOUSE_ID>

# Seed house with real SUI
# ... (see DEPLOYMENT.md)
```

## 🛠️ Customization

### Change Game Odds

Edit `colosseum/sources/colosseum_bets.move`:

```move
// Change to 1/3 chance (0, 1, or 2)
let outcome = random::generate_u8_in_range(&mut gen, 0, 3);
```

### Adjust Payouts

```move
// Change to 3x payout
payout_amt = amount * 3;
```

### Add New Betting Options

1. Add new game logic in Move contract
2. Update `BET_CHOICES` in `src/sui/config.js`
3. Modify `BettingPanel.jsx` UI
4. Update transaction builders in `src/sui/transactions.js`

## 📚 Resources

- **Sui Documentation**: https://docs.sui.io/
- **Move Language**: https://move-language.github.io/move/
- **Sui TypeScript SDK**: https://sdk.mystenlabs.com/typescript
- **dApp Kit**: https://sdk.mystenlabs.com/dapp-kit
- **Sui Explorer**: https://suiexplorer.com/ (view transactions)
- **Sui Faucet**: https://faucet.sui.io/ (get test tokens)

## 🐛 Troubleshooting

See [DEPLOYMENT.md](./DEPLOYMENT.md) for common issues and solutions.

**Quick Fixes:**
- Wallet won't connect → Install Sui Wallet extension
- Transaction fails → Check house pot has enough SUI
- "Module not found" → Verify PACKAGE_ID in .env
- "Object not found" → Verify HOUSE_ID in .env
- Out of gas → Request more from faucet (devnet)

## 🎯 Future Ideas

- 🎰 **Multiple games** - Roulette, dice, slots
- 🏆 **Leaderboards** - Track top players on-chain
- 🎁 **Rewards** - Loyalty tokens for frequent players
- 👥 **Multiplayer** - Head-to-head betting
- 📈 **Statistics** - Win rates, total volume charts
- 🔔 **Notifications** - Real-time bet results
- 💬 **Chat** - Social features for players

---

Built with ❤️ on Sui blockchain
