module agent_votes::agent_votes {
    use sui::object::{Self, UID};
    use sui::transfer;
    use sui::tx_context::{Self, TxContext};
    use sui::coin::{Self, Coin};
    use sui::sui::SUI;

    /// Shared object that stores vote counts and wallet addresses for all agents
    public struct VoteRegistry has key {
        id: UID,
        speedrunner_votes: u64,
        bloom_votes: u64,
        solver_votes: u64,
        loader_votes: u64,
        speedrunner_wallet: address,
        bloom_wallet: address,
        solver_wallet: address,
        loader_wallet: address,
        admin: address,
    }

    /// Initialize the voting registry (called once when deploying)
    fun init(ctx: &mut TxContext) {
        let registry = VoteRegistry {
            id: object::new(ctx),
            speedrunner_votes: 0,
            bloom_votes: 0,
            solver_votes: 0,
            loader_votes: 0,
            speedrunner_wallet: @0x0,
            bloom_wallet: @0x0,
            solver_wallet: @0x0,
            loader_wallet: @0x0,
            admin: tx_context::sender(ctx),
        };
        transfer::share_object(registry);
    }

    /// Vote for an agent
    /// agent_id: 0=speedrunner, 1=bloom, 2=solver, 3=loader
    public entry fun vote(
        registry: &mut VoteRegistry,
        agent_id: u8,
        _ctx: &mut TxContext
    ) {
        if (agent_id == 0) {
            registry.speedrunner_votes = registry.speedrunner_votes + 1;
        } else if (agent_id == 1) {
            registry.bloom_votes = registry.bloom_votes + 1;
        } else if (agent_id == 2) {
            registry.solver_votes = registry.solver_votes + 1;
        } else if (agent_id == 3) {
            registry.loader_votes = registry.loader_votes + 1;
        };
    }

    /// Get vote count for speedrunner
    public fun get_speedrunner_votes(registry: &VoteRegistry): u64 {
        registry.speedrunner_votes
    }

    /// Get vote count for bloom
    public fun get_bloom_votes(registry: &VoteRegistry): u64 {
        registry.bloom_votes
    }

    /// Get vote count for solver
    public fun get_solver_votes(registry: &VoteRegistry): u64 {
        registry.solver_votes
    }

    /// Get vote count for loader
    public fun get_loader_votes(registry: &VoteRegistry): u64 {
        registry.loader_votes
    }

    /// Vote for an agent with a SUI tip
    /// agent_id: 0=speedrunner, 1=bloom, 2=solver, 3=loader
    /// payment: Coin<SUI> to tip the agent
    public entry fun vote_with_tip(
        registry: &mut VoteRegistry,
        agent_id: u8,
        payment: Coin<SUI>,
        ctx: &mut TxContext
    ) {
        // Increment vote count
        if (agent_id == 0) {
            registry.speedrunner_votes = registry.speedrunner_votes + 1;
            transfer::public_transfer(payment, registry.speedrunner_wallet);
        } else if (agent_id == 1) {
            registry.bloom_votes = registry.bloom_votes + 1;
            transfer::public_transfer(payment, registry.bloom_wallet);
        } else if (agent_id == 2) {
            registry.solver_votes = registry.solver_votes + 1;
            transfer::public_transfer(payment, registry.solver_wallet);
        } else if (agent_id == 3) {
            registry.loader_votes = registry.loader_votes + 1;
            transfer::public_transfer(payment, registry.loader_wallet);
        } else {
            // Invalid agent_id, return the payment
            transfer::public_transfer(payment, tx_context::sender(ctx));
        };
    }

    /// Admin function to update agent wallet addresses
    public entry fun update_agent_wallets(
        registry: &mut VoteRegistry,
        speedrunner: address,
        bloom: address,
        solver: address,
        loader: address,
        ctx: &mut TxContext
    ) {
        assert!(tx_context::sender(ctx) == registry.admin, 0);
        registry.speedrunner_wallet = speedrunner;
        registry.bloom_wallet = bloom;
        registry.solver_wallet = solver;
        registry.loader_wallet = loader;
    }

    /// Get agent wallet addresses
    public fun get_agent_wallets(registry: &VoteRegistry): (address, address, address, address) {
        (
            registry.speedrunner_wallet,
            registry.bloom_wallet,
            registry.solver_wallet,
            registry.loader_wallet
        )
    }
}
