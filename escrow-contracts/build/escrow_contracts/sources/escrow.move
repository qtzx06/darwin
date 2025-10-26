/// Escrow Module - Secure third-party held transactions on Sui
///
/// Features:
/// - SUI and generic coin escrow
/// - Cancellable by sender before acceptance
/// - Dispute resolution with arbiter
/// - Time-locked escrows
/// - Swap escrows (two-party atomic swaps)

module escrow::escrow {
    use sui::coin::{Self, Coin};
    use sui::balance::{Self, Balance};
    use sui::sui::SUI;
    use sui::clock::{Self, Clock};
    use sui::event;
    use sui::object::{Self, UID};
    use sui::tx_context::{Self, TxContext};
    use sui::transfer;
    use std::option::{Self, Option};

    // ==================== Error Codes ====================

    const ENotSender: u64 = 0;
    const ENotRecipient: u64 = 1;
    const ENotArbiter: u64 = 2;
    const EAlreadyAccepted: u64 = 3;
    const ENotAccepted: u64 = 4;
    const EInDispute: u64 = 5;
    const ENotInDispute: u64 = 6;
    const EEscrowLocked: u64 = 7;
    const EInvalidAmount: u64 = 8;
    const ESwapNotReady: u64 = 9;
    const ENotSwapParticipant: u64 = 10;

    // ==================== Structs ====================

    /// Standard escrow object holding coins from sender to recipient
    public struct EscrowObject<phantom T> has key, store {
        id: UID,
        /// Address that created and funded the escrow
        sender: address,
        /// Address that can accept the escrow
        recipient: address,
        /// Optional arbiter for dispute resolution
        arbiter: Option<address>,
        /// Escrowed funds
        balance: Balance<T>,
        /// Whether recipient has accepted
        accepted: bool,
        /// Whether escrow is in dispute
        in_dispute: bool,
        /// Optional unlock timestamp (epoch ms)
        unlock_time: Option<u64>,
        /// Optional description/memo
        description: vector<u8>,
    }

    /// Swap escrow for atomic two-party exchanges
    public struct SwapEscrow<phantom T1, phantom T2> has key {
        id: UID,
        /// Party A's address
        party_a: address,
        /// Party B's address
        party_b: address,
        /// Party A's escrowed funds
        balance_a: Balance<T1>,
        /// Party B's escrowed funds
        balance_b: Balance<T2>,
        /// Party A has deposited
        deposited_a: bool,
        /// Party B has deposited
        deposited_b: bool,
        /// Expected amount from party A
        amount_a: u64,
        /// Expected amount from party B
        amount_b: u64,
        /// Swap expiration timestamp
        expiration: u64,
    }

    // ==================== Events ====================

    public struct EscrowCreated has copy, drop {
        escrow_id: ID,
        sender: address,
        recipient: address,
        amount: u64,
    }

    public struct EscrowAccepted has copy, drop {
        escrow_id: ID,
        recipient: address,
    }

    public struct EscrowCancelled has copy, drop {
        escrow_id: ID,
        sender: address,
    }

    public struct EscrowDisputed has copy, drop {
        escrow_id: ID,
        initiator: address,
    }

    public struct EscrowResolved has copy, drop {
        escrow_id: ID,
        winner: address,
    }

    public struct SwapCreated has copy, drop {
        swap_id: ID,
        party_a: address,
        party_b: address,
    }

    public struct SwapCompleted has copy, drop {
        swap_id: ID,
    }

    // ==================== Public Functions ====================

    /// Create a new escrow with SUI or generic coin
    public fun create<T>(
        coin: Coin<T>,
        recipient: address,
        arbiter: Option<address>,
        unlock_time: Option<u64>,
        description: vector<u8>,
        ctx: &mut TxContext
    ): EscrowObject<T> {
        let amount = coin::value(&coin);
        assert!(amount > 0, EInvalidAmount);

        let escrow_id = object::new(ctx);
        let id_copy = object::uid_to_inner(&escrow_id);

        event::emit(EscrowCreated {
            escrow_id: id_copy,
            sender: tx_context::sender(ctx),
            recipient,
            amount,
        });

        EscrowObject {
            id: escrow_id,
            sender: tx_context::sender(ctx),
            recipient,
            arbiter,
            balance: coin::into_balance(coin),
            accepted: false,
            in_dispute: false,
            unlock_time,
            description,
        }
    }

