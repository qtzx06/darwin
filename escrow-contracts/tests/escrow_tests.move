#[test_only]
module escrow::escrow_tests {
    use sui::test_scenario::{Self as ts, Scenario};
    use sui::coin::{Self, Coin};
    use sui::sui::SUI;
    use sui::test_utils;
    use sui::clock::{Self, Clock};
    use escrow::escrow::{Self, EscrowObject, SwapEscrow};
    use std::option;

    // Test addresses
    const SENDER: address = @0xA;
    const RECIPIENT: address = @0xB;
    const ARBITER: address = @0xC;
    const OTHER: address = @0xD;

    // Test constants
    const ESCROW_AMOUNT: u64 = 1000;
    const UNLOCK_TIME: u64 = 1000000;

    // ==================== Helper Functions ====================

    fun create_test_coin(amount: u64, scenario: &mut Scenario): Coin<SUI> {
        coin::mint_for_testing<SUI>(amount, ts::ctx(scenario))
    }

    fun create_clock(timestamp: u64, scenario: &mut Scenario): Clock {
        let mut clock = clock::create_for_testing(ts::ctx(scenario));
        clock::increment_for_testing(&mut clock, timestamp);
        clock
    }

    // ==================== Basic Escrow Tests ====================

    #[test]
    fun test_create_escrow() {
        let mut scenario = ts::begin(SENDER);

        // Create and share escrow
        {
            let coin = create_test_coin(ESCROW_AMOUNT, &mut scenario);
            escrow::create_shared(
                coin,
                RECIPIENT,
                option::none<address>(),
                option::none<u64>(),
                b"test escrow",
                ts::ctx(&mut scenario)
            );
        };

        // Verify escrow exists and has correct properties
        ts::next_tx(&mut scenario, SENDER);
        {
            let escrow = ts::take_shared<EscrowObject<SUI>>(&scenario);

            assert!(escrow::sender(&escrow) == SENDER, 0);
            assert!(escrow::recipient(&escrow) == RECIPIENT, 1);
            assert!(escrow::amount(&escrow) == ESCROW_AMOUNT, 2);
            assert!(!escrow::is_accepted(&escrow), 3);
            assert!(!escrow::is_disputed(&escrow), 4);

            ts::return_shared(escrow);
        };

        ts::end(scenario);
    }

    #[test]
    fun test_accept_escrow() {
        let mut scenario = ts::begin(SENDER);

        // Create escrow
        {
            let coin = create_test_coin(ESCROW_AMOUNT, &mut scenario);
            escrow::create_shared(
                coin,
                RECIPIENT,
                option::none<address>(),
                option::none<u64>(),
                b"test",
                ts::ctx(&mut scenario)
            );
        };

        // Recipient accepts
        ts::next_tx(&mut scenario, RECIPIENT);
        {
            let mut escrow = ts::take_shared<EscrowObject<SUI>>(&scenario);
            let clock = create_clock(0, &mut scenario);

            let accepted_coin = escrow::accept(&mut escrow, &clock, ts::ctx(&mut scenario));

            assert!(coin::value(&accepted_coin) == ESCROW_AMOUNT, 0);
            assert!(escrow::is_accepted(&escrow), 1);
            assert!(escrow::amount(&escrow) == 0, 2);

            coin::burn_for_testing(accepted_coin);
            clock::destroy_for_testing(clock);
            ts::return_shared(escrow);
        };

        ts::end(scenario);
    }

    #[test]
    fun test_cancel_escrow() {
        let mut scenario = ts::begin(SENDER);

        // Create escrow
        {
            let coin = create_test_coin(ESCROW_AMOUNT, &mut scenario);
            escrow::create_shared(
                coin,
                RECIPIENT,
                option::none<address>(),
                option::none<u64>(),
                b"test",
                ts::ctx(&mut scenario)
            );
        };

        // Sender cancels
        ts::next_tx(&mut scenario, SENDER);
        {
            let mut escrow = ts::take_shared<EscrowObject<SUI>>(&scenario);

            let refunded_coin = escrow::cancel(&mut escrow, ts::ctx(&mut scenario));

            assert!(coin::value(&refunded_coin) == ESCROW_AMOUNT, 0);
            assert!(escrow::amount(&escrow) == 0, 1);

            coin::burn_for_testing(refunded_coin);
            ts::return_shared(escrow);
        };

        ts::end(scenario);
    }

