# test_executor.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from schemas.state import GameState, PlanStep, SceneType
from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from langchain_core.messages import HumanMessage
import time

def test_executor_directly():
    """Test the executor in isolation"""
    print("🧪 Testing Executor Directly...")
    
    # Create a simple plan
    plan_step = PlanStep(
        scene_type=SceneType.INTRODUCTION,
        description="The adventure begins in a small village",
        expected_outcome="Meet the mentor and learn about the quest",
        expected_duration=1,
        emotional_intensity=0.7
    )
    
    # Create game state with this plan
    state = GameState(
        player_name="TestGoku",
        saga_name="Test Saga",
        player_stats={"power_level": 1000, "ki_mastery": 30},
        current_plan=[plan_step],
        plan_step_index=0
    )
    
    state.add_message(HumanMessage(content="Start the adventure"))
    
    # Initialize executor
    executor = ExecutorAgent()
    
    print("\n🎬 Invoking executor...")
    start_time = time.time()
    
    try:
        result = executor.invoke(state)
        elapsed = time.time() - start_time
        
        print(f"\n✅ Executor completed in {elapsed:.2f} seconds")
        print(f"Result keys: {list(result.keys())}")
        
        if "messages" in result:
            msg = result["messages"]
            print(f"\n📝 Generated scene:")
            print(f"{msg.content[:200]}...")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_planner_and_executor():
    """Test planner and executor together"""
    print("\n🧪 Testing Planner + Executor Together...")
    
    # Create initial state
    state = GameState(
        player_name="TestGoku",
        saga_name="Saiyan Saga",
        player_stats={"power_level": 1000}
    )
    
    state.add_message(HumanMessage(content="Start the saga"))
    
    # Run planner
    print("\n📋 Running Planner...")
    planner = PlannerAgent()
    plan_result = planner.invoke(state)
    
    # Update state with plan
    if "current_plan" in plan_result:
        state.current_plan = plan_result["current_plan"]
        state.plan_step_index = 0
        print(f"✅ Planner created {len(state.current_plan)} steps")
    
    # Run executor
    print("\n🎬 Running Executor on first step...")
    executor = ExecutorAgent()
    
    try:
        result = executor.invoke(state)
        
        if "messages" in result:
            print(f"\n✅ Success! Generated scene:")
            print(f"{result['messages'].content[:200]}...")
            
            # Verify state updates
            print(f"\n📊 State updates:")
            if "player_stats" in result:
                print(f"  Power: {result['player_stats'].get('power_level')}")
            if "scene_counter" in result:
                print(f"  Scene counter: {result['scene_counter']}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("EXECUTOR DEBUG TESTS")
    print("=" * 60)
    
    # Test 1: Direct executor test
    test_executor_directly()
    
    print("\n" + "=" * 60)
    
    # Test 2: Planner + Executor together
    test_planner_and_executor()