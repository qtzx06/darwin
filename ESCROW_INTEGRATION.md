# Escrow Contract Frontend Integration

This document describes how the Sui escrow smart contract is integrated into the Darwin frontend.

## Overview

The escrow contract allows users to:
- Create escrow payments with SUI coins
- Accept escrow as recipient
- Cancel escrow as sender (before acceptance)
- Raise disputes with optional arbiter
- Set time-locks for delayed releases

## Architecture

### Contract Details
- **Package ID (Testnet)**: `0xbe33bcc611a0a24391f7d66b94b399631f46c62469073c74359ab840b0509fdd`
- **Module**: `escrow::escrow`
- **Network**: Sui Testnet

### Frontend Structure

```
src/
├── sui/
│   ├── config.js          # Network and package configuration
│   ├── escrow.js          # Transaction builders for escrow operations
│   └── transactions.js    # Existing transaction utilities
├── hooks/
│   └── useEscrow.js       # React hook for escrow operations
└── components/
    ├── EscrowDemo.jsx     # Demo UI component
    └── EscrowDemo.css     # Styling
```

## Key Files

### 1. `src/sui/config.js`
Configuration for the escrow contract:
```javascript
export const SUI_CONFIG = {
  ESCROW_PACKAGE_ID: '0xbe33bcc611a0a24391f7d66b94b399631f46c62469073c74359ab840b0509fdd',
  CLOCK_ID: '0x6',
  NETWORK: 'testnet',
  // ...
};
```

### 2. `src/sui/escrow.js`
Transaction builders that match the e2e test flow:

- `buildCreateEscrowTx()` - Creates shared escrow object
- `buildAcceptEscrowTx()` - Recipient accepts and receives funds
- `buildCancelEscrowTx()` - Sender cancels and reclaims funds
- `buildRaiseDisputeTx()` - Raises a dispute
- `buildResolveDisputeTx()` - Arbiter resolves dispute
- `parseEscrowEvents()` - Parses transaction events
- `extractEscrowObjectId()` - Extracts created escrow ID

### 3. `src/hooks/useEscrow.js`
React hook providing escrow operations:

```javascript
const {
  createEscrow,      // Create new escrow
  acceptEscrow,      // Accept as recipient
  cancelEscrow,      // Cancel as sender
  raiseDispute,      // Raise dispute
  resolveDispute,    // Resolve dispute (arbiter)
  isLoading,         // Loading state
  error,             // Error message
  lastResult,        // Last transaction result
} = useEscrow();
```

### 4. `src/components/EscrowDemo.jsx`
Demo component showing escrow usage:
- Create escrow form
- Accept/Cancel buttons
- Transaction status display

## Usage Examples

### Creating an Escrow

```javascript
import { useEscrow } from '../hooks/useEscrow';
import { useCurrentAccount } from '@mysten/dapp-kit';

function MyComponent() {
  const currentAccount = useCurrentAccount();
  const { createEscrow, isLoading } = useEscrow();
  
  const handleCreate = async () => {
    const result = await createEscrow(
      0.1,                          // Amount in SUI
      '0xrecipient...',             // Recipient address
      currentAccount.address,       // Current user address
      {
        description: 'Payment',     // Optional description
        arbiterAddress: null,       // Optional arbiter
        unlockTimeMs: null,         // Optional time-lock
      }
    );
    
    console.log('Escrow ID:', result.escrowId);
  };
  
  return (
    <button onClick={handleCreate} disabled={isLoading}>
      Create Escrow
    </button>
  );
}
```

### Accepting an Escrow

```javascript
const { acceptEscrow } = useEscrow();

const handleAccept = async (escrowId) => {
  await acceptEscrow(
    escrowId,
    currentAccount.address  // Recipient address
  );
};
```

### Cancelling an Escrow

```javascript
const { cancelEscrow } = useEscrow();

const handleCancel = async (escrowId) => {
  await cancelEscrow(
    escrowId,
    currentAccount.address  // Sender address
  );
};
```

## Transaction Flow

Based on the e2e tests, the transaction flow is:

1. **Create Escrow**:
   - Split SUI coin from gas
   - Call `escrow::create_shared<0x2::sui::SUI>`
   - Returns shared `EscrowObject` ID
   - Wait 2-3 seconds for object propagation

2. **Accept Escrow**:
   - Call `escrow::accept<0x2::sui::SUI>` with escrow ID and Clock
   - Returns `Coin<SUI>` which must be transferred to recipient
   - Escrow object is deleted after acceptance

3. **Cancel Escrow**:
   - Call `escrow::cancel<0x2::sui::SUI>` with escrow ID
   - Returns `Coin<SUI>` which must be transferred to sender
   - Escrow object is deleted after cancellation

## Important Notes

### Object Propagation Delay
After creating an escrow, wait 2-3 seconds before accepting/cancelling to allow the shared object to propagate across RPC nodes:

```javascript
await new Promise(r => setTimeout(r, 2000));
```

### Returned Coins Must Be Transferred
The `accept` and `cancel` functions return `Coin<SUI>` objects that **must** be transferred in the same transaction:

```javascript
const [releasedCoin] = tx.moveCall({ ... });
tx.transferObjects([releasedCoin], recipientAddress);
```

### Module Path
The correct module path is `escrow::create_shared`, not `escrow::escrow::create_shared`.

## Environment Variables

Add to your `.env` file:

```bash
VITE_ESCROW_PACKAGE_ID=0xbe33bcc611a0a24391f7d66b94b399631f46c62469073c74359ab840b0509fdd
VITE_SUI_NETWORK=testnet
```

## Testing

The integration mirrors the e2e test flow in `/escrow-contracts/e2e-tests/basic-escrow-test.ts`:

1. Alice creates escrow for Bob
2. Wait for propagation
3. Bob accepts escrow
4. Funds transferred to Bob

## Future Enhancements

- [ ] Add dispute resolution UI
- [ ] Show escrow status (pending/accepted/disputed)
- [ ] List user's active escrows
- [ ] Add time-lock countdown display
- [ ] Support for custom coin types (not just SUI)
- [ ] Arbiter dashboard
- [ ] Escrow history and analytics

## Troubleshooting

### "FunctionNotFound" Error
- Check module path is `escrow::create_shared` not `escrow::escrow::create_shared`

### "UnusedValueWithoutDrop" Error
- Ensure returned coins from `accept`/`cancel` are transferred in the same transaction

### "Object not found" Error
- Add 2-3 second delay after creating escrow before accepting/cancelling
- Verify escrow object ID is correct

### Transaction Fails Silently
- Check `result.effects.status.status` for failure details
- Look at `result.effects.status.error` for error message

## References

- E2E Tests: `/escrow-contracts/e2e-tests/`
- Move Contract: `/escrow-contracts/sources/escrow.move`
- Package ID: `0xbe33bcc611a0a24391f7d66b94b399631f46c62469073c74359ab840b0509fdd`
