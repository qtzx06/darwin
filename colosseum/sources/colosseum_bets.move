module colosseum::colosseum_bets {
    use sui::balance::{Self, Balance};
    use sui::coin::{Self, Coin};
    use sui::event;
    use sui::random::{Self, Random};
    use sui::sui::SUI;
    use sui::transfer;
    use sui::tx_context::{Self, TxContext};

    /// Shared betting "house" that holds the SUI pot.
    public struct House has key {
        id: UID,
        pot: Balance<SUI>,
        admin: address,
    }

    /// Emitted when a bet is placed.
    public struct BetPlaced has copy, drop {
        player: address,
        amount: u64,
        choice: u8,
    }

    /// Emitted when a bet is settled.
    public struct BetSettled has copy, drop {
        player: address,
        amount: u64,
        choice: u8,
        outcome: u8,
        payout: u64,
    }

    /// One-time initializer. Publishes (shares) the House with empty pot.
    fun init(ctx: &mut TxContext) {
        let h = House {
            id: object::new(ctx),
            pot: balance::zero<SUI>(),
            admin: tx_context::sender(ctx),
        };
        transfer::share_object(h)
    }

    /// Deposit SUI directly to the house pot (e.g., seed liquidity).
    public entry fun deposit(house: &mut House, mut coin_in: Coin<SUI>, _ctx: &mut TxContext) {
        let b = coin::into_balance(coin_in);
        balance::join(&mut house.pot, b);
    }

    /// Place a bet with `amount` SUI taken from `coin_in`.
    /// Returns change to the caller as a Coin<SUI>.
    /// `choice`: your game choice (e.g., 0/1 for coin flip).
    public entry fun place_bet(
        house: &mut House,
        mut coin_in: Coin<SUI>,
        amount: u64,
        choice: u8,
        ctx: &mut TxContext
    ) {
        // split the exact bet amount from the user's coin
        let bet_coin = coin::split(&mut coin_in, amount, ctx);
        let bet_bal = coin::into_balance(bet_coin);
        // move bet into the house pot
        balance::join(&mut house.pot, bet_bal);

        event::emit(BetPlaced {
            player: tx_context::sender(ctx),
            amount,
            choice,
        });

        // transfer remaining balance back to sender
        transfer::public_transfer(coin_in, tx_context::sender(ctx));
    }

    /// Settle a bet for `player`. Uses on-chain randomness and pays out from the pot.
    /// For demo: 50/50; if win → payout = amount * 2, else payout = 0.
    /// You can call this immediately after `place_bet` in the same PTB,
    /// or later (e.g., by an operator) as a separate transaction.
    public entry fun settle_bet(
        house: &mut House,
        r: &Random,
        player: address,
        amount: u64,
        choice: u8,
        ctx: &mut TxContext
    ) {
        // Draw outcome in [0, 2) → {0,1}
        let mut gen = random::new_generator(r, ctx);
        let outcome = random::generate_u8_in_range(&mut gen, 0, 2);

        let mut payout_amt = 0;
        if (outcome == choice) {
            // simple 2x payout
            payout_amt = amount * 2;
            // withdraw from the pot
            let pay_bal = balance::split(&mut house.pot, payout_amt);
            let pay_coin = coin::from_balance(pay_bal, ctx);
            transfer::public_transfer(pay_coin, player);
        };

        event::emit(BetSettled {
            player,
            amount,
            choice,
            outcome,
            payout: payout_amt,
        });
    }

    /// Admin withdraws funds.
    public entry fun admin_withdraw(
        house: &mut House,
        to: address,
        amount: u64,
        ctx: &mut TxContext
    ) {
        assert!(tx_context::sender(ctx) == house.admin, 1);
        let bal = balance::split(&mut house.pot, amount);
        let c = coin::from_balance(bal, ctx);
        transfer::public_transfer(c, to);
    }
}
