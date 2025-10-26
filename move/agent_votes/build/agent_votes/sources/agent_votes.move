module agent_votes::agent_votes {
    use sui::object::{Self, UID};
    use sui::transfer;
    use sui::tx_context::{TxContext};

    /// Shared object that stores vote counts for all agents
    public struct VoteRegistry has key {
        id: UID,
        speedrunner_votes: u64,
        bloom_votes: u64,
        solver_votes: u64,
        loader_votes: u64,
    }

    /// Initialize the voting registry (called once when deploying)
    fun init(ctx: &mut TxContext) {
        let registry = VoteRegistry {
            id: object::new(ctx),
            speedrunner_votes: 0,
            bloom_votes: 0,
            solver_votes: 0,
            loader_votes: 0,
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
}