    #[test]
    #[expected_failure(abort_code = 1)]
    fun test_accept_wrong_recipient() {
        let mut scenario = ts::begin(SENDER);

        // Create escrow
        {
            let coin = create_test_coin(ESCROW_AMOUNT, &mut scenario);
            escrow::create_shared(
                coin,
                RECIPIENT,
                option::none<address>(),
                option::none<u64>(),
                b"test",
                ts::ctx(&mut scenario)
            );
        };

        // Wrong person tries to accept
        ts::next_tx(&mut scenario, OTHER);
        {
            let mut escrow = ts::take_shared<EscrowObject<SUI>>(&scenario);
            let clock = create_clock(0, &mut scenario);

            let _coin = escrow::accept(&mut escrow, &clock, ts::ctx(&mut scenario));

            abort 999 // Should never reach here
        };
    }

    #[test]
    #[expected_failure(abort_code = 0)]
    fun test_cancel_wrong_sender() {
        let mut scenario = ts::begin(SENDER);

        // Create escrow
        {
            let coin = create_test_coin(ESCROW_AMOUNT, &mut scenario);
            escrow::create_shared(
                coin,
                RECIPIENT,
                option::none<address>(),
                option::none<u64>(),
                b"test",
                ts::ctx(&mut scenario)
            );
        };

        // Wrong person tries to cancel
        ts::next_tx(&mut scenario, OTHER);
        {
            let mut escrow = ts::take_shared<EscrowObject<SUI>>(&scenario);

            let _coin = escrow::cancel(&mut escrow, ts::ctx(&mut scenario));

            abort 999 // Should never reach here
        };
    }

    #[test]
    #[expected_failure(abort_code = 3)]
    fun test_cancel_after_accept() {
        let mut scenario = ts::begin(SENDER);

        // Create escrow
        {
            let coin = create_test_coin(ESCROW_AMOUNT, &mut scenario);
            escrow::create_shared(
                coin,
                RECIPIENT,
                option::none<address>(),
                option::none<u64>(),
                b"test",
                ts::ctx(&mut scenario)
            );
        };

        // Recipient accepts
        ts::next_tx(&mut scenario, RECIPIENT);
        {
            let mut escrow = ts::take_shared<EscrowObject<SUI>>(&scenario);
            let clock = create_clock(0, &mut scenario);

            let accepted_coin = escrow::accept(&mut escrow, &clock, ts::ctx(&mut scenario));
            coin::burn_for_testing(accepted_coin);
            clock::destroy_for_testing(clock);

            ts::return_shared(escrow);
        };

        // Sender tries to cancel after acceptance
        ts::next_tx(&mut scenario, SENDER);
        {
            let mut escrow = ts::take_shared<EscrowObject<SUI>>(&scenario);

            let _coin = escrow::cancel(&mut escrow, ts::ctx(&mut scenario));

            abort 999 // Should never reach here
        };
    }

    // ==================== Time-Lock Tests ====================

    #[test]
    fun test_timelock_escrow_unlocked() {
        let mut scenario = ts::begin(SENDER);

        // Create time-locked escrow
        {
            let coin = create_test_coin(ESCROW_AMOUNT, &mut scenario);
            escrow::create_shared(
                coin,
                RECIPIENT,
                option::none<address>(),
                option::some(UNLOCK_TIME),
                b"time-locked",
                ts::ctx(&mut scenario)
            );
        };

        // Try to accept after unlock time
        ts::next_tx(&mut scenario, RECIPIENT);
        {
            let mut escrow = ts::take_shared<EscrowObject<SUI>>(&scenario);
            let clock = create_clock(UNLOCK_TIME, &mut scenario);

            let accepted_coin = escrow::accept(&mut escrow, &clock, ts::ctx(&mut scenario));

            assert!(coin::value(&accepted_coin) == ESCROW_AMOUNT, 0);

            coin::burn_for_testing(accepted_coin);
            clock::destroy_for_testing(clock);
            ts::return_shared(escrow);
        };

        ts::end(scenario);
    }

    #[test]
    #[expected_failure(abort_code = 7)]
    fun test_timelock_escrow_locked() {
        let mut scenario = ts::begin(SENDER);

        // Create time-locked escrow
        {
            let coin = create_test_coin(ESCROW_AMOUNT, &mut scenario);
            escrow::create_shared(
                coin,
                RECIPIENT,
                option::none<address>(),
                option::some(UNLOCK_TIME),
                b"time-locked",
                ts::ctx(&mut scenario)
            );
        };

        // Try to accept before unlock time
        ts::next_tx(&mut scenario, RECIPIENT);
        {
            let mut escrow = ts::take_shared<EscrowObject<SUI>>(&scenario);
            let clock = create_clock(UNLOCK_TIME - 1, &mut scenario);

            let _coin = escrow::accept(&mut escrow, &clock, ts::ctx(&mut scenario));

            abort 999 // Should never reach here
        };
    }

