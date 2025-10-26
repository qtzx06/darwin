"""
View the persistent memory blocks of Darwin agents using REST API
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def view_agent_memory(agent_id, agent_name):
    """View memory blocks for a specific agent using REST API."""
    print(f"\n{'='*80}")
    print(f"🧠 {agent_name}")
    print(f"   ID: {agent_id}")
    print('='*80)
    
    try:
        # Use REST API directly
        token = os.getenv("LETTA_API_TOKEN")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Get agent details
        response = requests.get(
            f"https://api.letta.com/v1/agents/{agent_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            agent = response.json()
            
            # Get memory blocks
            memory = agent.get('memory', {})
            blocks = memory.get('blocks', [])
            
            if blocks:
                print(f"\n📦 Found {len(blocks)} Memory Block(s):\n")
                for i, block in enumerate(blocks, 1):
                    print(f"{'─'*80}")
                    print(f"Block {i}:")
                    print(f"  ID: {block.get('id', 'N/A')}")
                    print(f"  Label: {block.get('label', 'N/A')}")
                    print(f"\n  Content:")
                    print("  " + "─"*76)
                    value = block.get('value', '')
                    for line in value.split('\n'):
                        print(f"  {line}")
                    print("  " + "─"*76)
                    print()
            else:
                print("\n⚠️  No memory blocks found")
                print(f"\nFull agent response: {agent}")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("🔍 Darwin Agent Memory Viewer\n")
    
    # Get agent IDs from .env
    agents = [
        ("React Specialists", os.getenv("LETTA_AGENT_1")),
        ("Performance Team", os.getenv("LETTA_AGENT_2")),
        ("Clean Code Team", os.getenv("LETTA_AGENT_3")),
        ("Innovation Lab", os.getenv("LETTA_AGENT_4")),
    ]
    
    for name, agent_id in agents:
        if agent_id:
            view_agent_memory(agent_id, name)
        else:
            print(f"⚠️  {name}: No agent ID in .env")
    
    print("\n" + "="*80)
    print("✅ Memory viewer complete")
    print("="*80)

if __name__ == "__main__":
    main()