    /// Create and share a new escrow
    public entry fun create_shared<T>(
        coin: Coin<T>,
        recipient: address,
        arbiter: Option<address>,
        unlock_time: Option<u64>,
        description: vector<u8>,
        ctx: &mut TxContext
    ) {
        let escrow = create(coin, recipient, arbiter, unlock_time, description, ctx);
        transfer::share_object(escrow);
    }

    /// Recipient accepts the escrow (time-lock check)
    public fun accept<T>(
        escrow: &mut EscrowObject<T>,
        clock: &Clock,
        ctx: &mut TxContext
    ): Coin<T> {
        assert!(tx_context::sender(ctx) == escrow.recipient, ENotRecipient);
        assert!(!escrow.accepted, EAlreadyAccepted);
        assert!(!escrow.in_dispute, EInDispute);

        // Check time lock
        if (escrow.unlock_time.is_some()) {
            let unlock = escrow.unlock_time.destroy_some();
            assert!(clock::timestamp_ms(clock) >= unlock, EEscrowLocked);
        };

        escrow.accepted = true;
        let amount = balance::value(&escrow.balance);

        event::emit(EscrowAccepted {
            escrow_id: object::uid_to_inner(&escrow.id),
            recipient: tx_context::sender(ctx),
        });

        coin::from_balance(balance::withdraw_all(&mut escrow.balance), ctx)
    }

    /// Sender cancels escrow before acceptance
    public fun cancel<T>(
        escrow: &mut EscrowObject<T>,
        ctx: &mut TxContext
    ): Coin<T> {
        assert!(tx_context::sender(ctx) == escrow.sender, ENotSender);
        assert!(!escrow.accepted, EAlreadyAccepted);
        assert!(!escrow.in_dispute, EInDispute);

        event::emit(EscrowCancelled {
            escrow_id: object::uid_to_inner(&escrow.id),
            sender: tx_context::sender(ctx),
        });

        coin::from_balance(balance::withdraw_all(&mut escrow.balance), ctx)
    }

    /// Either party can raise a dispute (requires arbiter)
    public entry fun raise_dispute<T>(
        escrow: &mut EscrowObject<T>,
        ctx: &TxContext
    ) {
        let sender = tx_context::sender(ctx);
        assert!(
            sender == escrow.sender || sender == escrow.recipient,
            ENotSender
        );
        assert!(!escrow.accepted, EAlreadyAccepted);
        assert!(escrow.arbiter.is_some(), ENotArbiter);

        escrow.in_dispute = true;

        event::emit(EscrowDisputed {
            escrow_id: object::uid_to_inner(&escrow.id),
            initiator: sender,
        });
    }

    /// Arbiter resolves dispute in favor of sender or recipient
    public fun resolve_dispute<T>(
        escrow: &mut EscrowObject<T>,
        award_to_sender: bool,
        ctx: &mut TxContext
    ): Coin<T> {
        assert!(escrow.in_dispute, ENotInDispute);
        assert!(escrow.arbiter.is_some(), ENotArbiter);

        let arbiter = *escrow.arbiter.borrow();
        assert!(tx_context::sender(ctx) == arbiter, ENotArbiter);

        let winner = if (award_to_sender) { escrow.sender } else { escrow.recipient };

        event::emit(EscrowResolved {
            escrow_id: object::uid_to_inner(&escrow.id),
            winner,
        });

        escrow.in_dispute = false;
        coin::from_balance(balance::withdraw_all(&mut escrow.balance), ctx)
    }

    /// Create a swap escrow for atomic two-party exchange
    public entry fun create_swap<T1, T2>(
        party_b: address,
        amount_a: u64,
        amount_b: u64,
        expiration: u64,
        ctx: &mut TxContext
    ) {
        let swap_id = object::new(ctx);
        let id_copy = object::uid_to_inner(&swap_id);

        event::emit(SwapCreated {
            swap_id: id_copy,
            party_a: tx_context::sender(ctx),
            party_b,
        });

        let swap = SwapEscrow<T1, T2> {
            id: swap_id,
            party_a: tx_context::sender(ctx),
            party_b,
            balance_a: balance::zero(),
            balance_b: balance::zero(),
            deposited_a: false,
            deposited_b: false,
            amount_a,
            amount_b,
            expiration,
        };

        transfer::share_object(swap);
    }

