# Escrow Contract Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Escrow Contract System                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │
        ┌─────────────────────┴─────────────────────┐
        │                                           │
        ▼                                           ▼
┌──────────────────┐                      ┌──────────────────┐
│  Standard Escrow │                      │   Atomic Swap    │
│  EscrowObject<T> │                      │ SwapEscrow<T1,T2>│
└──────────────────┘                      └──────────────────┘
        │                                           │
        │                                           │
   ┌────┴────┐                              ┌──────┴──────┐
   ▼         ▼                              ▼             ▼
Create   Accept                         Deposit A    Deposit B
Cancel   Dispute                        Execute      Cancel
```

## Standard Escrow Flow

### Happy Path
```
┌────────┐   create()    ┌──────────┐   accept()   ┌───────────┐
│ Sender │──────────────>│  Escrow  │─────────────>│ Recipient │
└────────┘               │ (shared) │              └───────────┘
                         └──────────┘
                              │
                              ├─> sender: address
                              ├─> recipient: address
                              ├─> balance: Balance<T>
                              ├─> accepted: false → true
                              └─> in_dispute: false
```

### Cancellation Path
```
┌────────┐   create()    ┌──────────┐   cancel()   ┌────────┐
│ Sender │──────────────>│  Escrow  │─────────────>│ Sender │
└────────┘               │ (shared) │  (refund)    └────────┘
                         └──────────┘
```

### Dispute Path
```
┌────────┐               ┌──────────┐              ┌─────────┐
│ Sender │───dispute()──>│  Escrow  │<──dispute()──│Recipient│
└────────┘               └─────┬────┘              └─────────┘
                               │
                               │ in_dispute: true
                               │
                               ▼
                         ┌──────────┐
                         │ Arbiter  │
                         └─────┬────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
            resolve(sender)       resolve(recipient)
```

## Time-Locked Escrow Flow

```
┌────────┐               ┌──────────────────┐
│ Sender │──create()────>│  Time-Locked     │
└────────┘               │  Escrow          │
                         │  unlock: T       │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
            Current < Unlock           Current ≥ Unlock
                    │                           │
                    ▼                           ▼
              EEscrowLocked                accept() ✓
```

## Atomic Swap Flow

```
Party A                        SwapEscrow                      Party B
   │                                │                              │
   │──create_swap()────────────────>│                              │
   │                                │                              │
   │──swap_deposit_a()─────────────>│                              │
   │                                │                              │
   │                                │<─────swap_deposit_b()────────│
   │                                │                              │
   │                                ▼                              │
   │                         Both deposited?                       │
   │                                │                              │
   │                       ┌────────┴────────┐                     │
   │                       ▼                 ▼                     │
   │                    Yes (execute)     No (wait/cancel)         │
   │                       │                                       │
   │<────transfer(B)───────┤                                       │
   │                       │                                       │
   │                       │─────transfer(A)──────────────────────>│
   │                       │                                       │
   │                    Completed                                  │
```

## State Machine

### EscrowObject States
```
        ┌─────────────────┐
        │    CREATED      │
        │ accepted: false │
        │ disputed: false │
        └────────┬────────┘
                 │
         ┌───────┼───────┐
         │       │       │
         ▼       ▼       ▼
    ┌────────┐ ┌───────┐ ┌─────────┐
    │ACCEPTED│ │DISPUTE│ │CANCELLED│
    │(final) │ │       │ │ (final) │
    └────────┘ └───┬───┘ └─────────┘
                   │
                   ▼
              ┌─────────┐
              │RESOLVED │
              │ (final) │
              └─────────┘
```

### SwapEscrow States
```
     ┌──────────────────┐
     │     CREATED      │
     │  dep_a: false    │
     │  dep_b: false    │
     └─────────┬────────┘
               │
       ┌───────┼───────┐
       │       │       │
       ▼       ▼       ▼
  ┌────────┐ ┌───┐ ┌────────┐
  │ A_ONLY │ │BOTH│ │ B_ONLY │
  └───┬────┘ └─┬─┘ └────┬───┘
      │        │        │
      ▼        ▼        ▼
   cancel   execute  cancel
