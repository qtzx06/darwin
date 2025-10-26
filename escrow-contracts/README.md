# Sui Escrow Contracts

A comprehensive, production-ready escrow system for Sui blockchain with full test coverage.

## Features

### 🔒 Standard Escrow
- **Sender → Recipient** transfers with optional arbiter
- **Time-locked escrows** with unlock timestamps
- **Cancellable** before acceptance
- **Dispute resolution** with neutral arbiter
- Works with **SUI and any custom coin type**

### 🔄 Atomic Swaps
- **Two-party exchanges** with guaranteed atomicity
- **Expiration times** to prevent indefinite locks
- **Partial deposit refunds** if swap fails
- **Type-safe** cross-asset swaps

### ✅ Security Features
- Access control on all operations
- Time-lock enforcement
- Dispute protection
- Event emission for transparency
- Comprehensive error handling

## Installation

### Prerequisites
```bash
# Install Sui CLI
cargo install --locked --git https://github.com/MystenLabs/sui.git --branch main sui

# Set up Sui wallet
sui client
```

### Build
```bash
cd escrow-contracts
sui move build
```

### Test
```bash
sui move test
```

### Publish
```bash
sui client publish --gas-budget 200000000
```

## Contract Architecture

### Core Objects

#### `EscrowObject<T>`
Standard escrow holding coins from sender to recipient.

```move
public struct EscrowObject<phantom T> has key, store {
    id: UID,
    sender: address,           // Creator and funder
    recipient: address,        // Can accept funds
    arbiter: Option<address>,  // Optional dispute resolver
    balance: Balance<T>,       // Escrowed funds
    accepted: bool,            // Acceptance status
    in_dispute: bool,          // Dispute flag
    unlock_time: Option<u64>,  // Optional time-lock (epoch ms)
    description: vector<u8>,   // Memo field
}
```

#### `SwapEscrow<T1, T2>`
Two-party atomic swap of different coin types.

```move
public struct SwapEscrow<phantom T1, phantom T2> has key {
    id: UID,
    party_a: address,          // First party
    party_b: address,          // Second party
    balance_a: Balance<T1>,    // Party A's funds
    balance_b: Balance<T2>,    // Party B's funds
    deposited_a: bool,         // A's deposit status
    deposited_b: bool,         // B's deposit status
    amount_a: u64,             // Expected from A
    amount_b: u64,             // Expected from B
    expiration: u64,           // Swap deadline
}
```

## Usage Examples

### 1. Basic Escrow (Shared Object)

```move
// Sender creates escrow
public entry fun create_shared<T>(
    coin: Coin<T>,
    recipient: address,
    arbiter: Option<address>,
    unlock_time: Option<u64>,
    description: vector<u8>,
    ctx: &mut TxContext
)
```

**CLI Example:**
```bash
sui client call \
  --package $PACKAGE_ID \
  --module escrow \
  --function create_shared \
  --type-args 0x2::sui::SUI \
  --args $COIN_ID $RECIPIENT_ADDR "[]" "[]" "0x48656c6c6f" \
  --gas-budget 100000000
```

**TypeScript Example:**
```typescript
const tx = new Transaction();
const [coin] = tx.splitCoins(tx.gas, [1000000000]); // 1 SUI

tx.moveCall({
  target: `${packageId}::escrow::create_shared`,
  typeArguments: ['0x2::sui::SUI'],
  arguments: [
    coin,
    tx.pure.address(recipientAddr),
    tx.pure.option('address', null), // no arbiter
    tx.pure.option('u64', null),     // no time-lock
    tx.pure(new TextEncoder().encode('Payment for services')),
  ],
});
```

### 2. Recipient Accepts Escrow

```move
public fun accept<T>(
    escrow: &mut EscrowObject<T>,
    clock: &Clock,
    ctx: &TxContext
): Coin<T>
```

**CLI Example:**
```bash
sui client call \
  --package $PACKAGE_ID \
  --module escrow \
  --function accept \
  --type-args 0x2::sui::SUI \
  --args $ESCROW_ID 0x6 \
  --gas-budget 100000000
```

**TypeScript Example:**
```typescript
const tx = new Transaction();

tx.moveCall({
  target: `${packageId}::escrow::accept`,
  typeArguments: ['0x2::sui::SUI'],
  arguments: [
    tx.object(escrowId),
    tx.object('0x6'), // Clock object
  ],
});
```

