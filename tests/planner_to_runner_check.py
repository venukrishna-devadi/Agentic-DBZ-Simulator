# planner_to_runner_check.py - FIXED VERSION

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from langgraph.graph import StateGraph, END, START
from schemas.state import GameState
from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from langchain_core.messages import HumanMessage, AIMessage

# IMPORT your SagaGraph builder
from graph.builder import create_saga_graph

def test_minimal_flow():
    print("🧪 Testing MINIMAL Planner → Executor flow...")
    
    # OPTION 1: Use your full SagaGraph (recommended)
    print("\n📋 Testing with full SagaGraph...")
    graph = create_saga_graph()
    
    # Create test state
    state = GameState(
        player_name="TestGoku",
        saga_name="Saiyan Saga",
        player_stats={
            "power_level": 1000,
            "health": 100,
            "max_health": 100,
            "ki_mastery": 30,
            "level": 1,
            "experience": 0,
            "items": ["Senzu Bean"]
        }
    )
    state.add_message(HumanMessage(content="Start the saga"))
    
    print(f"\n📊 Initial state - Power: {state.player_stats['power_level']}")
    
    # Use the SagaGraph's run method (which has coercion built-in)
    try:
        result = graph.run(state, thread_id="test", timeout=30)
        
        print("\n✅ Minimal graph succeeded!")
        print(f"📊 Final state - Power: {result.player_stats['power_level']}")
        print(f"📝 Messages: {len(result.messages)}")
        
        ai_msgs = [m for m in result.messages if isinstance(m, AIMessage)]
        if ai_msgs:
            print(f"\n📝 Last AI message:")
            print(ai_msgs[-1].content[:200] + "...")
        return True
    except Exception as e:
        print(f"\n❌ Minimal graph failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_minimal_manual():
    """Alternative: Build minimal graph manually but with coercion"""
    print("\n📋 Testing manually built graph with coercion...")
    
    # Create a minimal graph
    workflow = StateGraph(GameState)
    
    # Initialize agents
    planner = PlannerAgent()
    executor = ExecutorAgent()
    
    def planner_wrapper(state: GameState) -> GameState:
        updates = planner.invoke(state)
        for key, value in updates.items():
            if key == "messages":
                if isinstance(value, list):
                    for msg in value:
                        state.add_message(msg)
                else:
                    state.add_message(value)
            elif hasattr(state, key):
                setattr(state, key, value)
        state.plan_step_index = 0
        return state
    
    def executor_wrapper(state: GameState) -> GameState:
        # Get player action
        player_action = None
        for msg in reversed(state.messages):
            if hasattr(msg, 'type') and msg.type == "human":
                player_action = msg.content
                break
        
        updates = executor.invoke(state, player_action)
        
        for key, value in updates.items():
            if key == "messages":
                if isinstance(value, list):
                    for msg in value:
                        state.add_message(msg)
                else:
                    state.add_message(value)
            elif hasattr(state, key):
                setattr(state, key, value)
        
        if state.current_step and state.current_step.completed:
            state.plan_step_index += 1
        
        state.total_actions += 1
        return state
    
    workflow.add_node("planner", planner_wrapper)
    workflow.add_node("executor", executor_wrapper)
    workflow.add_edge(START, "planner")
    workflow.add_edge("planner", "executor")
    workflow.add_edge("executor", END)
    
    graph = workflow.compile()
    
    # Create test state
    state = GameState(
        player_name="TestGoku",
        saga_name="Saiyan Saga",
        player_stats={"power_level": 1000, "ki_mastery": 30}
    )
    state.add_message(HumanMessage(content="Start the saga"))
    
    try:
        # Manual coercion after invoke
        raw_result = graph.invoke(state)
        
        # Convert dict to GameState if needed
        if isinstance(raw_result, dict):
            # Use Pydantic v2 validation if available
            if hasattr(GameState, "model_validate"):
                result = GameState.model_validate(raw_result)
            else:
                result = GameState(**raw_result)
        else:
            result = raw_result
        
        print("\n✅ Manual graph succeeded!")
        print(f"📊 Final state - Power: {result.player_stats['power_level']}")
        print(f"📝 Messages: {len(result.messages)}")
        return True
    except Exception as e:
        print(f"\n❌ Manual graph failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("GRAPH TESTER")
    print("=" * 60)
    
    # Test with full SagaGraph
    test_minimal_flow()
    
    print("\n" + "=" * 60)
    
    # Test with manual graph + coercion
    test_minimal_manual()