```

## Function Access Control

```
Function              │ Sender │ Recipient │ Arbiter │ Anyone
──────────────────────┼────────┼───────────┼─────────┼────────
create_shared         │   ✓    │           │         │
accept                │        │     ✓     │         │
cancel                │   ✓    │           │         │
raise_dispute         │   ✓    │     ✓     │         │
resolve_dispute       │        │           │    ✓    │
create_swap           │   ✓    │           │         │
swap_deposit_a        │   ✓    │           │         │
swap_deposit_b        │        │     ✓     │         │
execute_swap          │        │           │         │   ✓
cancel_swap           │   ✓    │     ✓     │         │
```

## Data Flow

### Creating Escrow
```
Input: Coin<T>, recipient, arbiter?, unlock_time?, description
                          │
                          ▼
              ┌───────────────────────┐
              │ coin::into_balance()  │
              └───────────┬───────────┘
                          ▼
              ┌───────────────────────┐
              │  Create EscrowObject  │
              │  • Set sender         │
              │  • Set recipient      │
              │  • Store balance      │
              └───────────┬───────────┘
                          ▼
              ┌───────────────────────┐
              │ transfer::share_object│
              └───────────┬───────────┘
                          ▼
              ┌───────────────────────┐
              │  Emit EscrowCreated   │
              └───────────────────────┘
```

### Accepting Escrow
```
Input: &mut EscrowObject<T>, &Clock
                │
                ▼
      ┌─────────────────────┐
      │ Check recipient     │
      │ Check !accepted     │
      │ Check !disputed     │
      │ Check unlock_time   │
      └─────────┬───────────┘
                ▼
      ┌─────────────────────┐
      │ Set accepted = true │
      └─────────┬───────────┘
                ▼
      ┌─────────────────────┐
      │ withdraw_all()      │
      └─────────┬───────────┘
                ▼
      ┌─────────────────────┐
      │ coin::from_balance()│
      └─────────┬───────────┘
                ▼
      ┌─────────────────────┐
      │ Emit EscrowAccepted │
      └─────────┬───────────┘
                ▼
            Return Coin<T>
```

## Type System

```
Generic Type Parameters:
  T       = Coin type for standard escrow
  T1, T2  = Coin types for swap (can be different)

Key Types:
  EscrowObject<phantom T>      = Shared object, generic coin
  SwapEscrow<phantom T1, T2>   = Shared object, two generics
  Balance<T>                   = Efficient storage (vs Coin<T>)
  Option<address>              = Nullable arbiter
  Option<u64>                  = Nullable unlock time
```

## Event Architecture

```
All events have:
  • has copy, drop abilities
  • Minimal data for indexing
  • ID for tracking

Event Flow:
  Action → Emit → Blockchain → Indexer → Frontend
                                    │
                                    └──> Real-time updates
                                         Historical queries
```

## Error Handling Strategy

```
Error Pattern:
  assert!(condition, ERROR_CODE);

Error Hierarchy:
  ├─ Access Control (0-2)
  │  ├─ ENotSender
  │  ├─ ENotRecipient
  │  └─ ENotArbiter
  │
  ├─ State Validation (3-6)
  │  ├─ EAlreadyAccepted
  │  ├─ ENotAccepted
  │  ├─ EInDispute
  │  └─ ENotInDispute
  │
  └─ Business Logic (7-10)
     ├─ EEscrowLocked
     ├─ EInvalidAmount
     ├─ ESwapNotReady
     └─ ENotSwapParticipant
```

## Gas Optimization

```
Optimization                 │ Benefit
─────────────────────────────┼──────────────────
Use Balance<T> vs Coin<T>    │ Cheaper storage
Minimal state changes        │ Lower tx cost
Shared objects               │ Concurrent access
Event emission               │ Off-chain indexing
No loops                     │ O(1) operations
```

---

This architecture ensures:
- ✅ Type safety
- ✅ Access control
- ✅ State consistency
- ✅ Gas efficiency
- ✅ Transparency (events)