### 3. Sender Cancels Escrow

```move
public fun cancel<T>(
    escrow: &mut EscrowObject<T>,
    ctx: &TxContext
): Coin<T>
```

**CLI Example:**
```bash
sui client call \
  --package $PACKAGE_ID \
  --module escrow \
  --function cancel \
  --type-args 0x2::sui::SUI \
  --args $ESCROW_ID \
  --gas-budget 100000000
```

### 4. Raise Dispute

```move
public entry fun raise_dispute<T>(
    escrow: &mut EscrowObject<T>,
    ctx: &TxContext
)
```

**Requirements:**
- Escrow must have an arbiter
- Called by sender or recipient
- Cannot already be accepted

**CLI Example:**
```bash
sui client call \
  --package $PACKAGE_ID \
  --module escrow \
  --function raise_dispute \
  --type-args 0x2::sui::SUI \
  --args $ESCROW_ID \
  --gas-budget 100000000
```

### 5. Arbiter Resolves Dispute

```move
public fun resolve_dispute<T>(
    escrow: &mut EscrowObject<T>,
    award_to_sender: bool,
    ctx: &TxContext
): Coin<T>
```

**CLI Example:**
```bash
# Award to sender
sui client call \
  --package $PACKAGE_ID \
  --module escrow \
  --function resolve_dispute \
  --type-args 0x2::sui::SUI \
  --args $ESCROW_ID true \
  --gas-budget 100000000

# Award to recipient
sui client call \
  --package $PACKAGE_ID \
  --module escrow \
  --function resolve_dispute \
  --type-args 0x2::sui::SUI \
  --args $ESCROW_ID false \
  --gas-budget 100000000
```

### 6. Atomic Swap

**Step 1: Create Swap**
```move
public entry fun create_swap<T1, T2>(
    party_b: address,
    amount_a: u64,
    amount_b: u64,
    expiration: u64,
    ctx: &mut TxContext
)
```

**Step 2: Party A Deposits**
```move
public entry fun swap_deposit_a<T1, T2>(
    swap: &mut SwapEscrow<T1, T2>,
    coin: Coin<T1>,
    ctx: &TxContext
)
```

**Step 3: Party B Deposits**
```move
public entry fun swap_deposit_b<T1, T2>(
    swap: &mut SwapEscrow<T1, T2>,
    coin: Coin<T2>,
    ctx: &TxContext
)
```

**Step 4: Execute Swap**
```move
public entry fun execute_swap<T1, T2>(
    swap: &mut SwapEscrow<T1, T2>,
    clock: &Clock,
    ctx: &mut TxContext
)
```

**Full Example:**
```bash
# Party A creates swap: 500 COIN_A for 1000 COIN_B
sui client call \
  --package $PACKAGE_ID \
  --module escrow \
  --function create_swap \
  --type-args $COIN_A_TYPE $COIN_B_TYPE \
  --args $PARTY_B_ADDR 500 1000 $EXPIRATION_TIME \
  --gas-budget 100000000

# Party A deposits
sui client call \
  --package $PACKAGE_ID \
  --module escrow \
  --function swap_deposit_a \
  --type-args $COIN_A_TYPE $COIN_B_TYPE \
  --args $SWAP_ID $COIN_A_ID \
  --gas-budget 100000000

# Party B deposits
sui client call \
  --package $PACKAGE_ID \
  --module escrow \
  --function swap_deposit_b \
  --type-args $COIN_A_TYPE $COIN_B_TYPE \
  --args $SWAP_ID $COIN_B_ID \
  --gas-budget 100000000

# Execute swap
sui client call \
  --package $PACKAGE_ID \
  --module escrow \
  --function execute_swap \
  --type-args $COIN_A_TYPE $COIN_B_TYPE \
  --args $SWAP_ID 0x6 \
  --gas-budget 100000000
```

## Events

### EscrowCreated
```move
public struct EscrowCreated has copy, drop {
    escrow_id: ID,
    sender: address,
    recipient: address,
    amount: u64,
}
```

### EscrowAccepted
```move
public struct EscrowAccepted has copy, drop {
    escrow_id: ID,
    recipient: address,
}
```

### EscrowCancelled
```move
public struct EscrowCancelled has copy, drop {
    escrow_id: ID,
    sender: address,
}
```

### EscrowDisputed
```move
public struct EscrowDisputed has copy, drop {
    escrow_id: ID,
    initiator: address,
}
```

