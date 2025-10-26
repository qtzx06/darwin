# 🚀 Escrow Contracts Quick Start

Get started with Sui escrow contracts in 5 minutes!

## Prerequisites

```bash
# Install Sui CLI
cargo install --locked --git https://github.com/MystenLabs/sui.git --branch main sui

# Verify installation
sui --version
```

## Step 1: Build & Test

```bash
cd escrow-contracts

# Build the contracts
sui move build

# Run all tests
sui move test
```

You should see output like:
```
Running Move unit tests
[ PASS    ] escrow::escrow_tests::test_create_escrow
[ PASS    ] escrow::escrow_tests::test_accept_escrow
[ PASS    ] escrow::escrow_tests::test_cancel_escrow
...
Test result: OK. Total tests: 15; passed: 15; failed: 0
```

## Step 2: Deploy to Devnet

```bash
# Switch to devnet
sui client switch --env devnet

# Get test SUI tokens
sui client faucet

# Publish the package
sui client publish --gas-budget 200000000
```

**Save the Package ID** from the output!

## Step 3: Try a Simple Escrow

### Create an Escrow

```bash
# Set your package ID
export PACKAGE_ID=0xYOUR_PACKAGE_ID

# Set recipient address
export RECIPIENT=0xRECIPIENT_ADDRESS

# Get a coin to use
sui client gas

# Create escrow with 0.1 SUI
sui client call \
  --package $PACKAGE_ID \
  --module escrow \
  --function create_shared \
  --type-args 0x2::sui::SUI \
  --args YOUR_COIN_ID $RECIPIENT "[]" "[]" "0x5061796d656e74" \
  --gas-budget 100000000
```

**Save the Escrow Object ID** from the output!

### Accept the Escrow (as recipient)

```bash
export ESCROW_ID=0xYOUR_ESCROW_ID

sui client call \
  --package $PACKAGE_ID \
  --module escrow \
  --function accept \
  --type-args 0x2::sui::SUI \
  --args $ESCROW_ID 0x6 \
  --gas-budget 100000000
```

Done! The recipient now has the funds.

## Step 4: Try an Atomic Swap

### Create Swap (Party A)

```bash
export PARTY_B=0xPARTY_B_ADDRESS
export EXPIRATION=9999999999999  # Far future

# Create swap: 500 MIST for 1000 MIST
sui client call \
  --package $PACKAGE_ID \
  --module escrow \
  --function create_swap \
  --type-args 0x2::sui::SUI 0x2::sui::SUI \
  --args $PARTY_B 500 1000 $EXPIRATION \
  --gas-budget 100000000
```

**Save the Swap ID!**

### Party A Deposits

```bash
export SWAP_ID=0xYOUR_SWAP_ID

# Split exact amount
sui client split-coin --coin-id YOUR_COIN_ID --amounts 500
# Note the new coin ID

sui client call \
  --package $PACKAGE_ID \
  --module escrow \
  --function swap_deposit_a \
  --type-args 0x2::sui::SUI 0x2::sui::SUI \
  --args $SWAP_ID NEW_COIN_ID \
  --gas-budget 100000000
```

### Party B Deposits

```bash
# Switch to Party B's wallet or use different terminal
sui client switch --address $PARTY_B

# Split exact amount
sui client split-coin --coin-id PARTY_B_COIN_ID --amounts 1000

sui client call \
  --package $PACKAGE_ID \
  --module escrow \
  --function swap_deposit_b \
  --type-args 0x2::sui::SUI 0x2::sui::SUI \
  --args $SWAP_ID NEW_COIN_ID \
  --gas-budget 100000000
```

### Execute Swap

```bash
sui client call \
  --package $PACKAGE_ID \
  --module escrow \
  --function execute_swap \
  --type-args 0x2::sui::SUI 0x2::sui::SUI \
  --args $SWAP_ID 0x6 \
  --gas-budget 100000000
```

Done! Funds have been swapped atomically.

## Common Commands

### View Escrow Details
```bash
sui client object $ESCROW_ID --json
```

### View Events
```bash
sui client events --module escrow
```

### Cancel Escrow (as sender)
```bash
sui client call \
  --package $PACKAGE_ID \
  --module escrow \
  --function cancel \
  --type-args 0x2::sui::SUI \
  --args $ESCROW_ID \
  --gas-budget 100000000
```

### Raise Dispute
```bash
sui client call \
  --package $PACKAGE_ID \
  --module escrow \
  --function raise_dispute \
  --type-args 0x2::sui::SUI \
  --args $ESCROW_ID \
  --gas-budget 100000000
```

## TypeScript Integration

```typescript
import { Transaction } from '@mysten/sui/transactions';

// Create escrow
const tx = new Transaction();
const [coin] = tx.splitCoins(tx.gas, [100000000]); // 0.1 SUI

tx.moveCall({
  target: `${packageId}::escrow::create_shared`,
  typeArguments: ['0x2::sui::SUI'],
  arguments: [
    coin,
    tx.pure.address(recipient),
    tx.pure.option('address', null),
    tx.pure.option('u64', null),
    tx.pure(new TextEncoder().encode('Payment')),
  ],
});

await signAndExecuteTransaction({ transaction: tx });
```

## Troubleshooting

**"Insufficient gas"**
→ Request more: `sui client faucet`

**"Module not found"**
→ Check PACKAGE_ID is correct

**"Object not found"**
→ Check ESCROW_ID/SWAP_ID is correct

**"Wrong sender"**
→ Make sure you're using the right wallet address

## Next Steps

- Read [README.md](README.md) for full documentation
- Explore [tests/escrow_tests.move](tests/escrow_tests.move) for examples
- Deploy to mainnet for production use
- Build a frontend UI for your escrows

---

Happy escrow-ing! 🎉
