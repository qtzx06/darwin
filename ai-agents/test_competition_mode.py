"""
Example of how to use the chat simulator with competition mode and progress updates.
"""
import asyncio
from chat_simulator import ChatSimulator


async def demo_competition():
    """Demo showing competition mode and progress updates."""
    
    # Create simulator
    simulator = ChatSimulator()
    
    # Start the simulator (no welcome message anymore)
    simulator_task = asyncio.create_task(simulator.start())
    
    # Wait a bit for agents to start chatting
    await asyncio.sleep(10)
    
    # Start the competition!
    print("\n[STARTING COMPETITION]\n")
    await simulator.start_competition()
    
    # Wait for competition to heat up
    await asyncio.sleep(5)
    
    # Feed some progress updates (these don't require responses, just context)
    await simulator.add_agent_progress("Speedrunner", "Completed initial setup in 30 seconds")
    await asyncio.sleep(3)
    
    await simulator.add_agent_progress("Bloom", "Designed beautiful UI mockups with color palette")
    await asyncio.sleep(3)
    
    await simulator.add_agent_progress("Solver", "Implemented O(log n) search algorithm")
    await asyncio.sleep(3)
    
    await simulator.add_agent_progress("Loader", "Set up CI/CD pipeline with automated tests")
    await asyncio.sleep(3)
    
    await simulator.add_agent_progress("Speedrunner", "Finished entire feature while others still planning")
    await asyncio.sleep(10)
    
    # Competition continues...
    # Let it run until user presses Ctrl+C
    await simulator_task


if __name__ == "__main__":
    try:
        asyncio.run(demo_competition())
    except KeyboardInterrupt:
        pass