### EscrowResolved
```move
public struct EscrowResolved has copy, drop {
    escrow_id: ID,
    winner: address,
}
```

### SwapCreated
```move
public struct SwapCreated has copy, drop {
    swap_id: ID,
    party_a: address,
    party_b: address,
}
```

### SwapCompleted
```move
public struct SwapCompleted has copy, drop {
    swap_id: ID,
}
```

## Testing

The project includes comprehensive tests covering:

### Basic Escrow Tests
- ✅ Creating escrow with correct properties
- ✅ Recipient acceptance
- ✅ Sender cancellation
- ✅ Access control (wrong recipient/sender)
- ✅ Cannot cancel after acceptance

### Time-Lock Tests
- ✅ Accepting unlocked escrow
- ✅ Rejecting locked escrow

### Dispute Resolution Tests
- ✅ Raising disputes
- ✅ Resolving in favor of sender
- ✅ Resolving in favor of recipient
- ✅ Cannot accept during dispute

### Swap Tests
- ✅ Successful atomic swap
- ✅ Partial deposit cancellation
- ✅ Cannot execute unready swap

**Run tests:**
```bash
sui move test

# Verbose output
sui move test -v

# Specific test
sui move test test_accept_escrow
```

## Error Codes

| Code | Constant | Description |
|------|----------|-------------|
| 0 | `ENotSender` | Caller is not the sender |
| 1 | `ENotRecipient` | Caller is not the recipient |
| 2 | `ENotArbiter` | Caller is not the arbiter |
| 3 | `EAlreadyAccepted` | Escrow already accepted |
| 4 | `ENotAccepted` | Escrow not yet accepted |
| 5 | `EInDispute` | Escrow is in dispute |
| 6 | `ENotInDispute` | Escrow is not in dispute |
| 7 | `EEscrowLocked` | Time-lock not yet expired |
| 8 | `EInvalidAmount` | Invalid coin amount |
| 9 | `ESwapNotReady` | Swap not fully deposited |
| 10 | `ENotSwapParticipant` | Caller not party to swap |

## Use Cases

### 1. Service Payments
```
Freelancer (recipient) ← Client (sender)
• Client creates escrow
• Freelancer completes work
• Freelancer accepts payment
```

### 2. Marketplace Transactions
```
Buyer (sender) → Seller (recipient) with Arbiter
• Buyer creates escrow with platform as arbiter
• Seller ships product
• Buyer accepts on delivery
• Or raises dispute if issue
```

### 3. Time-Locked Vesting
```
Employee (recipient) ← Company (sender)
• Company creates time-locked escrow
• Employee can accept after unlock date
```

### 4. NFT/Token Swaps
```
Alice (500 Token A) ↔ Bob (1000 Token B)
• Alice creates swap
• Both deposit
• Swap executes atomically
```

## Security Considerations

### Access Control
- ✅ All functions check `ctx.sender()`
- ✅ Only authorized parties can perform actions
- ✅ No reentrancy risks (Move's resource model)

### Time Safety
- ✅ Clock object required for time checks
- ✅ Cannot bypass time-locks
- ✅ Swap expirations enforced

### Fund Safety
- ✅ Balances tracked accurately
- ✅ No double-withdrawals possible
- ✅ All coins accounted for

### Recommendations
1. **Use arbiters** for high-value escrows
2. **Set reasonable time-locks** for vesting
3. **Test on devnet** before mainnet
4. **Monitor events** for escrow lifecycle
5. **Set swap expirations** to prevent locks

## Gas Optimization

- Uses `Balance<T>` instead of `Coin<T>` for storage
- Minimal state changes
- Event emission is efficient
- No unnecessary object creation

## Future Enhancements

- [ ] Multi-signature escrows (m-of-n)
- [ ] Partial releases (milestone payments)
- [ ] Escrow templates for common use cases
- [ ] Fee system for arbiter compensation
- [ ] Batch escrow operations
- [ ] Cross-chain escrows (with bridges)

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Ensure all tests pass: `sui move test`
5. Submit pull request

## License

MIT License - See LICENSE file for details

## Support

- **Documentation**: [Sui Move Docs](https://docs.sui.io/concepts/sui-move-concepts)
- **Issues**: GitHub Issues
- **Discord**: [Sui Discord](https://discord.gg/sui)

---

Built with ❤️ on Sui blockchain
