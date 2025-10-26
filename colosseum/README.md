# Colosseum Betting - Sui Move Package

A decentralized betting platform built on Sui blockchain with on-chain randomness.

## Features

- **Shared House Object**: All bets pool into a shared house pot
- **On-Chain Randomness**: Uses Sui's native `Random` object for fair outcomes
- **Instant Settlement**: Place and settle bets in a single transaction (PTB)
- **2x Payout**: Win double your bet amount on correct prediction
- **Admin Controls**: House admin can withdraw funds

## Contract Structure

### Objects

**House** (Shared)
```move
struct House has key {
    id: UID,
    pot: Balance<SUI>,
    admin: address,
}
```

### Functions

**init(ctx: &mut TxContext)**
- Automatically called on publish
- Creates and shares the House object

**deposit(house: &mut House, coin_in: Coin<SUI>, _ctx: &mut TxContext)**
- Deposit SUI into the house pot
- Used to seed initial liquidity

**place_bet(house: &mut House, coin_in: Coin<SUI>, amount: u64, choice: u8, ctx: &mut TxContext)**
- Place a bet with choice 0 or 1
- Moves bet amount to house pot
- Emits `BetPlaced` event

**settle_bet(house: &mut House, r: &Random, player: address, amount: u64, choice: u8, ctx: &mut TxContext)**
- Settle a bet using on-chain randomness
- 50/50 chance, outcome is 0 or 1
- If win: pays 2x to player
- If lose: no payout (bet already in pot)
- Emits `BetSettled` event

**admin_withdraw(house: &mut House, to: address, amount: u64, ctx: &mut TxContext)**
- Admin-only function to withdraw from pot
- Reverts if caller is not the house admin

### Events

**BetPlaced**
```move
struct BetPlaced has copy, drop {
    player: address,
    amount: u64,
    choice: u8,
}
```

**BetSettled**
```move
struct BetSettled has copy, drop {
    player: address,
    amount: u64,
    choice: u8,
    outcome: u8,
    payout: u64,
}
```

## Building

```bash
sui move build
```

## Testing

```bash
sui move test
```

## Publishing

See [../DEPLOYMENT.md](../DEPLOYMENT.md) for full deployment guide.

Quick publish:
```bash
sui client publish --gas-budget 200000000
```

## Usage Examples

### Via CLI

**Deposit to House:**
```bash
sui client call \
  --package $PACKAGE_ID \
  --module colosseum_bets \
  --function deposit \
  --args $HOUSE_ID $COIN_ID \
  --gas-budget 100000000
```

**Place & Settle Bet:**
```bash
# Place bet
sui client call \
  --package $PACKAGE_ID \
  --module colosseum_bets \
  --function place_bet \
  --args $HOUSE_ID $COIN_ID 100000000 1 \
  --gas-budget 100000000

# Settle bet (use your address)
sui client call \
  --package $PACKAGE_ID \
  --module colosseum_bets \
  --function settle_bet \
  --args $HOUSE_ID 0x8 $YOUR_ADDRESS 100000000 1 \
  --gas-budget 100000000
```

### Via TypeScript

See `../src/sui/transactions.js` for client-side integration.

```typescript
import { buildPlaceAndSettleTx } from './sui/transactions';

const tx = buildPlaceAndSettleTx(
  BigInt(100_000_000), // 0.1 SUI in MIST
  1,                   // choice
  senderAddress
);

// Execute with wallet
await signAndExecuteTransaction({ transaction: tx });
```

## Security Considerations

1. **House Liquidity**: Ensure house pot has enough SUI to cover max payouts
2. **Admin Key**: Secure the admin private key (house deployer)
3. **Rate Limiting**: Consider adding cooldowns in production
4. **Max Bet**: Consider capping bet sizes to prevent pot drain

## Future Enhancements

- [ ] Multiple game modes (not just coin flip)
- [ ] Configurable odds and payouts
- [ ] House rake/fee percentage
- [ ] Player statistics and leaderboard
- [ ] Time-locked bets
- [ ] Multi-player tournaments