    // ==================== Dispute Resolution Tests ====================

    #[test]
    fun test_raise_and_resolve_dispute_for_sender() {
        let mut scenario = ts::begin(SENDER);

        // Create escrow with arbiter
        {
            let coin = create_test_coin(ESCROW_AMOUNT, &mut scenario);
            escrow::create_shared(
                coin,
                RECIPIENT,
                option::some(ARBITER),
                option::none<u64>(),
                b"with arbiter",
                ts::ctx(&mut scenario)
            );
        };

        // Sender raises dispute
        ts::next_tx(&mut scenario, SENDER);
        {
            let mut escrow = ts::take_shared<EscrowObject<SUI>>(&scenario);

            escrow::raise_dispute(&mut escrow, ts::ctx(&mut scenario));
            assert!(escrow::is_disputed(&escrow), 0);

            ts::return_shared(escrow);
        };

        // Arbiter resolves in favor of sender
        ts::next_tx(&mut scenario, ARBITER);
        {
            let mut escrow = ts::take_shared<EscrowObject<SUI>>(&scenario);

            let resolved_coin = escrow::resolve_dispute(
                &mut escrow,
                true, // award to sender
                ts::ctx(&mut scenario)
            );

            assert!(coin::value(&resolved_coin) == ESCROW_AMOUNT, 0);
            assert!(!escrow::is_disputed(&escrow), 1);

            coin::burn_for_testing(resolved_coin);
            ts::return_shared(escrow);
        };

        ts::end(scenario);
    }

    #[test]
    fun test_raise_and_resolve_dispute_for_recipient() {
        let mut scenario = ts::begin(SENDER);

        // Create escrow with arbiter
        {
            let coin = create_test_coin(ESCROW_AMOUNT, &mut scenario);
            escrow::create_shared(
                coin,
                RECIPIENT,
                option::some(ARBITER),
                option::none<u64>(),
                b"with arbiter",
                ts::ctx(&mut scenario)
            );
        };

        // Recipient raises dispute
        ts::next_tx(&mut scenario, RECIPIENT);
        {
            let mut escrow = ts::take_shared<EscrowObject<SUI>>(&scenario);

            escrow::raise_dispute(&mut escrow, ts::ctx(&mut scenario));
            assert!(escrow::is_disputed(&escrow), 0);

            ts::return_shared(escrow);
        };

        // Arbiter resolves in favor of recipient
        ts::next_tx(&mut scenario, ARBITER);
        {
            let mut escrow = ts::take_shared<EscrowObject<SUI>>(&scenario);

            let resolved_coin = escrow::resolve_dispute(
                &mut escrow,
                false, // award to recipient
                ts::ctx(&mut scenario)
            );

            assert!(coin::value(&resolved_coin) == ESCROW_AMOUNT, 0);

            coin::burn_for_testing(resolved_coin);
            ts::return_shared(escrow);
        };

        ts::end(scenario);
    }

    #[test]
    #[expected_failure(abort_code = 5)]
    fun test_cannot_accept_during_dispute() {
        let mut scenario = ts::begin(SENDER);

        // Create escrow with arbiter
        {
            let coin = create_test_coin(ESCROW_AMOUNT, &mut scenario);
            escrow::create_shared(
                coin,
                RECIPIENT,
                option::some(ARBITER),
                option::none<u64>(),
                b"with arbiter",
                ts::ctx(&mut scenario)
            );
        };

        // Raise dispute
        ts::next_tx(&mut scenario, SENDER);
        {
            let mut escrow = ts::take_shared<EscrowObject<SUI>>(&scenario);
            escrow::raise_dispute(&mut escrow, ts::ctx(&mut scenario));
            ts::return_shared(escrow);
        };

        // Try to accept during dispute
        ts::next_tx(&mut scenario, RECIPIENT);
        {
            let mut escrow = ts::take_shared<EscrowObject<SUI>>(&scenario);
            let clock = create_clock(0, &mut scenario);

            let _coin = escrow::accept(&mut escrow, &clock, ts::ctx(&mut scenario));

            abort 999 // Should never reach here
        };
    }

    // ==================== Swap Escrow Tests ====================

