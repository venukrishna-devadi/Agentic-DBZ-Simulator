# test_quick.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from graph.builder import create_saga_graph
from schemas.state import GameState
from langchain_core.messages import HumanMessage

def test_graph():
    print("🧪 Testing Graph...")
    
    graph = create_saga_graph()
    
    state = GameState(
        player_name="TestGoku",
        saga_name="Saiyan Saga",
        player_stats={"power_level": 1000}
    )
    
    state.add_message(HumanMessage(content="Start the saga"))
    
    result = graph.run(state, thread_id="test", timeout=10)
    
    if result.messages:
        print(f"✅ Got {len(result.messages)} messages")
        print(f"Last message: {result.messages[-1].content[:100]}...")
    else:
        print("❌ No messages generated")
    
    return result

if __name__ == "__main__":
    test_graph()