#!/usr/bin/env python
"""
🔍 NODE-SPECIFIC DEBUGGER
Tests each node individually to find where the graph hangs
"""

import sys
import time
import threading
import queue
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from schemas.state import GameState, PlanStep, SceneType
from agents.verifier import VerifierAgent
from utils.memory import MemoryManager
from graph.builder import SagaGraph
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

class NodeDebugger:
    def __init__(self):
        self.results = {}
        
    def print_header(self, title):
        print(f"\n{'='*60}")
        print(f"🔍 {title}")
        print(f"{'='*60}")
    
    def run_with_timeout(self, func, timeout=10, *args, **kwargs):
        """Run a function with timeout"""
        result_queue = queue.Queue()
        
        def target():
            try:
                start = time.time()
                result = func(*args, **kwargs)
                elapsed = time.time() - start
                result_queue.put(("success", result, elapsed))
            except Exception as e:
                result_queue.put(("error", str(e), 0))
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout=timeout)
        
        if thread.is_alive():
            return {"status": "timeout", "error": f"Function timed out after {timeout}s"}
        
        try:
            status, data, elapsed = result_queue.get_nowait()
            if status == "success":
                return {"status": "success", "result": data, "elapsed": elapsed}
            else:
                return {"status": "error", "error": data}
        except queue.Empty:
            return {"status": "error", "error": "Unknown error"}
    
    # =========================================================
    # TEST VERIFIER NODE
    # =========================================================
    def test_verifier(self):
        self.print_header("TESTING VERIFIER NODE")
        
        # Create test state
        state = GameState(
            player_name="TestGoku",
            saga_name="Saiyan Saga",
            player_stats={"power_level": 1000, "ki_mastery": 30}
        )
        
        # Add a test scene to verify
        test_scene = AIMessage(content=(
            "Goku stood before King Kai, determination burning in his eyes. "
            "'I'm ready to train!' The gravity was intense, but his spirit was stronger. "
            "After hours of grueling exercise, Goku's power began to rise."
        ))
        state.add_message(test_scene)
        
        # Add a plan step
        state.current_plan = [
            PlanStep(
                scene_type=SceneType.TRAINING,
                description="Train with King Kai",
                expected_outcome="Increase power level",
                expected_duration=2,
                emotional_intensity=0.6
            )
        ]
        state.plan_step_index = 0
        
        # Test verifier with different strictness levels
        verifier = VerifierAgent(strictness="low")
        print("\n📋 Testing Verifier (low strictness)...")
        result = self.run_with_timeout(verifier.invoke, 10, state)
        self.print_result("Verifier (low)", result)
        
        verifier = VerifierAgent(strictness="medium")
        print("\n📋 Testing Verifier (medium strictness)...")
        result = self.run_with_timeout(verifier.invoke, 10, state)
        self.print_result("Verifier (medium)", result)
        
        verifier = VerifierAgent(strictness="high")
        print("\n📋 Testing Verifier (high strictness)...")
        result = self.run_with_timeout(verifier.invoke, 10, state)
        self.print_result("Verifier (high)", result)
    
    # =========================================================
    # TEST MEMORY NODE
    # =========================================================
    def test_memory(self):
        self.print_header("TESTING MEMORY NODE")
        
        # Create memory manager
        memory = MemoryManager(enable_compression=True)
        
        # Create state with many messages
        state = GameState(
            player_name="TestGoku",
            saga_name="Saiyan Saga",
            player_stats={"power_level": 1000, "ki_mastery": 30},
            tokens_used=60000  # Trigger compression
        )
        
        # Add many test messages
        print("\n📋 Adding 50 test messages...")
        for i in range(50):
            if i % 2 == 0:
                state.add_message(AIMessage(content=f"Scene {i}: Training continues... The power grows."))
            else:
                state.add_message(HumanMessage(content=f"Choice {i}: Train harder"))
        
        print(f"   Messages before: {len(state.messages)}")
        
        # Test should_compress
        print("\n📋 Testing should_compress...")
        result = self.run_with_timeout(memory.should_compress, 5, state)
        self.print_result("Memory.should_compress", result)
        
        # Test compress_memory
        if result["status"] == "success" and result["result"]:
            print("\n📋 Testing compress_memory...")
            result = self.run_with_timeout(memory.compress_memory, 10, state)
            self.print_result("Memory.compress", result)
            
            if result["status"] == "success":
                print(f"   Summary preview: {result['result'][:100]}...")
    
    # =========================================================
    # TEST REPLAN LOGIC
    # =========================================================
    def test_replan_logic(self):
        self.print_header("TESTING REPLAN LOGIC")
        
        # Create a graph instance to access routing functions
        graph = SagaGraph()
        
        # Test 1: Normal situation - no replan needed
        print("\n📋 Test 1: Normal - No replan needed")
        state = GameState()
        state.current_plan = [
            PlanStep(
                scene_type=SceneType.BATTLE,
                description="Battle with Vegeta",
                expected_outcome="Win or learn"
            )
        ]
        state.plan_step_index = 0
        state.plan_revisions = 1
        
        result = self.run_with_timeout(graph._route_from_replan_check, 5, state)
        self.print_result("Replan Check (normal)", result)
        
        # Test 2: Too many unexpected events
        print("\n📋 Test 2: Too many unexpected events")
        step = PlanStep(
            scene_type=SceneType.BATTLE,
            description="Battle with Vegeta",
            expected_outcome="Win or learn"
        )
        step.unexpected_events = ["Event1", "Event2", "Event3", "Event4"]
        state.current_plan = [step]
        state.plan_step_index = 0
        
        result = self.run_with_timeout(graph._route_from_replan_check, 5, state)
        self.print_result("Replan Check (unexpected events)", result)
        
        # Test 3: Too many revisions
        print("\n📋 Test 3: Too many revisions")
        state.plan_revisions = 10
        result = self.run_with_timeout(graph._route_from_replan_check, 5, state)
        self.print_result("Replan Check (many revisions)", result)
        
        # Test 4: Plan completed
        print("\n📋 Test 4: Plan completed")
        state.plan_step_index = 1
        if state.current_plan:
            state.current_plan[0].completed = True
        result = self.run_with_timeout(graph._route_from_replan_check, 5, state)
        self.print_result("Replan Check (completed)", result)
    
    def print_result(self, name, result):
        if result["status"] == "success":
            elapsed = result.get("elapsed", 0)
            print(f"   ✅ {name}: Success in {elapsed:.2f}s")
        elif result["status"] == "timeout":
            print(f"   ❌ {name}: TIMEOUT - {result['error']}")
        else:
            print(f"   ❌ {name}: ERROR - {result['error']}")
    
    def run_all(self):
        self.print_header("NODE DEBUGGER START")
        
        # Test each node
        self.test_verifier()
        self.test_memory()
        self.test_replan_logic()
        
        print("\n" + "="*60)
        print("🔍 DEBUGGING COMPLETE")
        print("="*60)

if __name__ == "__main__":
    debugger = NodeDebugger()
    debugger.run_all()