    #[test]
    fun test_successful_swap() {
        let mut scenario = ts::begin(SENDER);
        let amount_a = 500;
        let amount_b = 1000;

        // SENDER creates swap
        {
            escrow::create_swap<SUI, SUI>(
                RECIPIENT,
                amount_a,
                amount_b,
                UNLOCK_TIME,
                ts::ctx(&mut scenario)
            );
        };

        // SENDER deposits
        ts::next_tx(&mut scenario, SENDER);
        {
            let mut swap = ts::take_shared<SwapEscrow<SUI, SUI>>(&scenario);
            let coin = create_test_coin(amount_a, &mut scenario);

            escrow::swap_deposit_a(&mut swap, coin, ts::ctx(&mut scenario));

            ts::return_shared(swap);
        };

        // RECIPIENT deposits
        ts::next_tx(&mut scenario, RECIPIENT);
        {
            let mut swap = ts::take_shared<SwapEscrow<SUI, SUI>>(&scenario);
            let coin = create_test_coin(amount_b, &mut scenario);

            escrow::swap_deposit_b(&mut swap, coin, ts::ctx(&mut scenario));

            ts::return_shared(swap);
        };

        // Execute swap
        ts::next_tx(&mut scenario, SENDER);
        {
            let mut swap = ts::take_shared<SwapEscrow<SUI, SUI>>(&scenario);
            let clock = create_clock(0, &mut scenario);

            escrow::execute_swap(&mut swap, &clock, ts::ctx(&mut scenario));

            clock::destroy_for_testing(clock);
            ts::return_shared(swap);
        };

        // Verify SENDER received amount_b
        ts::next_tx(&mut scenario, SENDER);
        {
            let received = ts::take_from_sender<Coin<SUI>>(&scenario);
            assert!(coin::value(&received) == amount_b, 0);
            ts::return_to_sender(&scenario, received);
        };

        // Verify RECIPIENT received amount_a
        ts::next_tx(&mut scenario, RECIPIENT);
        {
            let received = ts::take_from_sender<Coin<SUI>>(&scenario);
            assert!(coin::value(&received) == amount_a, 0);
            ts::return_to_sender(&scenario, received);
        };

        ts::end(scenario);
    }

    #[test]
    fun test_cancel_swap_partial_deposit() {
        let mut scenario = ts::begin(SENDER);
        let amount_a = 500;
        let amount_b = 1000;

        // Create swap
        {
            escrow::create_swap<SUI, SUI>(
                RECIPIENT,
                amount_a,
                amount_b,
                UNLOCK_TIME,
                ts::ctx(&mut scenario)
            );
        };

        // Only SENDER deposits
        ts::next_tx(&mut scenario, SENDER);
        {
            let mut swap = ts::take_shared<SwapEscrow<SUI, SUI>>(&scenario);
            let coin = create_test_coin(amount_a, &mut scenario);

            escrow::swap_deposit_a(&mut swap, coin, ts::ctx(&mut scenario));

            ts::return_shared(swap);
        };

        // Cancel swap (only one party deposited)
        ts::next_tx(&mut scenario, SENDER);
        {
            let mut swap = ts::take_shared<SwapEscrow<SUI, SUI>>(&scenario);
            let clock = create_clock(0, &mut scenario);

            escrow::cancel_swap(&mut swap, &clock, ts::ctx(&mut scenario));

            clock::destroy_for_testing(clock);
            ts::return_shared(swap);
        };

        // Verify SENDER got refund
        ts::next_tx(&mut scenario, SENDER);
        {
            let refund = ts::take_from_sender<Coin<SUI>>(&scenario);
            assert!(coin::value(&refund) == amount_a, 0);
            ts::return_to_sender(&scenario, refund);
        };

        ts::end(scenario);
    }

    #[test]
    #[expected_failure(abort_code = 9)]
    fun test_execute_swap_not_ready() {
        let mut scenario = ts::begin(SENDER);

        // Create swap
        {
            escrow::create_swap<SUI, SUI>(
                RECIPIENT,
                500,
                1000,
                UNLOCK_TIME,
                ts::ctx(&mut scenario)
            );
        };

        // Try to execute without deposits
        ts::next_tx(&mut scenario, SENDER);
        {
            let mut swap = ts::take_shared<SwapEscrow<SUI, SUI>>(&scenario);
            let clock = create_clock(0, &mut scenario);

            escrow::execute_swap(&mut swap, &clock, ts::ctx(&mut scenario));

            abort 999 // Should never reach here
        };
    }
}