    /// Party A deposits their funds into swap
    public entry fun swap_deposit_a<T1, T2>(
        swap: &mut SwapEscrow<T1, T2>,
        coin: Coin<T1>,
        ctx: &TxContext
    ) {
        assert!(tx_context::sender(ctx) == swap.party_a, ENotSwapParticipant);
        assert!(!swap.deposited_a, EAlreadyAccepted);
        assert!(coin::value(&coin) == swap.amount_a, EInvalidAmount);

        balance::join(&mut swap.balance_a, coin::into_balance(coin));
        swap.deposited_a = true;
    }

    /// Party B deposits their funds into swap
    public entry fun swap_deposit_b<T1, T2>(
        swap: &mut SwapEscrow<T1, T2>,
        coin: Coin<T2>,
        ctx: &TxContext
    ) {
        assert!(tx_context::sender(ctx) == swap.party_b, ENotSwapParticipant);
        assert!(!swap.deposited_b, EAlreadyAccepted);
        assert!(coin::value(&coin) == swap.amount_b, EInvalidAmount);

        balance::join(&mut swap.balance_b, coin::into_balance(coin));
        swap.deposited_b = true;
    }

    /// Execute swap when both parties have deposited
    public entry fun execute_swap<T1, T2>(
        swap: &mut SwapEscrow<T1, T2>,
        clock: &Clock,
        ctx: &mut TxContext
    ) {
        assert!(swap.deposited_a && swap.deposited_b, ESwapNotReady);
        assert!(clock::timestamp_ms(clock) < swap.expiration, EEscrowLocked);

        // Transfer funds to opposite parties
        let coin_a = coin::from_balance(balance::withdraw_all(&mut swap.balance_a), ctx);
        let coin_b = coin::from_balance(balance::withdraw_all(&mut swap.balance_b), ctx);

        transfer::public_transfer(coin_b, swap.party_a);
        transfer::public_transfer(coin_a, swap.party_b);

        event::emit(SwapCompleted {
            swap_id: object::uid_to_inner(&swap.id),
        });
    }

    /// Cancel swap and refund if expired or only one party deposited
    public entry fun cancel_swap<T1, T2>(
        swap: &mut SwapEscrow<T1, T2>,
        clock: &Clock,
        ctx: &mut TxContext
    ) {
        let sender = tx_context::sender(ctx);
        assert!(
            sender == swap.party_a || sender == swap.party_b,
            ENotSwapParticipant
        );

        // Can cancel if expired OR if swap not fully funded
        let can_cancel = clock::timestamp_ms(clock) >= swap.expiration ||
                         !(swap.deposited_a && swap.deposited_b);
        assert!(can_cancel, ESwapNotReady);

        // Refund party A if they deposited
        if (swap.deposited_a) {
            let coin_a = coin::from_balance(balance::withdraw_all(&mut swap.balance_a), ctx);
            transfer::public_transfer(coin_a, swap.party_a);
            swap.deposited_a = false;
        };

        // Refund party B if they deposited
        if (swap.deposited_b) {
            let coin_b = coin::from_balance(balance::withdraw_all(&mut swap.balance_b), ctx);
            transfer::public_transfer(coin_b, swap.party_b);
            swap.deposited_b = false;
        };
    }

    // ==================== Getter Functions ====================

    public fun sender<T>(escrow: &EscrowObject<T>): address {
        escrow.sender
    }

    public fun recipient<T>(escrow: &EscrowObject<T>): address {
        escrow.recipient
    }

    public fun amount<T>(escrow: &EscrowObject<T>): u64 {
        balance::value(&escrow.balance)
    }

    public fun is_accepted<T>(escrow: &EscrowObject<T>): bool {
        escrow.accepted
    }

    public fun is_disputed<T>(escrow: &EscrowObject<T>): bool {
        escrow.in_dispute
    }

    public fun unlock_time<T>(escrow: &EscrowObject<T>): Option<u64> {
        escrow.unlock_time
    }

    // ==================== Test-Only Functions ====================

    #[test_only]
    public fun create_for_testing<T>(
        coin: Coin<T>,
        recipient: address,
        ctx: &mut TxContext
    ): EscrowObject<T> {
        create(coin, recipient, option::none<address>(), option::none<u64>(), b"test", ctx)
    }

    #[test_only]
    public fun destroy_for_testing<T>(escrow: EscrowObject<T>) {
        let EscrowObject {
            id,
            sender: _,
            recipient: _,
            arbiter: _,
            balance,
            accepted: _,
            in_dispute: _,
            unlock_time: _,
            description: _,
        } = escrow;
        object::delete(id);
        balance::destroy_for_testing(balance);
    }
}
